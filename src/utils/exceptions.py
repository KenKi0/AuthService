class InvalidPassword(Exception):
    ...


class NoAccessError(Exception):
    ...


class EmailAlreadyExist(Exception):
    ...


class NotFoundError(Exception):
    ...


class RoleAlreadyExist(Exception):
    ...


class UniqueConstraintError(Exception):
    ...


class AttemptDeleteProtectedObjectError(Exception):
    ...
