from uuid import UUID

import click
from flask import Flask
from flask.cli import with_appcontext
from flask_security.utils import hash_password

from db.db import db
from models.permissions import Permission, RolePermission
from models.role import Role, RoleUser
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

        db.session.bulk_save_objects(Role(**role_data) for role_data in roles)
        db.session.bulk_save_objects(Permission(**permis_data) for permis_data in permissions)
        db.session.commit()
        # User
        role = Role.query.filter_by(name='User').first()
        perm = Permission.query.filter_by(code=0).first()
        role_permis = RolePermission(perm_id=perm.id, role_id=role.id)
        db.session.add(role_permis)
        db.session.commit()
        # Subscriber
        role = Role.query.filter_by(name='Subscriber').first()
        perm = Permission.query.filter_by(code=1).first()
        role_permis = RolePermission(perm_id=perm.id, role_id=role.id)
        db.session.add(role_permis)
        db.session.commit()
        # Moderator
        role = Role.query.filter_by(name='Moderator').first()
        perm = Permission.query.filter_by(code=3).first()
        role_permis = RolePermission(perm_id=perm.id, role_id=role.id)
        db.session.add(role_permis)
        db.session.commit()

    @with_appcontext
    @app.cli.command('test_data')
    def create_test_table():
        users = [
            # все пароли = Test_12345
            # admin
            {
                'id': UUID('f2e9e8f7-48f1-4d58-a012-d984170b88d8'),  # admin
                'username': 'admin_test',
                'email': 'admin_test@test.com',
                'password': '$2b$12$16kSsskBdY2GAkuYBS4UX.EDDim0KO8Dt3st.SPHr.gD2/LyD8nFy',
                'is_super': True,
            },
            # moderator
            {
                'id': UUID('91a3e189-87a8-44f4-965d-525fc6bd236b'),  # moderator
                'username': 'moderator_test',
                'email': 'moderator_test@test.com',
                'password': '$2b$12$Xz1MPyZFPnYAaRZJCgQgQuuxCO1Sl5Y.eQOjHxNtVEsFIvCwmTsqO',
            },
            # user
            {
                'id': UUID('e92f0742-ebbc-4f4f-be56-3511883dc898'),  # user
                'username': 'user_test',
                'email': 'user_test@test.com',
                'password': '$2b$12$IirWU6XQLUS2WufUs9w1KeS4iYlpinOEzx5iLAVn1pxQCtFzoYxVm',
            },
        ]
        roles = [
            {
                'id': UUID('dc4b923f-db37-4c9f-8c2c-73b11c038c03'),  # user
                'name': 'User',
                'description': 'new user',
                'protected': True,
            },
            {
                'id': UUID('a3cb43a4-3699-42af-92ca-1e74acbd3c81'),
                'name': 'Subscriber_test',
                'description': 'subscriber',
            },
            {
                'id': UUID('c207cb73-4200-4dc8-86a3-23a07250aa67'),  # moderator
                'name': 'Moderator_test',
                'description': 'moderator',
            },
        ]
        permissions = [
            {
                'id': UUID('c251f7a7-abe1-46e9-86f9-cb1afdef49fa'),  # user
                'name': 'Default_user_test',
                'code': 0,
                'description': 'Default user',
                'protected': True,
            },
            {
                'id': '48f91d51-e753-4231-9333-b51407fb8158',
                'name': 'Test',
                'code': 2,
                'description': '_test',
            },
            {
                'id': UUID('2fdb32ec-4008-441b-abf4-590d349e71d9'),  # moderator
                'name': 'Moderator_test',
                'code': 3,
                'description': 'Moderator',
            },
        ]

        # Users
        db.session.bulk_save_objects(User(**data) for data in users)
        db.session.commit()
        # Roles
        db.session.bulk_save_objects(Role(**data) for data in roles)
        db.session.commit()
        # Permissions
        db.session.bulk_save_objects(Permission(**data) for data in permissions)
        db.session.commit()

        # User_roles
        # User
        role = Role.query.filter_by(name='User').first()
        user = User.query.filter_by(username='user_test').first()
        user_role = RoleUser(user_id=user.id, role_id=role.id)
        db.session.add(user_role)
        # Moderator
        role = Role.query.filter_by(name='User').first()
        user = User.query.filter_by(username='moderator_test').first()
        user_role = RoleUser(user_id=user.id, role_id=role.id)
        db.session.add(user_role)

        role = Role.query.filter_by(name='Moderator_test').first()
        user = User.query.filter_by(username='moderator_test').first()
        user_role = RoleUser(user_id=user.id, role_id=role.id)
        db.session.add(user_role)
        # Admin
        role = Role.query.filter_by(name='User').first()
        user = User.query.filter_by(username='admin_test').first()
        user_role = RoleUser(user_id=user.id, role_id=role.id)
        db.session.add(user_role)

        # Role_permissions
        # User
        role = Role.query.filter_by(name='User').first()
        perm = Permission.query.filter_by(code=0).first()
        role_permis = RolePermission(perm_id=perm.id, role_id=role.id)
        db.session.add(role_permis)
        # Moderator
        role = Role.query.filter_by(name='Moderator_test').first()
        perm = Permission.query.filter_by(code=0).first()
        role_permis = RolePermission(perm_id=perm.id, role_id=role.id)
        db.session.add(role_permis)

        role = Role.query.filter_by(name='Moderator_test').first()
        perm = Permission.query.filter_by(code=3).first()
        role_permis = RolePermission(perm_id=perm.id, role_id=role.id)
        db.session.add(role_permis)
        db.session.commit()
