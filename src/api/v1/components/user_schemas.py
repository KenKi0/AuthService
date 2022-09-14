from typing import TypedDict

from pydantic import BaseModel


class Register(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        schema_extra = {
            'example': {
                'username': 'TestUser',
                'email': 'test_2@test.com',
                'password': 'Test_12345',
            },
        }


class Login(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            'example': {
                'email': 'test_2@test.com',
                'password': 'Test_12345',
            },
        }


class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    class Config:
        schema_extra = {
            'example': {
                'old_password': 'Test_12345',
                'new_password': 'Test_67890',
            },
        }


class Tokens(TypedDict):
    access_token: str
    refresh_token: str


class RefreshToken(BaseModel):
    tokens: Tokens

    class Config:
        schema_extra = {
            'example': {
                'tokens': {
                    'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2MzEyNDIzMiwianRpIjoiM2UxOWQ2NmEtYTU4ZS00OGYzLWIyMTMtOTViYmZjYjgxOGY1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImEyOWIxMjhkLTM5YzctNGMxNS1iZGEyLTAyNzgzMzliNzMxMyIsIm5iZiI6MTY2MzEyNDIzMiwiZXhwIjoxNjYzMTI1NDMyLCJwZXJtaXNzaW9ucyI6W10sImlzX3N1cGVyIjpmYWxzZX0.Y0VDqXj8MtD2XlVJKG8nBS_HjQoJHL9oPcbjBvmZ2_k',  # noqa: E501
                    'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2MzEyNDIzMiwianRpIjoiYzI2MzBlZmQtMjU1Ni00NDdiLTk1OGItMzZlOTIxNjg3MjM1IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiJhMjliMTI4ZC0zOWM3LTRjMTUtYmRhMi0wMjc4MzM5YjczMTMiLCJuYmYiOjE2NjMxMjQyMzIsImV4cCI6MTY2Mzk4ODIzMiwicGVybWlzc2lvbnMiOltdLCJpc19zdXBlciI6ZmFsc2V9.5Wmo7M7klrxO4_c47JI2xWAWSGljCS9cvn3D0VWUXmo',  # noqa: E501
                },
            },
        }
