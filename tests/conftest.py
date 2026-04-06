import os
import pytest
from app.db import db
from app import create_app
from dotenv import load_dotenv
from app.models.order import Order
from flask.signals import request_finished

load_dotenv()

load_dotenv()


@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ.get('SQLALCHEMY_TEST_DATABASE_URI')
    }

    app = create_app(test_config)

    @request_finished.connect_via(app)
    def expire_session(sender, response, **extra):
        db.session.remove()

    with app.app_context():
        db.create_all()
        yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def one_order(app):
    with app.app_context():
        order = Order(user_id=5)
        db.session.add(order)
        db.session.commit()
        return order.to_dict()


@pytest.fixture
def two_orders(app):
    with app.app_context():
        orders = [Order(user_id=1), Order(user_id=2)]
        db.session.add_all(orders)
        db.session.commit()
        return [o.to_dict() for o in orders]
