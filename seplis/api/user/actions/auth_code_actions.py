import secrets
from collections.abc import Sequence
from datetime import timedelta

import sqlalchemy as sa

from seplis.api.contexts import AsyncSession, get_session
from seplis.utils import datetime_now

from ..models.auth_code_model import MAuthCode
from ..schemas.auth_code_schemas import AuthCode, AuthCodeRedeemed


async def create_auth_code(
    action_by_user_id: int, scopes: Sequence[str], session: AsyncSession | None = None
) -> AuthCode:
    expires_at = datetime_now() + timedelta(minutes=10)
    async with get_session(session) as session:
        await delete_auth_codes(user_id=action_by_user_id, session=session)
        for _ in range(10):
            code = f'{secrets.randbelow(1_000_000):06d}'
            exists = (
                await session.execute(
                    sa.select(MAuthCode.__table__).where(MAuthCode.code == code)
                )
            ).first()
            if exists:
                continue
            await session.execute(
                sa.insert(MAuthCode.__table__).values(  # type: ignore
                    code=code,
                    user_id=action_by_user_id,
                    expires_at=expires_at,
                    created_at=datetime_now(),
                    scopes=' '.join(scopes),
                )
            )
            return AuthCode(code=code, expires_at=expires_at)

    raise RuntimeError('Unable to generate tv auth code')


async def delete_auth_codes(
    user_id: int | None = None, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        stmt = sa.delete(MAuthCode.__table__)  # type: ignore
        if user_id is not None:
            stmt = stmt.where(MAuthCode.user_id == user_id)
        else:
            stmt = stmt.where(MAuthCode.expires_at < datetime_now())
        await session.execute(stmt)


async def redeem_auth_code(
    code: str, session: AsyncSession | None = None
) -> AuthCodeRedeemed | None:
    async with get_session(session) as session:
        auth_code = (
            await session.execute(
                sa.select(MAuthCode.__table__)
                .where(MAuthCode.code == code, MAuthCode.expires_at >= datetime_now())
                .with_for_update(nowait=True)
            )
        ).first()

        if not auth_code:
            return None

        await delete_auth_codes(user_id=auth_code.user_id, session=session)

        return AuthCodeRedeemed(
            user_id=auth_code.user_id, scopes=auth_code.scopes.split(' ')
        )
