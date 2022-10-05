import datetime
from http import HTTPStatus

from flask_jwt_extended import decode_token
from werkzeug.wrappers import Request, Response

from core.config import settings


class RateLimitMiddleware:
    """
    Simple Rate limit middleware with Leaky bucket
    """

    def __init__(self, wsgi_app, app, storage):
        self.wsgi_app = wsgi_app
        self.app = app
        self.storage = storage

    def __call__(self, environ, start_response):
        request = Request(environ)
        token = request.headers.get('Authorization')
        if token is None:
            return self.wsgi_app(environ, start_response)
        with self.app.app_context():
            user_id = decode_token(token[7:]).get('identity')
        pipeline = self.storage.pipeline()
        now = datetime.datetime.utcnow()
        key = f'{user_id}:{now.minute}'
        pipeline.incr(key, 1)
        pipeline.expire(key, 59)
        request_number = pipeline.execute()[0]
        if request_number > settings.REQUEST_LIMIT_PER_MINUTE:
            res = Response('Too Many Requests', mimetype='text/plain', status=HTTPStatus.TOO_MANY_REQUESTS)
            return res(environ, start_response)
        return self.wsgi_app(environ, start_response)
