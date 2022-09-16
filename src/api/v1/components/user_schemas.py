from marshmallow import Schema, fields


class Register(Schema):
    username = fields.Str(description='name', required=True, example='TestUser')
    email = fields.Str(description='email', required=True, example='test_2@test.com')
    password = fields.Str(description='password', required=True, example='Test_12345')


class Login(Schema):
    email = fields.Str(description='email', required=True, example='test_2@test.com')
    password = fields.Str(description='password', required=True, example='Test_12345')


class ChangePassword(Schema):
    old_password = fields.Str(description='old_password', required=True, example='Test_12345')
    new_password = fields.Str(description='new_password', required=True, example='Test_67890')


class Tokens(Schema):
    access_token = fields.Str(
        description='access_token',
        required=True,
        example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2MzEyNDIzMiwianRpIjoiM2UxOWQ2NmEtYTU4ZS00OGYzLWIyMTMtOTViYmZjYjgxOGY1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImEyOWIxMjhkLTM5YzctNGMxNS1iZGEyLTAyNzgzMzliNzMxMyIsIm5iZiI6MTY2MzEyNDIzMiwiZXhwIjoxNjYzMTI1NDMyLCJwZXJtaXNzaW9ucyI6W10sImlzX3N1cGVyIjpmYWxzZX0.Y0VDqXj8MtD2XlVJKG8nBS_HjQoJHL9oPcbjBvmZ2_k',  # noqa: E501
    )
    refresh_token = fields.Str(
        description='refresh_token',
        required=True,
        example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2MzEyNDIzMiwianRpIjoiYzI2MzBlZmQtMjU1Ni00NDdiLTk1OGItMzZlOTIxNjg3MjM1IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiJhMjliMTI4ZC0zOWM3LTRjMTUtYmRhMi0wMjc4MzM5YjczMTMiLCJuYmYiOjE2NjMxMjQyMzIsImV4cCI6MTY2Mzk4ODIzMiwicGVybWlzc2lvbnMiOltdLCJpc19zdXBlciI6ZmFsc2V9.5Wmo7M7klrxO4_c47JI2xWAWSGljCS9cvn3D0VWUXmo',  # noqa: E501
    )


class RefreshToken(Schema):
    tokens = fields.Nested(Tokens)


class Logout(Schema):
    from_all = fields.Boolean(description='Выход со всех устройств')
