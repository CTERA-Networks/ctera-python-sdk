from .base_command import BaseCommand



class Roles(BaseCommand):
    """
    Portal Roles APIs

    :ivar cterasdk.core.roles.ReadWriteAdmin rw: Object holding the Portal Read Write Administrator Role APIs
    :ivar cterasdk.core.roles.ReadOnlyAdmin rw: Object holding the Portal Read Only Administrator Role APIs
    :ivar cterasdk.core.roles.SupportAdmin rw: Object holding the Portal Support Administrator Role APIs
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.rw = ReadWriteAdmin(self._portal)
        self.ro = ReadOnlyAdmin(self._portal)
        self.support = SupportAdmin(self._portal)


class Role(BaseCommand):
    """
    Portal Role
    """

    def __init__(self, portal):
        super().__init__(portal)

    def get(self, role):
        return self._portal.get('/rolesSettings/%s' % role)

    def put(self, role, param):
        return self._portal.put('/rolesSettings/%s' % role, param)


class ReadWriteAdmin(Role):
    """
    Portal Read Write Administrator Role
    """

    path = 'readWriteAdminSettings'

    def get(self):
        return super().get(ReadWriteAdmin.path)

    def put(self, param):
        return super().put(ReadWriteAdmin.path, param)


class ReadOnlyAdmin(Role):
    """
    Portal Read Only Administrator Role
    """

    path = 'readOnlyAdminSettings'

    def get(self):
        return super().get(ReadOnlyAdmin.path)

    def put(self, param):
        return super().put(ReadOnlyAdmin.path, param)


class SupportAdmin(Role):
    """
    Portal Support Administrator Role
    """

    path = 'supportAdminSettings'

    def get(self):
        return super().get(SupportAdmin.path)

    def put(self, param):
        return super().put(SupportAdmin.path, param)
