from ..db import db
from ..models.order import Order
from flask import Blueprint, request, Response, abort, make_response
from ..utilities import create_order, get_models_with_filters, validate_model, update_model

bp = Blueprint("orders_blueprint", __name__, url_prefix="/orders")


@bp.post("/")
def post_order():
    request_body = request.get_json()

    try:
        new_order = create_order(Order, request_body)
    except KeyError as e:
        abort(make_response({"message": f"Invalid: Missing key ({e.args[0]})"}, 400))

    return new_order.to_dict(), 201


@bp.get("/")
def get_all_orders():
    return get_models_with_filters(Order, request.args)


@bp.get("/<id>")
def get_single_order(id):
    try:
        order = validate_model(Order, id)
    except ValueError as e:
        abort(make_response({"message": str(e)}, 400))
    except LookupError as e:
        abort(make_response({"message": str(e)}, 404))

    return order.to_dict()


@bp.put("/<id>")
def update_order(id):
    try:
        order = validate_model(Order, id)
    except ValueError as e:
        abort(make_response({"message": str(e)}, 400))
    except LookupError as e:
        abort(make_response({"message": str(e)}, 404))

    update_model(order, request.get_json())

    return Response(status=204, mimetype="application/json")


@bp.delete("/<id>")
def delete_order(id):
    try:
        order = validate_model(Order, id)
    except ValueError as e:
        abort(make_response({"message": str(e)}, 400))
    except LookupError as e:
        abort(make_response({"message": str(e)}, 404))

    db.session.delete(order)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.get('/health')
def health():
    # return {
    #     "status": "healthy"
    # }
    return {'status': 'healthy', 'version': '1.0.1'}, 200
