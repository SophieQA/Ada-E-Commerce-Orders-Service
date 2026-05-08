from flask import Flask
from sqlalchemy.engine import URL
from .db import db, migrate
from flask_cors import CORS
from .models.order import Order
from .models.line_item import LineItem
from .routes.orders_route import bp as orders_bp

import os
import boto3
import json


def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB_HOST = os.environ.get('DATABASE_HOST')
    DB_PORT = int(os.environ.get('DATABASE_PORT', 5432))
    DB_NAME = os.environ.get('DATABASE_NAME')
    DB_USER = os.environ.get('DATABASE_USER')

    secrets_client = boto3.client('secretsmanager')
    secret = secrets_client.get_secret_value(SecretId=os.environ.get('DB_SECRET_ARN'))
    DB_PASSWORD = json.loads(secret['SecretString'])['password']

    connection_url = URL.create(
        drivername='postgresql+psycopg2',
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = connection_url

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
    
    @app.get('/health')
    def health():
        return {
            "status": "healthy"
        }

    return app
