from .db import db
from .models.line_item import LineItem


def validate_model(cls, id):
    try:
        id = int(id)
    except ValueError:
        raise ValueError(f"{cls.__name__} id ({id}) is invalid.")

    query = db.select(cls).where(cls.id == id)
    model = db.session.scalar(query)

    if not model:
        raise LookupError(f"{cls.__name__} with id ({id}) not found.")

    return model


def create_order(cls, model_data):
    new_order = cls.from_dict(model_data)
    line_items = []

    for item in model_data.get("items", []):
        item["order_id"] = new_order.id
        line_item = LineItem.from_dict(item)
        line_items.append(line_item)

    new_order.items = line_items

    db.session.add(new_order)
    db.session.commit()

    return new_order


def get_models_with_filters(cls, filters=None):
    query = db.select(cls)

    if filters:
        for attribute, value in filters.items():
            if hasattr(cls, attribute):
                query = query.where(
                    getattr(cls, attribute).ilike(f"%{value}%"))

    models = db.session.scalars(query.order_by(cls.id))
    return [model.to_dict() for model in models]


def update_model(obj, data):
    for attr, value in data.items():
        if hasattr(obj, attr):
            setattr(obj, attr, value)

    db.session.commit()
