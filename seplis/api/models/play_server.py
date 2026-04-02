from datetime import UTC, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from seplis import utils
from seplis.utils.sqlalchemy import UtcDateTime

from .. import exceptions, schemas
from ..database import AsyncSession, auto_session, database
from .base import Base
from .movie import MMovie
from .series import MSeries


class MPlayServer(Base):
    __tablename__ = 'play_servers'

    id: Mapped[str] = mapped_column(utils.sqlalchemy.UUID, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    updated_at: Mapped[datetime | None] = mapped_column(UtcDateTime)
    user_id: Mapped[int | None] = mapped_column()
    name: Mapped[str] = mapped_column(sa.String(45))
    url: Mapped[str | None] = mapped_column(sa.String(200))
    secret: Mapped[str | None] = mapped_column(sa.String(200))

    @staticmethod
    async def save(
        data: schemas.Play_server_create | schemas.Play_server_update,
        user_id: int,
        play_server_id: int | None = None,
    ) -> schemas.Play_server_with_url:
        _data = data.model_dump(exclude_unset=True)
        async with database.session() as session:
            async with session.begin():
                if not play_server_id:
                    play_server_id = str(uuid7())
                    await session.execute(
                        sa.insert(MPlayServer).values(
                            id=play_server_id,
                            created_at=datetime.now(tz=UTC),
                            user_id=user_id,
                            **_data,
                        )
                    )
                    await session.execute(
                        sa.insert(MPlayServerAccess).values(
                            play_server_id=play_server_id,
                            user_id=user_id,
                            created_at=datetime.now(tz=UTC),
                        )
                    )
                else:
                    await session.execute(
                        sa.update(MPlayServer)
                        .where(MPlayServer.id == play_server_id)
                        .values(updated_at=datetime.now(tz=UTC), **_data)
                    )
                play_server = await session.scalar(
                    sa.select(MPlayServer).where(MPlayServer.id == play_server_id)
                )
                await session.commit()
                return schemas.Play_server_with_url.model_validate(play_server)

    @staticmethod
    async def delete(id_: str, user_id: int | str) -> None:
        async with database.session() as session:
            async with session.begin():
                p = await session.scalar(
                    sa.select(MPlayServer.id).where(
                        MPlayServer.user_id == user_id,
                        MPlayServer.id == id_,
                    )
                )
                if not p:
                    raise exceptions.Not_found('Unknown play server')
                await session.execute(
                    sa.delete(MPlayServerAccess).where(
                        MPlayServerAccess.play_server_id == id_,
                    )
                )
                await session.execute(
                    sa.delete(MPlayServer).where(
                        MPlayServer.id == id_,
                    )
                )
                await session.commit()


class MPlayServerAccess(Base):
    """Users with access to the play server"""

    __tablename__ = 'play_server_access'

    play_server_id: Mapped[str] = mapped_column(utils.sqlalchemy.UUID, primary_key=True)
    user_id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(UtcDateTime)

    @staticmethod
    async def remove_user(
        play_server_id: str, owner_user_id: int | str, user_id: int | str
    ) -> bool:
        async with database.session() as session:
            p = session.scalar(
                sa.select(MPlayServer.id).where(
                    MPlayServer.id == play_server_id,
                    MPlayServer.user_id == owner_user_id,
                    MPlayServerAccess.play_server_id == MPlayServer.id,
                    MPlayServerAccess.user_id == user_id,
                )
            )
            if not p:
                raise exceptions.Play_server_access_user_no_access()
            await session.execute(
                sa.delete(MPlayServerAccess).where(
                    MPlayServerAccess.play_server_id == play_server_id,
                    MPlayServerAccess.user_id == user_id,
                )
            )
            await session.commit()
            return True


class MPlayServerInvite(Base):
    __tablename__ = 'play_server_invites'

    play_server_id: Mapped[str] = mapped_column(
        utils.sqlalchemy.UUID,
        sa.ForeignKey('play_servers.id', ondelete='cascade', onupdate='cascade'),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'),
        primary_key=True,
    )
    invite_id: Mapped[str] = mapped_column(utils.sqlalchemy.UUID)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    expires_at: Mapped[datetime] = mapped_column(UtcDateTime)

    @staticmethod
    async def invite(
        play_server_id: str, owner_user_id: str, data: schemas.Play_server_invite_create
    ) -> schemas.Play_server_invite_id:
        async with database.session() as session:
            p = await session.scalar(
                sa.select(MPlayServer.id).where(
                    MPlayServer.id == play_server_id,
                    MPlayServer.user_id == owner_user_id,
                )
            )
            if not p:
                raise exceptions.Play_server_unknown()

            p = await session.scalar(
                sa.select(MPlayServerAccess.user_id).where(
                    MPlayServerAccess.play_server_id == play_server_id,
                    MPlayServerAccess.user_id == data.user_id,
                )
            )
            if p:
                raise exceptions.Play_server_invite_already_has_access()

            invite_id = str(uuid7())
            ins = sa.dialects.mysql.insert(MPlayServerInvite).values(
                play_server_id=play_server_id,
                invite_id=invite_id,
                created_at=datetime.now(tz=UTC),
                expires_at=datetime.now(tz=UTC) + timedelta(hours=24),
                **data.model_dump(exclude_unset=True),
            )
            ins = ins.on_duplicate_key_update(
                invite_id=ins.inserted.invite_id,
                created_at=ins.inserted.created_at,
                expires_at=ins.inserted.expires_at,
            )
            await session.execute(ins)
            await session.commit()
            return schemas.Play_server_invite_id(invite_id=invite_id)

    @staticmethod
    async def accept_invite(user_id: str, invite_id: str) -> bool:
        async with database.session() as session:
            play_server_id = await session.scalar(
                sa.select(MPlayServerInvite.play_server_id).where(
                    MPlayServerInvite.user_id == user_id,
                    MPlayServerInvite.invite_id == invite_id,
                    MPlayServerInvite.expires_at >= datetime.now(tz=UTC),
                )
            )
            if not play_server_id:
                raise exceptions.Play_server_invite_invalid()
            await session.execute(
                sa.insert(MPlayServerAccess).values(
                    play_server_id=play_server_id,
                    user_id=user_id,
                    created_at=datetime.now(tz=UTC),
                )
            )
            await session.execute(
                sa.delete(MPlayServerInvite).where(
                    MPlayServerInvite.user_id == user_id,
                    MPlayServerInvite.invite_id == invite_id,
                )
            )
            await session.commit()
            return True

    @staticmethod
    async def delete_invite(
        play_server_id: str, owner_user_id: str, user_id: str
    ) -> bool:
        async with database.session() as session:
            p = await session.scalar(
                sa.select(MPlayServer.id).where(
                    MPlayServer.id == play_server_id,
                    MPlayServer.user_id == owner_user_id,
                    MPlayServerInvite.play_server_id == MPlayServer.id,
                    MPlayServerInvite.user_id == user_id,
                )
            )
            if not p:
                raise exceptions.Play_server_invite_invalid()
            await session.execute(
                sa.delete(MPlayServerInvite).where(
                    MPlayServerInvite.play_server_id == play_server_id,
                    MPlayServerInvite.user_id == user_id,
                )
            )
            await session.commit()
            return True


class MPlayServerMovie(Base):
    __tablename__ = 'play_server_movies'

    play_server_id: Mapped[str] = mapped_column(
        utils.sqlalchemy.UUID,
        sa.ForeignKey('play_servers.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
    )
    movie_id: Mapped[int] = mapped_column(
        sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
        autoincrement=False,
    )
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)

    @staticmethod
    @auto_session
    async def save(
        play_server_id: str,
        play_server_secret: str,
        data: list[schemas.Play_server_movie_create],
        patch=True,
        session: AsyncSession = None,
    ) -> None:
        p = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.secret == play_server_secret,
            )
        )
        if not p:
            raise exceptions.Play_server_unknown()

        if not patch:
            await session.execute(
                sa.delete(MPlayServerMovie).where(
                    MPlayServerMovie.play_server_id == play_server_id,
                )
            )
        if data:
            dt = datetime.now(tz=UTC)
            sql = sa.dialects.mysql.insert(MPlayServerMovie).values(
                [
                    {
                        'play_server_id': play_server_id,
                        'movie_id': r.movie_id,
                        'created_at': r.created_at,
                        'updated_at': dt,
                    }
                    for r in data
                ]
            )
            sql = sql.on_duplicate_key_update(
                created_at=sql.inserted.created_at,
                updated_at=sql.inserted.updated_at,
            )
            try:
                await session.execute(sql)
            except sa.exc.IntegrityError:
                for r in data:
                    t = await session.scalar(
                        sa.select(MMovie.id).where(MMovie.id == r.movie_id)
                    )
                    if not t:
                        raise exceptions.Movie_unknown(r.movie_id)
                raise

    @staticmethod
    @auto_session
    async def delete(
        play_server_id: str,
        play_server_secret: str,
        movie_id: int,
        patch=True,
        session: AsyncSession = None,
    ) -> None:
        p = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.secret == play_server_secret,
            )
        )
        if not p:
            raise exceptions.Play_server_unknown()
        await session.execute(
            sa.delete(MPlayServerMovie).where(
                MPlayServerMovie.play_server_id == play_server_id,
                MPlayServerMovie.movie_id == movie_id,
            )
        )


class MPlayServerEpisode(Base):
    __tablename__ = 'play_server_episodes'

    play_server_id: Mapped[str] = mapped_column(
        utils.sqlalchemy.UUID,
        sa.ForeignKey('play_servers.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
    )
    series_id: Mapped[int] = mapped_column(
        sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
        autoincrement=False,
    )
    episode_number: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)

    @staticmethod
    @auto_session
    async def save(
        play_server_id: str,
        play_server_secret: str,
        data: list[schemas.Play_server_episode_create],
        patch=True,
        session: AsyncSession = None,
    ) -> None:
        p = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.secret == play_server_secret,
            )
        )
        if not p:
            raise exceptions.Play_server_unknown()

        if not patch:
            await session.execute(
                sa.delete(MPlayServerEpisode).where(
                    MPlayServerEpisode.play_server_id == play_server_id,
                )
            )

        if data:
            dt = datetime.now(tz=UTC)
            sql = sa.dialects.mysql.insert(MPlayServerEpisode).values(
                [
                    {
                        'play_server_id': play_server_id,
                        'series_id': r.series_id,
                        'episode_number': r.episode_number,
                        'created_at': r.created_at,
                        'updated_at': dt,
                    }
                    for r in data
                ]
            )
            sql = sql.on_duplicate_key_update(
                created_at=sql.inserted.created_at,
                updated_at=sql.inserted.updated_at,
            )
            try:
                await session.execute(sql)
            except sa.exc.IntegrityError:
                series_ids = []
                for r in data:
                    if r.series_id in series_ids:
                        continue
                    t = await session.scalar(
                        sa.select(MSeries.id).where(MSeries.id == r.series_id)
                    )
                    if not t:
                        raise exceptions.Series_unknown(r.series_id)
                    series_ids.append(r.series_id)
                raise

    @staticmethod
    @auto_session
    async def delete(
        play_server_id: str,
        play_server_secret: str,
        series_id: int,
        episode_number: int,
        session: AsyncSession = None,
    ) -> None:
        p = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.secret == play_server_secret,
            )
        )
        if not p:
            raise exceptions.Play_server_unknown()
        await session.execute(
            sa.delete(MPlayServerEpisode).where(
                MPlayServerEpisode.play_server_id == play_server_id,
                MPlayServerEpisode.series_id == series_id,
                MPlayServerEpisode.episode_number == episode_number,
            )
        )
