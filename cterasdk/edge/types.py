from collections import namedtuple
from . import enum
from ..common import StringCriteriaBuilder, IntegerCriteriaBuilder, ListCriteriaBuilder, DateTimeCriteriaBuilder, Object
from ..exception import InputError


TCPService = namedtuple('TCPService', ('host', 'port'))
TCPService.__doc__ = 'Tuple holding the host and port to connect over TCP'
TCPService.host.__doc__ = 'The ip address, hostname or fully qualified domain name of the host'
TCPService.port.__doc__ = 'The port number'


TCPConnectResult = namedtuple('TCPConnectResult', ('host', 'port', 'is_open'))
TCPConnectResult.__doc__ = 'Tuple holding the host and port to connect over TCP'
TCPConnectResult.host.__doc__ = 'The ip address, hostname or fully qualified domain name of the host'
TCPConnectResult.port.__doc__ = 'The port number'
TCPConnectResult.is_open.__doc__ = 'Boolean, indicating whether a TCP connection can be successfully ' \
                                   'established to the target host over the specified port'


class UserGroupEntry():
    """
    User or Group Entry

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    """

    _valid_principal_types = list({k: v for k, v in enum.PrincipalType.__dict__.items() if not k.startswith('_')}.values())

    def __init__(self, principal_type, name):
        UserGroupEntry._validate_principal_type(principal_type)
        self._principal_type = principal_type
        self.name = name

    @property
    def principal_type(self):
        return self._principal_type

    @principal_type.setter
    def principal_type(self, principal_type):
        UserGroupEntry._validate_principal_type(principal_type)
        self._principal_type = principal_type

    def to_server_object(self):
        user_group_obj = Object()
        if self.principal_type == enum.PrincipalType.LU:
            user_group_obj._classname = enum.PrincipalType.LU  # pylint: disable=protected-access
            user_group_obj.ref = "#config#auth#users#" + self.name
        elif self.principal_type == enum.PrincipalType.LG:
            user_group_obj._classname = enum.PrincipalType.LG  # pylint: disable=protected-access
            user_group_obj.ref = "#config#auth#groups#" + self.name
        elif self.principal_type == enum.PrincipalType.DU:
            user_group_obj._classname = enum.PrincipalType.DU  # pylint: disable=protected-access
            user_group_obj.name = self.name
        elif self.principal_type == enum.PrincipalType.DG:
            user_group_obj._classname = enum.PrincipalType.DG  # pylint: disable=protected-access
            user_group_obj.name = self.name
        return user_group_obj

    @staticmethod
    def from_server_object(server_object):
        principal_type = server_object._classname  # pylint: disable=protected-access
        if principal_type in [enum.PrincipalType.LU, enum.PrincipalType.LG]:
            name = server_object.ref
            name = name[name.rfind('#') + 1:]
        else:
            name = server_object.name
        return UserGroupEntry(principal_type, name)

    @staticmethod
    def _validate_principal_type(principal_type):
        if principal_type not in UserGroupEntry._valid_principal_types:
            raise InputError('Invalid principal type', principal_type, UserGroupEntry._valid_principal_types)

    def __str__(self):
        return ('\\' + self.name) if self.principal_type in [enum.PrincipalType.LG, enum.PrincipalType.LU] else self.name


class AccessControlEntryValidator:

    _valid_permissions = list({k: v for k, v in enum.FileAccessMode.__dict__.items() if not k.startswith('_')}.values())

    @staticmethod
    def validate_permission(permission):
        if permission not in AccessControlEntryValidator._valid_permissions:
            raise InputError('Invalid permissions', permission, AccessControlEntryValidator._valid_permissions)


class NFSv3AccessControlEntry():
    """
    NFS v3 export access control entry
    :ivar str address: IP address, hostname or fully qualified domain name of client machine
    :ivar str netmask: Subnet mask
    :ivar cterasdk.edge.enum.FileAccessMode perm: File access permission
    """

    def __init__(self, address, netmask, perm):
        AccessControlEntryValidator.validate_permission(perm)
        self._address = address
        self._netmask = netmask
        self._perm = perm
        self._noRootSquash = False

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = address

    @property
    def netmask(self):
        return self._netmask

    @netmask.setter
    def netmask(self, netmask):
        self._netmask = netmask

    @property
    def perm(self):
        return self._perm

    @perm.setter
    def perm(self, perm):
        AccessControlEntryValidator.validate_permission(perm)
        self._perm = perm

    @staticmethod
    def from_server_object(server_object):
        return NFSv3AccessControlEntry(server_object.address, server_object.netmask, server_object.accessLevel)

    def to_server_object(self):
        param = Object()
        param.address = self._address
        param.netmask = self._netmask
        param.accessLevel = self._perm
        param.noRootSquash = self._noRootSquash
        return param

    def __str__(self):
        return str(dict(address=self.address, netmask=self.netmask, permission=self.perm))


class ShareAccessControlEntry():
    """
    Share access control entry for filer shares

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    :ivar cterasdk.edge.enum.FileAccessMode perm: The file access permission
    """

    _valid_permissions = list({k: v for k, v in enum.FileAccessMode.__dict__.items() if not k.startswith('_')}.values())

    def __init__(self, principal_type, name, perm):
        AccessControlEntryValidator.validate_permission(perm)
        self._user_group_entry = UserGroupEntry(principal_type, name)
        self._perm = perm

    @property
    def principal_type(self):
        return self._user_group_entry.principal_type

    @principal_type.setter
    def principal_type(self, principal_type):
        self._user_group_entry.principal_type = principal_type

    @property
    def name(self):
        return self._user_group_entry.name

    @name.setter
    def name(self, name):
        self._user_group_entry.name = name

    @property
    def perm(self):
        return self._perm

    @perm.setter
    def perm(self, perm):
        AccessControlEntryValidator.validate_permission(perm)
        self._perm = perm

    def to_server_object(self):
        ace = Object()
        ace._classname = "ShareACLRule"  # pylint: disable=protected-access
        ace.principal2 = self._user_group_entry.to_server_object()
        ace.permissions = self._create_permissions_object()
        return ace

    def _create_permissions_object(self):
        permissions = Object()
        permissions._classname = "FileAccessPermissions"  # pylint: disable=protected-access
        permissions.allowedFileAccess = self.perm
        return permissions

    @staticmethod
    def from_server_object(server_object):
        user_group_entry = UserGroupEntry.from_server_object(server_object.principal2)
        perm = server_object.permissions.allowedFileAccess
        return ShareAccessControlEntry(user_group_entry.principal_type, user_group_entry.name, perm)


class RemoveShareAccessControlEntry(UserGroupEntry):
    """
    Object holding share access control principal type and name

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    """


class FileExclusionBuilder:

    Type = 'File'

    @staticmethod
    def extensions():
        return ListCriteriaBuilder(FileExclusionBuilder.Type, enum.FileCriteria.Type)

    @staticmethod
    def names():
        return ListCriteriaBuilder(FileExclusionBuilder.Type, enum.FileCriteria.Name)

    @staticmethod
    def name():
        return StringCriteriaBuilder(FileExclusionBuilder.Type, enum.FileCriteria.Name)

    @staticmethod
    def paths():
        return ListCriteriaBuilder(FileExclusionBuilder.Type, enum.FileCriteria.Path)

    @staticmethod
    def path():
        return StringCriteriaBuilder(FileExclusionBuilder.Type, enum.FileCriteria.Path)

    @staticmethod
    def size():
        return IntegerCriteriaBuilder(FileExclusionBuilder.Type, enum.FileCriteria.Size)

    @staticmethod
    def last_modified():
        return DateTimeCriteriaBuilder(FileExclusionBuilder.Type, enum.FileCriteria.Modified)


class DirectoryEntryFactory:

    @staticmethod
    def root(included):
        return DirEntry('root', included=included)


class FileEntry(Object):

    def __init__(self, name, display_name=None, included=None):
        self.name = name
        self.displayName = display_name
        self.isIncluded = included


class DirEntry(FileEntry):

    def __init__(self, name, display_name=None, included=None, children=None):
        super().__init__(name, display_name, included)
        self.children = children


class BackupSet(Object):

    def __init__(self, name, directory_tree=None, filter_rules=None, defaults_dirs=None,
                 template_dirs=None, enabled=True, boolean_function=None, comment=None):
        self._classname = self.__class__.__name__  # pylint: disable=protected-access
        self.name = name
        self.isEnabled = enabled
        self.directoryTree = directory_tree if directory_tree else DirectoryEntryFactory.root(True)
        self.booleanFunction = boolean_function if boolean_function else enum.BooleanFunction.AND
        self.templateDirectories = template_dirs
        self.defaultDirs = defaults_dirs
        self.comment = comment
        self.filterRules = filter_rules


class FilterBackupSet(BackupSet):
    pass
