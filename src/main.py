from flask import Flask

from db.db import init_db

app = Flask(__name__)
# TODO в app.config передать settings


def main():
    init_db(app)
    with app.app_context():
        # TODO создание таблиц
        pass
