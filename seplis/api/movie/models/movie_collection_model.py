import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.model_base import Base


class MMovieCollection(Base):
    __tablename__ = 'movie_collections'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(sa.String(200))
