from typing import cast

import sqlalchemy as sa
from sqlalchemy.engine import RowMapping

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor
from seplis.api.user import UserPublic
from seplis.api.user.models.user_model import MUserPublic

from ..models.play_server_model import MPlayServer, MPlayServerAccess
from ..schemas.play_server_schemas import PlayServerAccess


def play_server_access_mapper(row: RowMapping) -> PlayServerAccess:
    return PlayServerAccess(
        created_at=row['access_created_at'],
        user=UserPublic(id=row['user_id'], username=row['username']),
    )


async def get_users_with_access(
    play_server_id: str,
    owner_user_id: int,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[PlayServerAccess]:
    query = (
        sa.select(
            MPlayServerAccess.created_at.label('access_created_at'),
            MUserPublic.id.label('user_id'),
            MUserPublic.username,
        )
        .where(
            MPlayServer.user_id == owner_user_id,
            MPlayServer.id == play_server_id,
            MPlayServerAccess.play_server_id == MPlayServer.id,
            MUserPublic.id == MPlayServerAccess.user_id,
        )
        .order_by(sa.asc(MUserPublic.username), sa.asc(MUserPublic.id))
    )
    return await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        record_mapper=play_server_access_mapper,
    )


async def remove_user_access(
    play_server_id: str,
    owner_user_id: int,
    user_id: int,
) -> None:
    async with get_session() as session:
        has_access = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.user_id == owner_user_id,
                MPlayServerAccess.play_server_id == MPlayServer.id,
                MPlayServerAccess.user_id == user_id,
            )
        )
        if not has_access:
            raise exceptions.PlayServerAccessUserNoAccess()
        await session.execute(
            sa.delete(cast(sa.Table, MPlayServerAccess.__table__)).where(
                MPlayServerAccess.play_server_id == play_server_id,
                MPlayServerAccess.user_id == user_id,
            )
        )


async def leave_play_server(play_server_id: str, user_id: int) -> None:
    async with get_session() as session:
        play_server = (
            (
                await session.execute(
                    sa.select(MPlayServer.__table__).where(
                        MPlayServer.id == play_server_id,
                    )
                )
            )
            .mappings()
            .first()
        )
        if not play_server:
            raise exceptions.PlayServerUnknown()
        if play_server['user_id'] == user_id:
            raise exceptions.Forbidden(
                'Owner cannot remove their own access from the play server'
            )

        has_access = await session.scalar(
            sa.select(MPlayServerAccess.play_server_id).where(
                MPlayServerAccess.play_server_id == play_server_id,
                MPlayServerAccess.user_id == user_id,
            )
        )
        if not has_access:
            raise exceptions.PlayServerAccessUserNoAccess()

        await session.execute(
            sa.delete(cast(sa.Table, MPlayServerAccess.__table__)).where(
                MPlayServerAccess.play_server_id == play_server_id,
                MPlayServerAccess.user_id == user_id,
            )
        )
