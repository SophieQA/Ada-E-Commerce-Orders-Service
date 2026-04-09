from flask import Flask
from .db import db, migrate
from .models.order import Order
from .models.line_item import LineItem
from .routes.orders_route import bp as orders_bp

import os


def create_app(config=None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'SQLALCHEMY_DATABASE_URI')

    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(orders_bp)

    @app.get('/')
    def index():
        return {
            "status": "ok"
        }

    return app
