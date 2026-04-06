from ..db import db
from sqlalchemy.orm import Mapped, mapped_column


class Order(db.Model):

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int]

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
        }

    @classmethod
    def from_dict(cls, order_data):
        new_order = cls(
            user_id=order_data["user_id"]
        )

        return new_order
