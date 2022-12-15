import uuid
import sqlalchemy as sa
from .base import Base
from seplis import utils
from datetime import datetime, timezone, timedelta
from ..database import database
from .. import schemas, exceptions

class Play_server(Base):
    __tablename__ = 'play_servers'

    id = sa.Column(utils.sqlalchemy.UUID, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    updated_at = sa.Column(sa.DateTime)
    user_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String(45))
    url = sa.Column(sa.String(200))
    secret = sa.Column(sa.String(200))

    @staticmethod
    async def save(data: schemas.Play_server_create | schemas.Play_server_update, id_: int | None, user_id: int) -> schemas.Play_server_with_url:
        d = data.dict(exclude_unset=True)
        async with database.session() as session:
            async with session.begin():
                if not id_:
                    id_ = utils.sqlalchemy.uuid7_mariadb()
                    await session.execute(sa.insert(Play_server).values(
                        id=id_,
                        created_at=datetime.now(tz=timezone.utc),
                        user_id=user_id,
                        **d
                    ))
                    await session.execute(sa.insert(Play_server_access).values(
                        play_server_id=id_,
                        user_id=user_id,
                        created_at=datetime.now(tz=timezone.utc),
                    ))
                else:
                    r = await session.execute(sa.update(Play_server).where(Play_server.id == id_).values(
                        updated_at=datetime.now(tz=timezone.utc),
                        **d
                    ))
                play_server = await session.scalar(sa.select(Play_server).where(Play_server.id == id_))
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
    created_at = sa.Column(sa.DateTime)


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
    created_at = sa.Column(sa.DateTime, nullable=False)
    expires_at = sa.Column(sa.DateTime, nullable=False)


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
