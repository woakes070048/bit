# coding=utf-8
from __future__ import absolute_import, unicode_literals
import enum
import six


class GoogleDrivePermissionType(enum.Enum):
    """
        Describe a permission type for Google Drive as described on
        `Drive docs <https://developers.google.com/drive/v3/reference/permissions>`_
    """

    USER = "user"
    """
        Permission for single user
    """

    GROUP = "group"
    """
        Permission for group defined in Google Drive
    """

    DOMAIN = "domain"
    """
        Permission for domain defined in Google Drive
    """

    ANYONE = "anyone"
    """
        Permission for anyone
    """


class GoogleDrivePermissionRole(enum.Enum):
    """
        Describe a permission role for Google Drive as described on
        `Drive docs <https://developers.google.com/drive/v3/reference/permissions>`_
    """

    OWNER = "owner"
    """
        File Owner
    """

    READER = "reader"
    """
        User can read a file
    """

    WRITER = "writer"
    """
        User can write a file
    """

    COMMENTER = "commenter"
    """
        User can comment a file
    """


class GoogleDriveFilePermission(object):
    """
        Describe a permission for Google Drive as described on
        `Drive docs <https://developers.google.com/drive/v3/reference/permissions>`_

        :param gdstorage.GoogleDrivePermissionRole g_role: Role associated to this permission
        :param gdstorage.GoogleDrivePermissionType g_type: Type associated to this permission
        :param str g_value: email address that qualifies the User associated to this permission

    """

    @property
    def role(self):
        """
            Role associated to this permission

            :return: Enumeration that states the role associated to this permission
            :rtype: gdstorage.GoogleDrivePermissionRole
        """
        return self._role

    @property
    def type(self):
        """
            Type associated to this permission

            :return: Enumeration that states the role associated to this permission
            :rtype: gdstorage.GoogleDrivePermissionType
        """
        return self._type

    @property
    def value(self):
        """
            Email that qualifies the user associated to this permission
            :return: Email as string
            :rtype: str
        """
        return self._value

    @property
    def raw(self):
        """
            Transform the :class:`.GoogleDriveFilePermission` instance into a string used to issue the command to
            Google Drive API

            :return: Dictionary that states a permission compliant with Google Drive API
            :rtype: dict
        """

        result = {
            "role": self.role.value,
            "type": self.type.value
        }

        if self.value is not None:
            result["value"] = self.value

        return result

    def __init__(self, g_role, g_type, g_value=None):
        """
            Instantiate this class
        """
        if not isinstance(g_role, GoogleDrivePermissionRole):
            raise ValueError("Role should be a GoogleDrivePermissionRole instance")
        if not isinstance(g_type, GoogleDrivePermissionType):
            raise ValueError("Permission should be a GoogleDrivePermissionType instance")
        if g_value is not None and not isinstance(g_value, six.string_types):
            raise ValueError("Value should be a String instance")

        self._role = g_role
        self._type = g_type
        self._value = g_value


_ANYONE_CAN_READ_PERMISSION_ = GoogleDriveFilePermission(
    GoogleDrivePermissionRole.READER,
    GoogleDrivePermissionType.ANYONE
)
