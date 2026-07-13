from typing import Annotated

from fastapi import APIRouter, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.person_actions import (
    create_person,
    delete_person,
    get_person,
    patch_person,
    update_person,
)
from ..schemas.person_schemas import Person, PersonCreate, PersonUpdate

router = APIRouter()


@router.post(
    '',
    status_code=201,
    description="""
            **Scope required:** `person:create`
            """,
)
async def person_create_route(
    data: PersonCreate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['person:create'])],
) -> Person:
    return await create_person(data)


@router.put(
    '/{person_id}',
    description="""
            **Scope required:** `person:edit`
            """,
)
async def person_update_route(
    person_id: int,
    data: PersonUpdate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['person:edit'])],
) -> Person:
    return await update_person(person_id, data)


@router.patch(
    '/{person_id}',
    description="""
            **Scope required:** `person:edit`
            """,
)
async def person_patch_route(
    person_id: int,
    data: PersonUpdate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['person:edit'])],
) -> Person:
    return await patch_person(person_id, data)


@router.get(
    '/{person_id}',
    description="""
            **Scope required:** `person:read`
            """,
)
async def person_get_route(person_id: int) -> Person:
    return await get_person(person_id)


@router.delete(
    '/{person_id}',
    status_code=204,
    description="""
            **Scope required:** `person:delete`
            """,
)
async def person_delete_route(
    person_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['person:delete'])],
) -> None:
    await delete_person(person_id)
