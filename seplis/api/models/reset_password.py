import uuid
from datetime import UTC, datetime, timedelta
from urllib.parse import urljoin

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.utils.sqlalchemy import UtcDateTime

from ... import config
from ..database import database
from .base import Base


class MResetPassword(Base):
    __tablename__ = 'reset_password'

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    key: Mapped[str] = mapped_column(sa.String, primary_key=True)
    expires: Mapped[datetime | None] = mapped_column(UtcDateTime)

    @staticmethod
    async def create_reset_link(user_id: int) -> str:
        async with database.session() as session:
            key = str(uuid.uuid4())
            await session.execute(
                sa.insert(MResetPassword).values(
                    user_id=user_id,
                    key=key,
                    expires=datetime.now(tz=UTC) + timedelta(minutes=30),
                )
            )
            await session.commit()
            return urljoin(str(config.web.url), f'/users/reset-password/{key}')
