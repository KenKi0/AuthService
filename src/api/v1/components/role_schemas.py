from pydantic import BaseModel


class Role(BaseModel):
    name: str
    description: str

    class Config:
        schema_extra = {
            'example': {
                'name': 'test_role',
                'description': 'Test',
            },
        }
