import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seplis.api.model_base import Base
from seplis.api.person.models.person_model import MPerson


class MEpisodeCast(Base):
    __tablename__ = 'episode_cast'

    person_id: Mapped[int] = mapped_column(sa.ForeignKey('people.id'), primary_key=True)
    series_id: Mapped[int] = mapped_column(sa.ForeignKey('series.id'), primary_key=True)
    person: Mapped[MPerson] = relationship('MPerson', lazy=False)
    episode_number: Mapped[int] = mapped_column(primary_key=True)
    character: Mapped[str | None] = mapped_column(sa.String(200))
    order: Mapped[int | None] = mapped_column()
