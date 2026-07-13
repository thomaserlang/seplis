import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seplis.api.model_base import Base
from seplis.api.person.models.person_model import MPerson


class MSeriesCast(Base):
    __tablename__ = 'series_cast'

    series_id: Mapped[int] = mapped_column(sa.ForeignKey('series.id'), primary_key=True)
    person_id: Mapped[int] = mapped_column(sa.ForeignKey('people.id'), primary_key=True)
    person: Mapped[MPerson] = relationship('MPerson', lazy=False)
    roles: Mapped[list | None] = mapped_column(sa.JSON, server_default='[]')
    order: Mapped[int | None] = mapped_column()
    total_episodes: Mapped[int | None] = mapped_column()
