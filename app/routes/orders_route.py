from ..db import db
from ..models.order import Order
from flask import Blueprint, request, Response
from .route_utilities import create_order, get_models_with_filters, validate_model, update_model

bp = Blueprint("orders_blueprint", __name__, url_prefix="/orders")


@bp.post("/")
def post_order():
    request_body = request.get_json()

    return create_order(Order, request_body)


@bp.get("/")
def get_all_orders():
    return get_models_with_filters(Order, request.args)


@bp.get("/<id>")
def get_single_order(id):
    order = validate_model(Order, id)

    return order.to_dict()


@bp.put("/<id>")
def update_order(id):
    order = validate_model(Order, id)
    request_body = request.get_json()

    return update_model(order, request_body)


@bp.delete("/<id>")
def delete_order(id):
    order = validate_model(Order, id)

    db.session.delete(order)
    db.session.commit()

    return Response(status=204, mimetype="application/json")
