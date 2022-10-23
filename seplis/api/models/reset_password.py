import uuid
import sqlalchemy as sa
from .base import Base
from ..database import database
from ... import config
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

class Reset_password(Base):
    __tablename__ = 'reset_password'

    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    key = sa.Column(sa.String, primary_key=True)
    expires = sa.Column(sa.DateTime)

    @staticmethod
    async def create_reset_link(user_id: int) -> str:
        async with database.session() as session:
            key = str(uuid.uuid4())
            await session.execute(sa.insert(Reset_password).values(
                user_id=user_id,
                key=key,
                expires=datetime.now(tz=timezone.utc) + timedelta(hours=24),
            ))
            await session.commit()
            return config.data.web.url + f'/reset-password/{key}'