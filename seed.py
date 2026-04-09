from app.db import db
from app import create_app
from dotenv import load_dotenv
from app.models.order import Order
from app.models.line_item import LineItem

load_dotenv()

app = create_app()


def seed_orders():
    orders = [
        Order(user_id=1),
        Order(user_id=2),
        Order(user_id=3),
    ]

    db.session.add_all(orders)
    db.session.flush()

    items = [
        LineItem(
            order_id=orders[0].id,
            product_id="S001",
            product_name="Pastel Gel Pen Set",
            product_price=8.99,
            quantity=2,
        ),
        LineItem(
            order_id=orders[0].id,
            product_id="S002",
            product_name="Floral Washi Tape Bundle",
            product_price=12.49,
            quantity=3,
        ),
        LineItem(
            order_id=orders[1].id,
            product_id="S003",
            product_name="Kawaii Memo Pad",
            product_price=5.99,
            quantity=4,
        ),
        LineItem(
            order_id=orders[1].id,
            product_id="S004",
            product_name="Mushroom Sticky Notes",
            product_price=4.49,
            quantity=2,
        ),
        LineItem(
            order_id=orders[2].id,
            product_id="S005",
            product_name="Holographic Sticker Sheet",
            product_price=3.99,
            quantity=5,
        ),
        LineItem(
            order_id=orders[2].id,
            product_id="S001",
            product_name="Pastel Gel Pen Set",
            product_price=8.99,
            quantity=1,
        ),
    ]

    db.session.add_all(items)
    db.session.commit()
    print("Seeded orders and order items!")


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_orders()
