from marshmallow import Schema, fields


class Permission(Schema):
    name = fields.Str(metadata={'description': 'name', 'required': True, 'example': 'Default user'})
    code = fields.Integer(metadata={'description': 'code', 'required': True, 'example': 0})
    description = fields.Str(
        metadata={'description': 'description', 'required': True, 'example': 'Может просматривать свой контент'},
    )
