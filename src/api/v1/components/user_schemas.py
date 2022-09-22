from marshmallow import Schema, fields


class Register(Schema):
    username = fields.Str(metadata={'description': 'name', 'required': True, 'example': 'TestUser'})
    email = fields.Str(metadata={'description': 'email', 'required': True, 'example': 'test_2@test.com'})
    password = fields.Str(metadata={'description': 'password', 'required': True, 'example': 'Test_12345'})


class Login(Schema):
    email = fields.Str(metadata={'description': 'email', 'required': True, 'example': 'test_2@test.com'})
    password = fields.Str(metadata={'description': 'password', 'required': True, 'example': 'Test_12345'})


class ChangePassword(Schema):
    old_password = fields.Str(metadata={'description': 'old_password', 'required': True, 'example': 'Test_12345'})
    new_password = fields.Str(metadata={'description': 'new_password', 'required': True, 'example': 'Test_67890'})


class Tokens(Schema):
    access_token = fields.Str(
        metadata={
            'description': 'access_token',
            'required': True,
            'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2MzEyN.....',
        },
    )
    refresh_token = fields.Str(
        metadata={
            'description': 'refresh_token',
            'required': True,
            'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2Mz......',
        },
    )


class RefreshToken(Schema):
    tokens = fields.Nested(Tokens)


class Logout(Schema):
    from_all = fields.Boolean(metadata={'description': 'Выход со всех устройств'})


class Session(Schema):
    device_id = fields.UUID(metadata={'description': 'Device', 'required': True})
    user_id = fields.UUID(metadata={'description': 'User', 'required': True})
    auth_date = fields.DateTime(metadata={'description': 'Login data', 'required': True})
