from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seplis.api.database import AsyncSession, auto_session

from .. import schemas
from .base import Base

if TYPE_CHECKING:
    from .person import MPerson


class MSeriesCast(Base):
    __tablename__ = 'series_cast'

    series_id: Mapped[int] = mapped_column(sa.ForeignKey('series.id'), primary_key=True)
    person_id: Mapped[int] = mapped_column(sa.ForeignKey('people.id'), primary_key=True)
    person: Mapped[MPerson] = relationship('MPerson', lazy=False)
    roles: Mapped[list | None] = mapped_column(sa.JSON, server_default='[]')
    order: Mapped[int | None] = mapped_column()
    total_episodes: Mapped[int | None] = mapped_column()

    @staticmethod
    @auto_session
    async def save(
        data: schemas.Series_cast_person_create, session: AsyncSession
    ) -> None:
        data_ = data.model_dump(exclude_unset=True)
        await session.execute(
            sa.dialects.mysql.insert(MSeriesCast)
            .values(data_)
            .on_duplicate_key_update(data_)
        )

    @staticmethod
    @auto_session
    async def delete(series_id: int, person_id: int, session: AsyncSession) -> None:
        await session.execute(
            sa.delete(MSeriesCast).where(
                MSeriesCast.series_id == series_id,
                MSeriesCast.person_id == person_id,
            )
        )
