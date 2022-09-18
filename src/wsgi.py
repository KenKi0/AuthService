from gevent import monkey

monkey.patch_all()

from gevent.pywsgi import WSGIServer  # noqa: E402

from core.config import settings  # noqa: E402
from main import create_app, main  # noqa: E402

server = WSGIServer(('0.0.0.0', settings.flask.PORT), main(create_app()))
server.serve_forever()
