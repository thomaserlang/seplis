import uuid
from datetime import UTC, datetime, timedelta
from urllib.parse import urljoin

import sqlalchemy as sa

from seplis import config
from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.send_email import send_reset_password

from ..models.reset_password_model import MResetPassword
from ..models.user_model import MUser


async def send_reset_link(email: str, session: AsyncSession | None = None) -> None:
    async with get_session(session) as session:
        user_id = await session.scalar(sa.select(MUser.id).where(MUser.email == email))
        if not user_id:
            return
        url = await create_reset_link(user_id)
        await send_reset_password(to=email, url=url)


async def create_reset_link(user_id: int) -> str:
    key = str(uuid.uuid4())
    async with get_session() as session:
        await session.execute(
            sa.insert(MResetPassword.__table__).values(  # type: ignore
                user_id=user_id,
                key=key,
                expires=datetime.now(tz=UTC) + timedelta(minutes=30),
            )
        )
    return urljoin(str(config.web.url), f'/users/reset-password/{key}')


async def get_reset_password_user_id(
    key: str, session: AsyncSession | None = None
) -> int:
    async with get_session(session) as session:
        user_id = await session.scalar(
            sa.select(MResetPassword.user_id).where(
                MResetPassword.key == key,
                MResetPassword.expires >= datetime.now(tz=UTC),
            )
        )
        if not user_id:
            raise exceptions.Forbidden('Invalid reset key')
        return user_id
