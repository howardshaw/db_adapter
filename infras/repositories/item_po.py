from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from .base_po import BasePO


class ItemPO(BasePO):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        comment='Item name'
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment='Item description',
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Item quantity',
    )
    price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment='item price',
    )
