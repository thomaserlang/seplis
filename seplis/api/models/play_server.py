import sqlalchemy as sa
from seplis.utils.sqlalchemy import UtcDateTime
from .base import Base
from seplis import logger, utils
from datetime import datetime, timezone, timedelta
from ..database import database, auto_session, AsyncSession
from .. import schemas, exceptions

class Play_server(Base):
    __tablename__ = 'play_servers'

    id = sa.Column(utils.sqlalchemy.UUID, primary_key=True)
    created_at = sa.Column(UtcDateTime)
    updated_at = sa.Column(UtcDateTime)
    user_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String(45))
    url = sa.Column(sa.String(200))
    secret = sa.Column(sa.String(200))

    @staticmethod
    async def save(data: schemas.Play_server_create | schemas.Play_server_update, user_id: int, play_server_id: int | None = None) -> schemas.Play_server_with_url:
        _data = data.dict(exclude_unset=True)
        async with database.session() as session:
            async with session.begin():
                if not play_server_id:
                    play_server_id = utils.sqlalchemy.uuid7_mariadb()
                    await session.execute(sa.insert(Play_server).values(
                        id=play_server_id,
                        created_at=datetime.now(tz=timezone.utc),
                        user_id=user_id,
                        **_data
                    ))
                    await session.execute(sa.insert(Play_server_access).values(
                        play_server_id=play_server_id,
                        user_id=user_id,
                        created_at=datetime.now(tz=timezone.utc),
                    ))
                else:
                    await session.execute(sa.update(Play_server).where(Play_server.id == play_server_id).values(
                        updated_at=datetime.now(tz=timezone.utc),
                        **_data
                    ))
                play_server = await session.scalar(sa.select(Play_server).where(Play_server.id == play_server_id))
                await session.commit()
                return schemas.Play_server_with_url.from_orm(play_server)


    @staticmethod
    async def delete(id_: str, user_id: int | str):        
        async with database.session() as session:
            async with session.begin():
                p = await session.scalar(sa.select(Play_server.id).where(
                    Play_server.user_id == user_id,
                    Play_server.id == id_,
                ))
                if not p:
                    raise exceptions.Not_found('Unknown play server')
                await session.execute(sa.delete(Play_server_access).where(
                    Play_server_access.play_server_id == id_, 
                ))
                await session.execute(sa.delete(Play_server).where(
                    Play_server.id == id_,
                ))
                await session.commit()


class Play_server_access(Base):
    __tablename__ = 'play_server_access'

    play_server_id = sa.Column(utils.sqlalchemy.UUID, primary_key=True)
    user_id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(UtcDateTime)


    @staticmethod
    async def remove_user(play_server_id: str, owner_user_id: int | str, user_id: int | str):
        async with database.session() as session:
            p = session.scalar(sa.select(Play_server.id).where(
                Play_server.id == play_server_id,
                Play_server.user_id == owner_user_id,
                Play_server_access.play_server_id == Play_server.id,
                Play_server_access.user_id == user_id,
            ))
            if not p:
                raise exceptions.Play_server_access_user_no_access()
            await session.execute(sa.delete(Play_server_access).where(
                Play_server_access.play_server_id == play_server_id,
                Play_server_access.user_id == user_id,
            ))
            await session.commit()
            return True


class Play_server_invite(Base):
    __tablename__ = 'play_server_invites'

    play_server_id = sa.Column(utils.sqlalchemy.UUID, sa.ForeignKey('play_servers.id', ondelete='cascade', onupdate='cascade'), primary_key=True,)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'), primary_key=True)
    invite_id = sa.Column(utils.sqlalchemy.UUID, nullable=False)
    created_at = sa.Column(UtcDateTime, nullable=False)
    expires_at = sa.Column(UtcDateTime, nullable=False)


    @staticmethod
    async def invite(play_server_id: str, owner_user_id: str, data: schemas.Play_server_invite_create) -> schemas.Play_server_invite_id:
        async with database.session() as session:
            p = await session.scalar(sa.select(Play_server.id).where(
                Play_server.id == play_server_id,
                Play_server.user_id == owner_user_id,
            ))
            if not p:
                raise exceptions.Play_server_unknown()

            p = await session.scalar(sa.select(Play_server_access.user_id).where(
                Play_server_access.play_server_id == play_server_id,
                Play_server_access.user_id == data.user_id,
            ))
            if p:
                raise exceptions.Play_server_invite_already_has_access()

            invite_id = utils.sqlalchemy.uuid7_mariadb()
            ins = sa.dialects.mysql.insert(Play_server_invite).values(
                play_server_id=play_server_id,
                invite_id=invite_id,
                created_at=datetime.now(tz=timezone.utc),
                expires_at=datetime.now(tz=timezone.utc)+timedelta(hours=24),
                **data.dict(exclude_unset=True)
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
    async def accept_invite(user_id: str, invite_id: str):
        async with database.session() as session:
            play_server_id = await session.scalar(sa.select(Play_server_invite.play_server_id).where(
                Play_server_invite.user_id == user_id,
                Play_server_invite.invite_id == invite_id,
                Play_server_invite.expires_at >= datetime.now(tz=timezone.utc),
            ))
            if not play_server_id:
                raise exceptions.Play_server_invite_invalid()
            await session.execute(sa.insert(Play_server_access).values(
                play_server_id=play_server_id,
                user_id=user_id,
                created_at=datetime.now(tz=timezone.utc),
            ))
            await session.execute(sa.delete(Play_server_invite).where(
                Play_server_invite.user_id == user_id,
                Play_server_invite.invite_id == invite_id,
            ))
            await session.commit()
            return True


    @staticmethod
    async def delete_invite(play_server_id: str, owner_user_id: str, user_id: str):
        async with database.session() as session:
            p = await session.scalar(sa.select(Play_server.id).where(
                Play_server.id == play_server_id,
                Play_server.user_id == owner_user_id,
                Play_server_invite.play_server_id == Play_server.id,
                Play_server_invite.user_id == user_id,
            ))
            if not p:
                raise exceptions.Play_server_invite_invalid()
            await session.execute(sa.delete(Play_server_invite).where(
                Play_server_invite.play_server_id == play_server_id,
                Play_server_invite.user_id == user_id,
            ))
            await session.commit()
            return True


class Play_server_movie(Base):
    __tablename__ = 'play_server_movies'

    play_server_id = sa.Column(utils.sqlalchemy.UUID, sa.ForeignKey('play_servers.id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False)
    created_at = sa.Column(UtcDateTime, nullable=False)
    updated_at = sa.Column(UtcDateTime, nullable=False)


    @staticmethod
    @auto_session
    async def save(play_server_id: str, play_server_secret: str, data: list[schemas.Play_server_movie_create], patch=True, session: AsyncSession = None):
        p = await session.scalar(sa.select(Play_server.id).where(
            Play_server.id == play_server_id,
            Play_server.secret == play_server_secret,
        ))
        if not p:
            raise exceptions.Play_server_unknown()

        if not patch:
            await session.execute(sa.delete(Play_server_movie).where(
                Play_server_movie.play_server_id == play_server_id,
            ))
        if data:
            dt = datetime.now(tz=timezone.utc)
            sql = sa.dialects.mysql.insert(Play_server_movie).values([{
                'play_server_id': play_server_id,
                'movie_id': r.movie_id,
                'created_at': r.created_at,
                'updated_at': dt,
            } for r in data])
            sql = sql.on_duplicate_key_update(
                created_at=sql.inserted.created_at,
                updated_at=sql.inserted.updated_at,
            )
            await session.execute(sql)
        
    
    @staticmethod
    @auto_session
    async def delete(play_server_id: str, play_server_secret: str, movie_id: int, patch=True, session: AsyncSession = None):
        p = await session.scalar(sa.select(Play_server.id).where(
            Play_server.id == play_server_id,
            Play_server.secret == play_server_secret,
        ))
        if not p:
            raise exceptions.Play_server_unknown()        
        await session.execute(sa.delete(Play_server_movie).where(
            Play_server_movie.play_server_id == play_server_id,
            Play_server_movie.movie_id == movie_id,
        ))


class Play_server_episode(Base):
    __tablename__ = 'play_server_episodes'
    
    play_server_id = sa.Column(utils.sqlalchemy.UUID, sa.ForeignKey('play_servers.id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    created_at = sa.Column(UtcDateTime, nullable=False)
    updated_at = sa.Column(UtcDateTime, nullable=False)


    @staticmethod
    @auto_session
    async def save(play_server_id: str, play_server_secret: str, data: list[schemas.Play_server_episode_create], patch=True, session: AsyncSession = None):
        p = await session.scalar(sa.select(Play_server.id).where(
            Play_server.id == play_server_id,
            Play_server.secret == play_server_secret,
        ))
        if not p:
            raise exceptions.Play_server_unknown()

        if not patch:
            await session.execute(sa.delete(Play_server_episode).where(
                Play_server_episode.play_server_id == play_server_id,
            ))

        if data:
            dt = datetime.now(tz=timezone.utc)
            sql = sa.dialects.mysql.insert(Play_server_episode).values([{
                'play_server_id': play_server_id,
                'series_id': r.series_id,
                'episode_number': r.episode_number,
                'created_at': r.created_at,
                'updated_at': dt,
            } for r in data])
            sql = sql.on_duplicate_key_update(
                created_at=sql.inserted.created_at,
                updated_at=sql.inserted.updated_at,
            )
            await session.execute(sql)


    @staticmethod
    @auto_session
    async def delete(play_server_id: str, play_server_secret: str, series_id: int, episode_number: int, session: AsyncSession = None):
        p = await session.scalar(sa.select(Play_server.id).where(
            Play_server.id == play_server_id,
            Play_server.secret == play_server_secret,
        ))
        if not p:
            raise exceptions.Play_server_unknown()
        await session.execute(sa.delete(Play_server_episode).where(
            Play_server_episode.play_server_id == play_server_id,
            Play_server_episode.series_id == series_id,
            Play_server_episode.episode_number == episode_number,
        ))