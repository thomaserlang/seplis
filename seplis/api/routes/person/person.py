from fastapi import Security
from ...dependencies import authenticated
from ... import models, schemas, exceptions
from .router import router


@router.post('', response_model=schemas.Person, status_code=201,
            description='''
            **Scope required:** `person:create`
            ''')
async def person_create(
    data: schemas.Person_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=['person:create']),
):
    return await models.Person.save(data=data)


@router.put('/{person_id}', response_model=schemas.Person,
            description='''
            **Scope required:** `person:edit`
            ''')
async def person_update(
    person_id: int,
    data: schemas.Person_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=['person:edit']),
):
    return await models.Person.save(
        person_id=person_id,
        data=data,
        patch=False,
    )


@router.patch('/{person_id}', response_model=schemas.Person,
            description='''
            **Scope required:** `person:edit`
            ''')
async def person_patch(
    person_id: int,
    data: schemas.Person_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=['person:edit']),
):
    return await models.Person.save(
        person_id=person_id,
        data=data,
        patch=True,
    )


@router.get('/{person_id}', response_model=schemas.Person,
            description='''
            **Scope required:** `person:read`
            ''')
async def person_get(
    person_id: int,
):
    person = await models.Person.get(person_id=person_id)
    if not person:
        raise exceptions.Not_found('Person not found')
    return person


@router.delete('/{person_id}', status_code=204,
            description='''
            **Scope required:** `person:delete`
            ''')
async def person_delete(
    person_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['person:delete']),
):
    await models.Person.delete(person_id=person_id)