from .db import db, migrate
from flask import Flask

import os

def create_app():
  app = Flask(__name__)

  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

  db.init_app(app)
  migrate.init_app(app, db)

  @app.get('/')
  def index():
    return {
      "status": "ok"
    }

  return app