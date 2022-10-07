import json
import string
import typing
from secrets import choice as secrets_choice

from flask import Response, redirect, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_security.utils import hash_password
from rauth import OAuth2Service

import user.layer_models as layer_models
import user.payload_models as payload_models
import user.repositories as repo
import utils.exceptions as exc
import utils.types as types
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)

db_repo = repo.get_user_db_repo()
tms_repo = repo.get_user_tms_repo()


class OAuthSubclassesProtocol(typing.Protocol):
    def authorize(self, handle_name: str) -> Response:
        """
        Редирекнуть на сайт провайдера для авторизации.

        :param handle_name: название ручки для обработки callback
        """
        ...

    def callback(self, code: str) -> layer_models.UserOAuth:
        """
        Обменять code а token и получить данные пользователя.

        :param code: code полученный от провайдера после авторазации пользователя
        :raises NoAccessError: если не указан code
        """
        ...

    def register(self, user: payload_models.OAuthUser) -> None:
        """
        Зарегестрировать нового пользователя.

        :raises EmailAlreadyExist: указанный email уже сущетсвует
        :raises UniqueConstraintError: если указанная социальная сеть уже привязана к другому пользователю
        """
        ...

    def login(self, user_payload: payload_models.OAuthUser) -> tuple[types.AccessToken, types.RefreshToken]:
        """
        Войти в аккаунт с помощью соц сети.

        :raises NotFoundError: если не получилось идентефицировать пользователя
        """
        ...


class OAuthService:
    providers: dict = None

    def __init__(
        self,
        provider_name: settings.oauth.providers,
        db_repository: repo.UserRepositoryProtocol = db_repo,
        tm_storage_repository: repo.UserTmStorageRepositoryProtocol = tms_repo,
    ):
        self.db_repo = db_repository
        self.tms_repo = tm_storage_repository
        self.provider_name = provider_name.value
        credentials = settings.oauth.CREDENTIALS.get(provider_name)
        self.consumer_id = credentials.get('id')
        self.consumer_secret = credentials.get('secret')
        self.authorize_url = credentials.get('authorize_url')
        self.access_token_url = credentials.get('access_token_url')
        self.base_url = credentials.get('base_url')

    def get_callback_url(self, handle_name: str):
        return url_for('auth.' + handle_name, provider=self.provider_name, _external=True)

    @classmethod
    def get_provider(cls, provider_name: str) -> OAuthSubclassesProtocol:
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]

    def login(self, user_payload: payload_models.OAuthUser) -> tuple[types.AccessToken, types.RefreshToken]:
        try:
            social_account = self.db_repo.get_social_account(user_payload.social_id, self.provider_name)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке получить social_account: \n %s', str(ex))
            raise
        try:
            user = self.db_repo.get_by_id(social_account.user_id)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке получить пользователя: \n %s', str(ex))
            raise
        device = payload_models.UserDevicePayload(user_id=user.id, user_agent=user_payload.user_agent)
        try:
            user_device = self.db_repo.get_allowed_device(device)
        except exc.NotFoundError:
            user_device = self.db_repo.add_allowed_device(device)
        self.db_repo.add_new_session(payload_models.SessionPayload(user_id=user.id, device_id=user_device.id))
        user_permissions = self.db_repo.get_user_permissions(user.id)
        additional_claims = {
            'permissions': [permission.code for permission in user_permissions],
            'is_super': user.is_super,
        }
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=settings.jwt.ACCESS_TOKEN_EXP,
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=settings.jwt.REFRESH_TOKEN_EXP,
        )
        self.tms_repo.set(
            user_payload.user_agent + str(user.id),
            refresh_token,
            ex=settings.jwt.REFRESH_TOKEN_EXP,
        )
        return access_token, refresh_token

    def register(self, user: payload_models.OAuthUser) -> None:
        password = self.generate_password()
        new_user = payload_models.UserCreatePayload(
            username=user.username,
            email=user.email,
            password=hash_password(password),
        )
        try:
            new_user = self.db_repo.create(new_user)
        except exc.UniqueConstraintError as ex:
            logger.info('Ошибка при попытке зарегестрировать нового пользователя: \n %s', str(ex))
            raise exc.EmailAlreadyExist from ex
        social_account = payload_models.SocialAccountPayload(
            user_id=new_user.id,
            social_id=user.social_id,
            social_name=self.provider_name,
        )
        try:
            self.db_repo.create_social_account(social_account)
        except exc.UniqueConstraintError as ex:
            logger.info('Ошибка при попытке создать новый social_account: \n %s', str(ex))
            raise

    @staticmethod
    def generate_password():
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets_choice(alphabet) for _ in range(16))


class YandexOAuth(OAuthSubclassesProtocol, OAuthService):
    def __init__(self):
        super(YandexOAuth, self).__init__(settings.oauth.providers.yandex)
        self.service = OAuth2Service(
            name=self.provider_name,
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url,
        )

    def authorize(self, handle_name: str) -> Response:
        return redirect(
            self.service.get_authorize_url(
                scope='login:info login:email',
                response_type='code',
                redirect_uri=self.get_callback_url(handle_name),
            ),
        )

    def callback(self, code: str) -> layer_models.UserOAuth:
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if code is None:
            raise exc.NoAccessError

        oauth_session = self.service.get_auth_session(
            data={'code': code, 'grant_type': 'authorization_code'},
            decoder=decode_json,
        )
        me = oauth_session.get('', params={'format': 'json'}).json()
        return layer_models.UserOAuth(username=me.get('login'), email=me.get('default_email'), social_id=me.get('id'))
