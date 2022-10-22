import uuid
import sqlalchemy as sa
from .base import Base
from seplis import utils
from datetime import datetime, timezone
from ..database import database
from .. import schemas

class Play_server(Base):
    __tablename__ = 'play_servers'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    created = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String(45))
    external_id = sa.Column(sa.String(36))
    url = sa.Column(sa.String(200))
    secret = sa.Column(sa.String(200))

    @staticmethod
    async def save(data: schemas.Play_server_create | schemas.Play_server_update, id_: int | None, user_id: int) -> schemas.Play_server_with_secret:
        d = data.dict(exclude_unset=True)
        async with database.session() as session:
            async with session.begin():
                if not id_:
                    r = await session.execute(sa.insert(Play_server).values(
                        external_id=str(uuid.uuid4()),
                        created=datetime.now(tz=timezone.utc),
                        user_id=user_id,
                        **d
                    ))
                    id_ = r.lastrowid
                    await session.execute(sa.insert(Play_access).values(
                        play_server_id=id_,
                        user_id=user_id,
                    ))
                else:
                    r = await session.execute(sa.update(Play_server).where(Play_server.id == id_).values(
                        updated=datetime.now(tz=timezone.utc),
                        **d
                    ))
                play_server = await session.scalar(sa.select(Play_server).where(Play_server.id == id_))
                await session.commit()
                return schemas.Play_server_with_secret.from_orm(play_server)


class Play_access(Base):
    __tablename__ = 'play_access'

    play_server_id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, primary_key=True)

