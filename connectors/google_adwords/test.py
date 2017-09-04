# coding=utf-8
#  system
import os
import json
import httplib2

# oauth
from oauth2client.service_account import ServiceAccountCredentials

# google api
from googleapiclient.discovery import build

# local
from storages.google.permissions import _ANYONE_CAN_READ_PERMISSION_
from storages.google.permissions import GoogleDriveFilePermission
from storages.google.permissions import GoogleDrivePermissionRole
from storages.google.permissions import GoogleDrivePermissionType


class GoogleDriveStorage(object):

    _UNKNOWN_MIMETYPE_ = "application/octet-stream"
    _GOOGLE_DRIVE_FOLDER_MIMETYPE_ = "application/vnd.google-apps.folder"

    cred_file_name = 'z-analytics-9254f090b6fe.json'

    credentials = ''

    def init(self):

        with open(self.cred_file_name, 'r') as f:
            self.credentials = f.read()
        f.closed
        # print('Initial')
        # print(self.credentials)

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

    def _open(self, name, mode='rb'):
        file_data = self._check_file_exists(name)
        response, content = self._drive_service._http.request(
            file_data['downloadUrl'])

        print(content)

        # return File(BytesIO(content), name)

    def open(self, name, mode='rb'):
        """
        Retrieves the specified file from storage.
        """
        return self._open(name, mode)

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
            # content = File(content, name)

        name = self.get_available_name(name, max_length=max_length)
        return self._save(name, content)


gds = GoogleDriveStorage()
# gds.open('config.json')
gds.open('2017-08-20/CAMPAIGN_PERFORMANCE_REPORT.zip')
