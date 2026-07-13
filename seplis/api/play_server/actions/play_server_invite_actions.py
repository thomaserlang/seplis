from datetime import UTC, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.engine import RowMapping
from uuid6 import uuid7

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor
from seplis.api.user import UserPublic
from seplis.api.user.models.user_model import MUserPublic

from ..models.play_server_model import (
    MPlayServer,
    MPlayServerAccess,
    MPlayServerInvite,
)
from ..schemas.play_server_schemas import (
    PlayServerInvite,
    PlayServerInviteCreate,
    PlayServerInviteId,
)


def play_server_invite_mapper(row: RowMapping) -> PlayServerInvite:
    user = row['MUserPublic']
    return PlayServerInvite(
        created_at=row['created_at'],
        expires_at=row['expires_at'],
        user=UserPublic(id=user.id, username=user.username),
    )


async def create_play_server_invite(
    play_server_id: str,
    owner_user_id: int,
    data: PlayServerInviteCreate,
) -> PlayServerInviteId:
    async with get_session() as session:
        play_server = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.user_id == owner_user_id,
            )
        )
        if not play_server:
            raise exceptions.PlayServerUnknown()

        existing_access = await session.scalar(
            sa.select(MPlayServerAccess.user_id).where(
                MPlayServerAccess.play_server_id == play_server_id,
                MPlayServerAccess.user_id == data['user_id'],
            )
        )
        if existing_access:
            raise exceptions.PlayServerInviteAlreadyHasAccess()

        invite_id = str(uuid7())
        stmt = sa.dialects.mysql.insert(MPlayServerInvite.__table__).values(  # type: ignore
            play_server_id=play_server_id,
            invite_id=invite_id,
            created_at=datetime.now(tz=UTC),
            expires_at=datetime.now(tz=UTC) + timedelta(hours=24),
            **dict(data),
        )
        stmt = stmt.on_duplicate_key_update(
            invite_id=stmt.inserted.invite_id,
            created_at=stmt.inserted.created_at,
            expires_at=stmt.inserted.expires_at,
        )
        await session.execute(stmt)
        return PlayServerInviteId(invite_id=invite_id)


async def get_play_server_invites(
    play_server_id: str,
    owner_user_id: int,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[PlayServerInvite]:
    query = (
        sa.select(
            MPlayServerInvite.created_at,
            MPlayServerInvite.expires_at,
            MUserPublic,
        )
        .where(
            MPlayServer.user_id == owner_user_id,
            MPlayServer.id == play_server_id,
            MPlayServerInvite.play_server_id == MPlayServer.id,
            MUserPublic.id == MPlayServerInvite.user_id,
        )
        .order_by(sa.asc(MPlayServer.name))
    )
    return await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        record_mapper=play_server_invite_mapper,
    )


async def delete_play_server_invite(
    play_server_id: str,
    owner_user_id: int,
    user_id: int,
) -> None:
    async with get_session() as session:
        invite = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.user_id == owner_user_id,
                MPlayServerInvite.play_server_id == MPlayServer.id,
                MPlayServerInvite.user_id == user_id,
            )
        )
        if not invite:
            raise exceptions.PlayServerInviteInvalid()
        await session.execute(
            sa.delete(MPlayServerInvite.__table__).where(  # type: ignore
                MPlayServerInvite.play_server_id == play_server_id,
                MPlayServerInvite.user_id == user_id,
            )
        )


async def accept_play_server_invite(user_id: int, invite_id: str) -> None:
    async with get_session() as session:
        play_server_id = await session.scalar(
            sa.select(MPlayServerInvite.play_server_id).where(
                MPlayServerInvite.user_id == user_id,
                MPlayServerInvite.invite_id == invite_id,
                MPlayServerInvite.expires_at >= datetime.now(tz=UTC),
            )
        )
        if not play_server_id:
            raise exceptions.PlayServerInviteInvalid()
        await session.execute(
            sa.insert(MPlayServerAccess.__table__).values(  # type: ignore
                play_server_id=play_server_id,
                user_id=user_id,
                created_at=datetime.now(tz=UTC),
            )
        )
        await session.execute(
            sa.delete(MPlayServerInvite.__table__).where(  # type: ignore
                MPlayServerInvite.user_id == user_id,
                MPlayServerInvite.invite_id == invite_id,
            )
        )
