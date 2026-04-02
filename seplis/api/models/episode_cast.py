from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import schemas
from ..database import AsyncSession, auto_session
from .base import Base

if TYPE_CHECKING:
    from .person import MPerson


class MEpisodeCast(Base):
    __tablename__ = 'episode_cast'

    person_id: Mapped[int] = mapped_column(sa.ForeignKey('people.id'), primary_key=True)
    series_id: Mapped[int] = mapped_column(sa.ForeignKey('series.id'), primary_key=True)
    person: Mapped[MPerson] = relationship('MPerson', lazy=False)
    episode_number: Mapped[int] = mapped_column(primary_key=True)
    character: Mapped[str | None] = mapped_column(sa.String(200))
    order: Mapped[int | None] = mapped_column()

    @staticmethod
    @auto_session
    async def save(
        data: schemas.Episode_cast_person_create, session: AsyncSession
    ) -> None:
        data_ = data.model_dump(exclude_unset=True)
        await session.execute(
            sa.dialects.mysql.insert(MEpisodeCast)
            .values(data_)
            .on_duplicate_key_update(data_)
        )

    @staticmethod
    @auto_session
    async def delete(
        series_id: int, episode_number: int, person_id: int, session: AsyncSession
    ) -> None:
        await session.execute(
            sa.delete(MEpisodeCast).where(
                MEpisodeCast.series_id == series_id,
                MEpisodeCast.episode_number == episode_number,
                MEpisodeCast.person_id == person_id,
            )
        )
