from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.engine import RowMapping
from uuid6 import uuid7

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor

from ..models.play_server_model import (
    MPlayServer,
    MPlayServerAccess,
)
from ..schemas.play_server_schemas import (
    PlayServer,
    PlayServerCreate,
    PlayServerUpdate,
    PlayServerWithUrl,
)


def play_server_mapper(play_server: MPlayServer) -> PlayServer:
    return PlayServer(
        id=play_server.id,
        name=play_server.name,
    )


def play_server_row_mapper(row: RowMapping) -> PlayServer:
    return play_server_mapper(row['MPlayServer'])


def play_server_with_url_mapper(
    play_server: MPlayServer | None,
) -> PlayServerWithUrl:
    if not play_server:
        raise exceptions.PlayServerUnknown()
    return PlayServerWithUrl(
        id=play_server.id,
        name=play_server.name,
        url=play_server.url or '',
    )


def play_server_with_url_row_mapper(row: RowMapping) -> PlayServerWithUrl:
    return play_server_with_url_mapper(row['MPlayServer'])


async def create_play_server(data: PlayServerCreate, user_id: int) -> PlayServerWithUrl:
    return await save_play_server(data=data, play_server_id=None, user_id=user_id)


async def update_play_server(
    play_server_id: str,
    data: PlayServerUpdate,
    user_id: int,
) -> PlayServerWithUrl:
    return await save_play_server(
        data=data, play_server_id=play_server_id, user_id=user_id
    )


async def save_play_server(
    data: PlayServerCreate | PlayServerUpdate,
    user_id: int,
    play_server_id: str | None = None,
) -> PlayServerWithUrl:
    values = dict(data)
    async with get_session() as session:
        if not play_server_id:
            play_server_id = str(uuid7())
            await session.execute(
                sa.insert(MPlayServer.__table__).values(  # type: ignore
                    id=play_server_id,
                    created_at=datetime.now(tz=UTC),
                    user_id=user_id,
                    **values,
                )
            )
            await session.execute(
                sa.insert(MPlayServerAccess.__table__).values(  # type: ignore
                    play_server_id=play_server_id,
                    user_id=user_id,
                    created_at=datetime.now(tz=UTC),
                )
            )
        else:
            await session.execute(
                sa.update(MPlayServer.__table__)  # type: ignore
                .where(MPlayServer.id == play_server_id)
                .values(updated_at=datetime.now(tz=UTC), **values)
            )
        play_server = await session.scalar(
            sa.select(MPlayServer).where(MPlayServer.id == play_server_id)
        )
        return play_server_with_url_mapper(play_server)


async def get_play_server(
    play_server_id: str, user_id: int, session: AsyncSession | None = None
) -> PlayServerWithUrl:
    async with get_session(session) as session:
        play_server = await session.scalar(
            sa.select(MPlayServer).where(
                MPlayServer.user_id == user_id,
                MPlayServer.id == play_server_id,
            )
        )
        if not play_server:
            raise exceptions.NotFound('Unknown play server')
        return play_server_with_url_mapper(play_server)


async def delete_play_server(play_server_id: str, user_id: int) -> None:
    async with get_session() as session:
        exists = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.user_id == user_id,
                MPlayServer.id == play_server_id,
            )
        )
        if not exists:
            raise exceptions.NotFound('Unknown play server')
        await session.execute(
            sa.delete(MPlayServerAccess.__table__).where(  # type: ignore
                MPlayServerAccess.play_server_id == play_server_id,
            )
        )
        await session.execute(
            sa.delete(MPlayServer.__table__).where(  # type: ignore
                MPlayServer.id == play_server_id,
            )
        )


async def get_play_servers(
    user_id: int,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[PlayServer]:
    query = (
        sa.select(MPlayServer)
        .where(MPlayServer.user_id == user_id)
        .order_by(sa.asc(MPlayServer.name))
    )
    return await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        record_mapper=play_server_row_mapper,
    )


async def get_play_servers_with_access(
    user_id: int,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[PlayServerWithUrl]:
    query = (
        sa.select(MPlayServer)
        .where(
            MPlayServerAccess.user_id == user_id,
            MPlayServerAccess.play_server_id == MPlayServer.id,
            MPlayServer.user_id != user_id,
        )
        .order_by(sa.asc(MPlayServer.name), sa.asc(MPlayServer.id))
    )
    return await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        record_mapper=play_server_with_url_row_mapper,
    )
