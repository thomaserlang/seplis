import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.model_base import Base


class MGenre(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(sa.String(100))
    type: Mapped[str | None] = mapped_column(sa.String(30))
    number_of: Mapped[int | None] = mapped_column(server_default='0')
