from datetime import date, datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seplis.api.image.models.image_model import MImage
from seplis.api.model_base import Base


class MPerson(Base):
    __tablename__ = 'people'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(sa.DateTime)
    name: Mapped[str] = mapped_column(sa.String(500))
    also_known_as: Mapped[list | None] = mapped_column(sa.JSON)
    gender: Mapped[int | None] = mapped_column(sa.SMALLINT)
    birthday: Mapped[date | None] = mapped_column(sa.Date)
    deathday: Mapped[date | None] = mapped_column(sa.Date)
    biography: Mapped[str | None] = mapped_column(sa.String(2000))
    place_of_birth: Mapped[str | None] = mapped_column(sa.String(100))
    popularity: Mapped[Decimal | None] = mapped_column(sa.DECIMAL(precision=12, scale=4))
    externals: Mapped[dict | None] = mapped_column(sa.JSON)
    profile_image_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey('images.id', onupdate='cascade', ondelete='set null')
    )
    profile_image: Mapped[MImage | None] = relationship('MImage', lazy=False)


class MPersonExternal(Base):
    __tablename__ = 'person_externals'

    person_id: Mapped[int] = mapped_column(
        sa.ForeignKey('people.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
        autoincrement=False,
    )
    title: Mapped[str] = mapped_column(sa.String(45), primary_key=True)
    value: Mapped[str | None] = mapped_column(sa.String(45))
