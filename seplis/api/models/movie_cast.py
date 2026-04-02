from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import schemas
from ..database import AsyncSession, auto_session
from .base import Base

if TYPE_CHECKING:
    from .person import MPerson


class MMovieCast(Base):
    __tablename__ = 'movie_cast'

    movie_id: Mapped[int] = mapped_column(sa.ForeignKey('movies.id'), primary_key=True)
    person_id: Mapped[int] = mapped_column(sa.ForeignKey('people.id'), primary_key=True)
    person: Mapped[MPerson] = relationship('MPerson', lazy=False)
    character: Mapped[str | None] = mapped_column(sa.String(200))
    order: Mapped[int | None] = mapped_column()

    @staticmethod
    @auto_session
    async def save(data: schemas.Movie_cast_person_create, session: AsyncSession) -> None:
        data_ = data.model_dump(exclude_unset=True)
        await session.execute(
            sa.dialects.mysql.insert(MMovieCast)
            .values(data_)
            .on_duplicate_key_update(data_)
        )

    @staticmethod
    @auto_session
    async def delete(movie_id: int, person_id: int, session: AsyncSession) -> None:
        await session.execute(
            sa.delete(MMovieCast).where(
                MMovieCast.movie_id == movie_id,
                MMovieCast.person_id == person_id,
            )
        )
