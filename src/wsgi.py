from gevent import monkey

monkey.patch_all()

from gevent.pywsgi import WSGIServer  # noqa: E402

from core.config import settings  # noqa: E402
from main import app, main  # noqa: E402

app_port = settings.flask.PORT
server = WSGIServer(('0.0.0.0', app_port), main(app))
server.serve_forever()
