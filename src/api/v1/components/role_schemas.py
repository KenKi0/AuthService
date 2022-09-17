from marshmallow import Schema, fields


class Role(Schema):
    name = fields.Str(description='name', required=True, example='test_role')
    description = fields.Str(description='description', required=True, example='Test')
