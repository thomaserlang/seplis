import base64
from collections.abc import Callable, Mapping
from dataclasses import Field as DataclassField
from typing import Any, ClassVar, Protocol, overload

import sqlalchemy as sa
from pydantic import BaseModel
from sqlakeyset.asyncio import select_page
from sqlalchemy.engine import Row, RowMapping
from sqlalchemy.orm import DeclarativeBase, noload

from seplis.api.common.utils.validate_helper import validate_python
from seplis.api.contexts import AsyncSession, get_session

from .schemas import PageCursor, PageCursorQuery


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, DataclassField[Any]]]


ValidTaskReturnType = BaseModel | Mapping[str, Any] | DataclassInstance


@overload
async def page_cursor[TP: tuple[Any, ...], R: ValidTaskReturnType](
    query: sa.Select[TP],
    page_query: PageCursorQuery,
    response_model: type[R],
    session: AsyncSession | None = None,
    count_total: bool = True,
    record_mapper: None = None,
) -> PageCursor[R]: ...


@overload
async def page_cursor[TP: tuple[Any, ...], R: ValidTaskReturnType](
    query: sa.Select[TP],
    page_query: PageCursorQuery,
    response_model: None = None,
    session: AsyncSession | None = None,
    count_total: bool = True,
    record_mapper: Callable[[RowMapping], R] | None = None,
) -> PageCursor[R]: ...


@overload
async def page_cursor[TP: tuple[Any, ...]](
    query: sa.Select[TP],
    page_query: PageCursorQuery,
    response_model: None = None,
    session: AsyncSession | None = None,
    count_total: bool = True,
    record_mapper: None = None,
) -> PageCursor[Row[TP]]: ...


async def page_cursor[TP: tuple[Any, ...]](
    query: sa.Select[TP],
    page_query: PageCursorQuery,
    response_model: Any | None = None,
    session: AsyncSession | None = None,
    count_total: bool = True,
    record_mapper: Callable[[RowMapping], Any] | None = None,
) -> PageCursor[Any]:
    async with get_session(session) as session:
        page = await select_page(
            s=session,
            selectable=query,
            per_page=page_query.per_page,
            page=base64.urlsafe_b64decode(page_query.cursor).decode()
            if page_query.cursor
            else None,
        )
        cursor = (
            base64.urlsafe_b64encode(page.paging.bookmark_next.encode()).decode()
            if page.paging.has_next
            else None
        )

        total = None
        if count_total:
            count_subquery = query.order_by(None).options(noload('*')).subquery()
            total = await session.scalar(
                sa.Select[TP](sa.func.count(sa.literal_column('*'))).select_from(
                    count_subquery
                )
            )
            if total is None:
                total = 0

        if record_mapper is not None:
            records = [record_mapper(row._mapping) for row in page.paging.rows]
        elif response_model is None:
            records = page.paging.rows
        else:
            records = [
                validate_record(response_model=response_model, row=row)
                for row in page.paging.rows
            ]

        return PageCursor(records=records, cursor=cursor, total=total)


def validate_record(response_model: Any, row: Row[Any]) -> Any:
    is_obj = len(row) == 1 and isinstance(row[0], DeclarativeBase)
    try:
        is_base_model = issubclass(response_model, BaseModel)
    except TypeError:
        is_base_model = False

    if is_base_model:
        return response_model.model_validate(row[0] if is_obj else dict(row._mapping))

    if is_obj:
        raise ValueError('Must use .__table__ for non-BaseModel response_model')

    return validate_python(response_model, dict(row._mapping))
