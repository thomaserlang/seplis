import hashlib
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, cast
from uuid import UUID, uuid7

import jwt
import sqlalchemy as sa

from seplis import config
from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.utils import datetime_now

from ..models.device_authorization_model import MDeviceAuthorization
from ..schemas.device_authorization_schemas import (
    DeviceAuthorization,
    DeviceAuthorizationToken,
)
from .token_actions import create_token

DEVICE_AUTHORIZATION_LIFETIME = timedelta(minutes=10)
DEVICE_AUTHORIZATION_POLL_INTERVAL_SECONDS = 3
DEVICE_AUTHORIZATION_JWT_ALGORITHM = 'HS256'
DEVICE_AUTHORIZATION_JWT_AUDIENCE = 'device-authorization'
DEVICE_AUTHORIZATION_JWT_ISSUER = 'seplis'


def normalize_user_code(user_code: str) -> str:
    return user_code.replace('-', '').replace(' ', '')


def hash_device_code(device_code: str) -> str:
    return hashlib.sha256(device_code.encode()).hexdigest()


def create_device_code(*, issued_at: datetime, expires_at: datetime) -> str:
    return jwt.encode(
        {
            'aud': DEVICE_AUTHORIZATION_JWT_AUDIENCE,
            'exp': expires_at,
            'iat': issued_at,
            'iss': DEVICE_AUTHORIZATION_JWT_ISSUER,
            'jti': str(uuid7()),
        },
        get_device_authorization_secret(),
        algorithm=DEVICE_AUTHORIZATION_JWT_ALGORITHM,
    )


def validate_device_code(device_code: str) -> None:
    try:
        payload = jwt.decode(
            device_code,
            get_device_authorization_secret(),
            algorithms=[DEVICE_AUTHORIZATION_JWT_ALGORITHM],
            audience=DEVICE_AUTHORIZATION_JWT_AUDIENCE,
            issuer=DEVICE_AUTHORIZATION_JWT_ISSUER,
            options={'require': ['exp', 'iat', 'jti']},
        )
        authorization_id = payload['jti']
        if not isinstance(authorization_id, str) or UUID(authorization_id).version != 7:
            raise exceptions.DeviceAuthorizationUnknown()
    except jwt.ExpiredSignatureError:
        raise exceptions.DeviceAuthorizationExpired() from None
    except jwt.InvalidTokenError, KeyError, TypeError, ValueError:
        raise exceptions.DeviceAuthorizationUnknown() from None


def get_device_authorization_secret() -> str:
    secret = config.web.cookie_secret
    if not secret:
        raise RuntimeError('web.cookie_secret must be configured')
    return secret


def verification_uri(user_code: str | None = None) -> str:
    path = '/device'
    if user_code:
        path = f'{path}?{urllib.parse.urlencode({"code": user_code})}'
    if not config.web.url:
        return path
    return urllib.parse.urljoin(str(config.web.url), path)


async def create_device_authorization(
    session: AsyncSession | None = None,
) -> DeviceAuthorization:
    now = datetime_now()
    expires_at = now + DEVICE_AUTHORIZATION_LIFETIME
    device_code = create_device_code(issued_at=now, expires_at=expires_at)

    async with get_session(session) as session:
        await delete_expired_device_authorizations(session)
        for _ in range(10):
            user_code = f'{secrets.randbelow(1_000_000):06d}'
            exists = await session.scalar(
                sa.select(MDeviceAuthorization.user_code).where(
                    MDeviceAuthorization.user_code == user_code
                )
            )
            if exists:
                continue
            await session.execute(
                sa.insert(cast(sa.Table, MDeviceAuthorization.__table__)).values(
                    device_code_hash=hash_device_code(device_code),
                    user_code=user_code,
                    scopes='me',
                    created_at=now,
                    expires_at=expires_at,
                )
            )
            return DeviceAuthorization(
                device_code=device_code,
                user_code=user_code,
                verification_uri=verification_uri(),
                verification_uri_complete=verification_uri(user_code),
                expires_at=expires_at,
                poll_interval_seconds=DEVICE_AUTHORIZATION_POLL_INTERVAL_SECONDS,
            )

    raise RuntimeError('Unable to generate a unique device authorization code')


async def approve_device_authorization(
    *,
    user_code: str,
    user_id: int,
    session: AsyncSession | None = None,
) -> None:
    now = datetime_now()
    normalized_code = normalize_user_code(user_code)
    async with get_session(session) as session:
        authorization = (
            (
                await session.execute(
                    sa.select(MDeviceAuthorization.__table__).where(
                        MDeviceAuthorization.user_code == normalized_code
                    )
                )
            )
            .mappings()
            .first()
        )
        if not authorization:
            raise exceptions.DeviceAuthorizationUnknown()
        if authorization['expires_at'] < now:
            await delete_device_authorization(
                authorization['device_code_hash'], session=session
            )
            raise exceptions.DeviceAuthorizationExpired()
        if authorization['user_id'] is not None:
            raise exceptions.DeviceAuthorizationAlreadyApproved()

        result = cast(
            Any,
            await session.execute(
                sa.update(cast(sa.Table, MDeviceAuthorization.__table__))
                .where(
                    MDeviceAuthorization.device_code_hash
                    == authorization['device_code_hash'],
                    MDeviceAuthorization.user_id.is_(None),
                )
                .values(user_id=user_id, approved_at=now)
            ),
        )
        if result.rowcount != 1:
            raise exceptions.DeviceAuthorizationAlreadyApproved()


async def poll_device_authorization(
    *,
    device_code: str,
    session: AsyncSession | None = None,
) -> DeviceAuthorizationToken:
    validate_device_code(device_code)
    device_code_hash = hash_device_code(device_code)
    async with get_session(session) as session:
        authorization = (
            (
                await session.execute(
                    sa.select(MDeviceAuthorization.__table__).where(
                        MDeviceAuthorization.device_code_hash == device_code_hash
                    )
                )
            )
            .mappings()
            .first()
        )
        if not authorization:
            raise exceptions.DeviceAuthorizationUnknown()
        if authorization['expires_at'] < datetime_now():
            await delete_device_authorization(device_code_hash, session=session)
            raise exceptions.DeviceAuthorizationExpired()
        if authorization['user_id'] is None:
            return DeviceAuthorizationToken(status='pending')

        claimed = await delete_device_authorization(device_code_hash, session=session)
        if not claimed:
            raise exceptions.DeviceAuthorizationUnknown()

        access_token = await create_token(
            user_id=authorization['user_id'],
            scopes=authorization['scopes'].split(' '),
        )
        return DeviceAuthorizationToken(
            status='authorized',
            access_token=access_token,
            token_type='bearer',
        )


async def delete_device_authorization(
    device_code_hash: str,
    *,
    session: AsyncSession,
) -> bool:
    result = cast(
        Any,
        await session.execute(
            sa.delete(cast(sa.Table, MDeviceAuthorization.__table__)).where(
                MDeviceAuthorization.device_code_hash == device_code_hash
            )
        ),
    )
    return result.rowcount == 1


async def delete_expired_device_authorizations(session: AsyncSession) -> None:
    await session.execute(
        sa.delete(cast(sa.Table, MDeviceAuthorization.__table__)).where(
            MDeviceAuthorization.expires_at < datetime_now()
        )
    )
