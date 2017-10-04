# system
import os
import json
import mimetypes
import httplib2
from dateutil.parser import parse
from io import BytesIO

# oauth
from oauth2client.service_account import ServiceAccountCredentials

# google
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# flask_appbuilder
from flask_appbuilder import Model

# superset
from superset import app

# local
from .. storages.google.permissions import _ANYONE_CAN_READ_PERMISSION_
from .. storages.google.permissions import GoogleDriveFilePermission
from .. storages.google.permissions import GoogleDrivePermissionRole
from .. storages.google.permissions import GoogleDrivePermissionType

from  . connector import AdWordsConnector

DB_PREFIX = '{}'.format(
    app.config.get('APP_DB_PREFIX', 'bit'),
)

class GoogleDriveStorage(Model):
    """
    Storage class for Django?? that interacts with Google Drive as persistent storage.
    This class uses a system account for Google API that create an application drive
    (the drive is not owned by any Google User, but it is owned by the application declared on
    Google API console).
    """

    __tablename__ = '{}_adwords_google_drive_storage'.format(DB_PREFIX)  # sql table name

    id = Column(Integer, primary_key=True)

    connector_id = Column(Integer, ForeignKey('{}_connectors.id'.format(DB_PREFIX)))
    connector = relationship('AdWordsConnector', back_populates='storage')

    credentials = Column(Text)


    _UNKNOWN_MIMETYPE_ = "application/octet-stream"
    _GOOGLE_DRIVE_FOLDER_MIMETYPE_ = "application/vnd.google-apps.folder"
    cred_file_name = 'z-analytics-9254f090b6fe.json'


    def init(self):

        # with open(self.cred_file_name, 'r') as f:
        #     self.credentials = f.read()
        # f.closed

        if self.credentials is not None and len(self.credentials):
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                json.loads(self.credentials),
                scopes=[
                    "https://www.googleapis.com/auth/drive",
                    # 'https://www.googleapis.com/auth/drive.metadata.readonly'
                ]
            )

            permissions = (
                GoogleDriveFilePermission(
                    GoogleDrivePermissionRole.READER,
                    GoogleDrivePermissionType.USER,
                    # "drive-993@project-id-8281928869006252347.iam.gserviceaccount.com"
                ),
            )

            http = httplib2.Http()
            http = credentials.authorize(http)

            self._permissions = None
            if permissions is None:
                self._permissions = (_ANYONE_CAN_READ_PERMISSION_,)
            else:
                if not isinstance(permissions, (tuple, list,)):
                    raise ValueError(
                        "Permissions should be a list or a tuple of GoogleDriveFilePermission instances")
                else:
                    for p in permissions:
                        if not isinstance(p, GoogleDriveFilePermission):
                            raise ValueError(
                                "Permissions should be a list or a tuple of GoogleDriveFilePermission instances")
                    # Ok, permissions are good
                    self._permissions = permissions

            self._drive_service = build('drive', 'v2', http=http)

    def __init__(self, *args, **kwargs):
        super(GoogleDriveStorage, self).__init__(*args, **kwargs)
        self.init()


    def _split_path(self, p):
        """
        Split a complete path in a list of strings

        :param p: Path to be splitted
        :type p: string
        :returns: list - List of strings that composes the path
        """
        p = p[1:] if p[0] == '/' else p
        a, b = os.path.split(p)
        return (self._split_path(a) if len(a) and len(b) else []) + [b]

    def _get_or_create_folder(self, path, parent_id=None):
        """
        Create a folder on Google Drive.
        It creates folders recursively.
        If the folder already exists, it retrieves only the unique identifier.

        :param path: Path that had to be created
        :type path: string
        :param parent_id: Unique identifier for its parent (folder)
        :type parent_id: string
        :returns: dict
        """
        folder_data = self._check_file_exists(path, parent_id)
        if folder_data is None:
            # Folder does not exists, have to create
            split_path = self._split_path(path)
            current_folder_data = None
            for p in split_path:
                meta_data = {
                    'title': p,
                    'mimeType': self._GOOGLE_DRIVE_FOLDER_MIMETYPE_
                }
                if current_folder_data is not None:
                    meta_data['parents'] = [{'id': current_folder_data['id']}]
                else:
                    # This is the first iteration loop so we have to set the parent_id
                    # obtained by the user, if available
                    if parent_id is not None:
                        meta_data['parents'] = [{'id': parent_id}]
                current_folder_data = self._drive_service.files().insert(body=meta_data).execute()
            return current_folder_data
        else:
            return folder_data

    def _check_file_exists(self, filename, parent_id=None):
        """
        Check if a file with specific parameters exists in Google Drive.

        :param filename: File or folder to search
        :type filename: string
        :param parent_id: Unique identifier for its parent (folder)
        :type parent_id: string
        :param mime_type: Mime Type for the file to search
        :type mime_type: string
        :returns: dict containing file / folder data if exists or None if does not exists
        """
        split_filename = self._split_path(filename)
        if len(split_filename) > 1:
            # This is an absolute path with folder inside
            # First check if the first element exists as a folder
            # If so call the method recursively with next portion of path
            # Otherwise the path does not exists hence the file does not exists
            q = "mimeType = '{0}' and title = '{1}'".format(self._GOOGLE_DRIVE_FOLDER_MIMETYPE_,
                                                            split_filename[0])
            if parent_id is not None:
                q = "{0} and '{1}' in parents".format(q, parent_id)
            max_results = 1  # Max value admitted from google drive
            folders = self._drive_service.files().list(q=q, maxResults=max_results).execute()
            for folder in folders["items"]:
                if folder["title"] == split_filename[0]:
                    # Assuming every folder has a single parent
                    return self._check_file_exists(os.path.sep.join(split_filename[1:]), folder["id"])
            return None
        else:
            # This is a file, checking if exists
            q = "title = '{0}'".format(split_filename[0])
            if parent_id is not None:
                q = "{0} and '{1}' in parents".format(q, parent_id)
            max_results = 1000  # Max value admitted from google drive
            file_list = self._drive_service.files().list(q=q, maxResults=max_results).execute()
            if len(file_list["items"]) == 0:
                q = "" if parent_id is None else "'{0}' in parents".format(parent_id)
                file_list = self._drive_service.files().list(q=q, maxResults=max_results).execute()
                for element in file_list["items"]:
                    if split_filename[0] in element["title"]:
                        return element
                return None
            else:
                return file_list["items"][0]

    # Methods that had to be implemented
    # to create a valid storage for Django

    def open(self, name, mode='rb'):
        return self._open(name, mode)

    def _open(self, name, mode='rb'):
        file_data = self._check_file_exists(name)
        response, content = self._drive_service._http.request(
            file_data['downloadUrl'])

        return BytesIO(content)
        # return File(BytesIO(content), name)

    def save(self, name, content, max_length=None):
        """
        Saves new content to the file specified by name. The content should be
        a proper File object or any python file-like object, ready to be read
        from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        # if not hasattr(content, 'chunks'):
        #     content = File(content, name)

        name = self.get_available_name(name, max_length=max_length)
        return self._save(name, content)

    def _save(self, name, content):
        folder_path = os.path.sep.join(self._split_path(name)[:-1])
        folder_data = self._get_or_create_folder(folder_path)
        parent_id = None if folder_data is None else folder_data['id']
        # Now we had created (or obtained) folder on GDrive
        # Upload the file
        fd = BytesIO(content.file.read())
        mime_type = mimetypes.guess_type(name)
        if mime_type[0] is None:
            mime_type = self._UNKNOWN_MIMETYPE_
        media_body = MediaIoBaseUpload(fd, mime_type, resumable=True)
        body = {
            'title': name,
            'mimeType': mime_type
        }
        # Set the parent folder.
        if parent_id:
            body['parents'] = [{'id': parent_id}]
        file_data = self._drive_service.files().insert(
            body=body,
            media_body=media_body).execute()

        # Setting up permissions
        for p in self._permissions:
            self._drive_service.permissions().insert(fileId=file_data["id"], body=p.raw).execute()

        return file_data.get(u'originalFilename', file_data.get(u'title'))

    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        file_data = self._check_file_exists(name)
        if file_data is not None:
            self._drive_service.files().delete(fileId=file_data['id']).execute()

    def exists(self, name):
        """
        Returns True if a file referenced by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        return self._check_file_exists(name) is not None

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        directories, files = [], []
        if path == "/":
            folder_id = {"id": "root"}
        else:
            folder_id = self._check_file_exists(path)
        if folder_id:
            file_params = {
                'q': "'{0}' in parents and mimeType != '{1}'".format(folder_id["id"],
                                                                     self._GOOGLE_DRIVE_FOLDER_MIMETYPE_),
                'maxResults': 1000,

            }
            dir_params = {
                'q': "'{0}' in parents and mimeType = '{1}'".format(folder_id["id"],
                                                                    self._GOOGLE_DRIVE_FOLDER_MIMETYPE_),
                'maxResults': 1000,
            }

            def list_files(service, params):
                elements = list()
                request = service.list(**params)
                while True:
                    response = request.execute()
                    for e in response["items"]:
                        elements.append(
                            os.path.join(path, e["title"])
                        )

                    if response.get('nextPageToken', None) is None:
                        break

                    request = service.list_next(
                        previous_request=request,
                        previous_response=response
                    )

                return elements

            directories = list_files(self._drive_service.files(), dir_params)
            files = list_files(self._drive_service.files(), file_params)

        return directories, files

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return 0
        else:
            return file_data["fileSize"]

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        else:
            return file_data["alternateLink"]

    def accessed_time(self, name):
        """
        Returns the last accessed time (as datetime object) of the file
        specified by name.
        """
        return self.modified_time(name)

    def created_time(self, name):
        """
        Returns the creation time (as datetime object) of the file
        specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        else:
            return parse(file_data['createdDate'])

    def modified_time(self, name):
        """
        Returns the last modified time (as datetime object) of the file
        specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        else:
            return parse(file_data["modifiedDate"])

    # def deconstruct(self):
    #     """
    #         Handle field serialization to support migration
    #
    #     """
    #     name, path, args, kwargs = \
    #         super(GoogleDriveStorage, self).deconstruct()
    #     if self._service_email is not None:
    #         kwargs["service_email"] = self._service_email
    #     if self._json_keyfile_path is not None:
    #         kwargs["json_keyfile_path"] = self._json_keyfile_path
