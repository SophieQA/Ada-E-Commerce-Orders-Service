from ..db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class LineItem(db.Model):
    __tablename__ = "line_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    product_id: Mapped[str]
    product_name: Mapped[str]
    product_price: Mapped[float]
    quantity: Mapped[int]

    order = db.relationship("Order", back_populates="items")

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_price": self.product_price,
            "quantity": self.quantity
        }

    @classmethod
    def from_dict(cls, item_data):
        new_order_item = cls(
            product_id=item_data["product_id"],
            product_name=item_data["product_name"],
            product_price=item_data["product_price"],
            quantity=item_data["quantity"],
            order_id=item_data["order_id"]
        )

        return new_order_item
