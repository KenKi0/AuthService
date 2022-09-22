from marshmallow import Schema, fields


class Role(Schema):
    name = fields.Str(metadata={'description': 'name', 'required': True, 'example': 'test_role'})
    description = fields.Str(metadata={'description': 'description', 'required': True, 'example': 'Test'})
