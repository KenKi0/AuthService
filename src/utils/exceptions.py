class InvalidPassword(Exception):
    ...


class NoAccessError(Exception):
    ...


class EmailAlreadyExist(Exception):
    ...


class NotFoundError(Exception):
    ...


class UniqueConstraintError(Exception):
    ...


INTEGRITY_UNIQUE_CONSTRAINT_MSG = 'already exist'
INTEGRITY_KEY_DIDNT_EXIST_MSG = 'not present in table'
