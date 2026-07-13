import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seplis.api.model_base import Base
from seplis.api.person.models.person_model import MPerson


class MMovieCast(Base):
    __tablename__ = 'movie_cast'

    movie_id: Mapped[int] = mapped_column(sa.ForeignKey('movies.id'), primary_key=True)
    person_id: Mapped[int] = mapped_column(sa.ForeignKey('people.id'), primary_key=True)
    person: Mapped[MPerson] = relationship('MPerson', lazy=False)
    character: Mapped[str | None] = mapped_column(sa.String(200))
    order: Mapped[int | None] = mapped_column()
