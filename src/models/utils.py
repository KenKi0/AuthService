import uuid
from db.db import db


def generate_uuid():
    return str(uuid.uuid4())


class BaseModel(db.Model):
    __table_args__ = {'schema': 'auth'}
    id = db.Column(db.String, primary_key=True, default=generate_uuid, unique=True, nullable=False)

    def set(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        # TODO определить какой будет Exception, обработать его
        except Exception as ex:
            raise ex
