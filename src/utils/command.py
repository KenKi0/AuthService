import click
from flask import Flask
from flask.cli import with_appcontext
from flask_security.utils import hash_password

from db.db import db
from models.permissions import Permission as _Permission
from models.permissions import RolePermission as _RolePermission
from models.role import Role as _Role
from models.user import User


def init_cli(app: Flask):
    @with_appcontext
    @app.cli.command('create_sudo')
    @click.argument('name')
    @click.argument('mail')
    @click.argument('password')
    def create_sudo(name: str, mail: str, password: str):
        _admin = {
            'username': name,
            'password': hash_password(password),
            'email': mail,
            'is_super': True,
        }
        admin = User.query.filter_by(email=_admin['email']).first()
        if admin:
            return
        admin = User(**_admin)
        db.session.add(admin)
        db.session.commit()

    @with_appcontext
    @app.cli.command('create_tables')
    def create_table():
        roles = [
            {
                'name': 'User',
                'description': 'new user',
                'protected': True,
            },
            {'name': 'Subscriber', 'description': 'subscriber'},
            {'name': 'Moderator', 'description': 'moderator'},
        ]
        permissions = [
            {
                'name': 'Default user',
                'code': 0,
                'description': 'Может просматривать свой контент',
                'protected': True,
            },
            {
                'name': 'Subscriber',
                'code': 1,
                'description': 'Может смотреть бесплатный контент',
            },
            {
                'name': 'Vip subscriber',
                'code': 2,
                'description': 'Может смотреть платный контент',
            },
            {
                'name': 'Moderator',
                'code': 3,
                'description': 'Может работать с role',
            },
        ]

        db.session.bulk_save_objects(_Role(**role_data) for role_data in roles)
        db.session.bulk_save_objects(_Permission(**permis_data) for permis_data in permissions)
        db.session.commit()
        # User
        role = _Role.query.filter_by(name='User').first()
        perm = _Permission.query.filter_by(code=0).first()
        role_permis = _RolePermission(perm_id=perm.id, role_id=role.id)
        db.session.add(role_permis)
        db.session.commit()
        # Subscriber
        role = _Role.query.filter_by(name='Subscriber').first()
        perm = _Permission.query.filter_by(code=1).first()
        role_permis = _RolePermission(perm_id=perm.id, role_id=role.id)
        db.session.add(role_permis)
        db.session.commit()
        # Moderator
        role = _Role.query.filter_by(name='Moderator').first()
        perm = _Permission.query.filter_by(code=3).first()
        role_permis = _RolePermission(perm_id=perm.id, role_id=role.id)
        db.session.add(role_permis)
        db.session.commit()
