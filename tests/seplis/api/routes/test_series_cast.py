import pytest
from seplis.api import constants, schemas, models
from seplis.api.testbase import client, run_file, AsyncClient, user_signin

@pytest.mark.asyncio
async def test_series_cast(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_EDIT_SHOW)])

    series = await models.Series.save(schemas.Series_create(
        title='Test series',
        episodes=[
            schemas.Episode_create(number=1, title='Test episode'),
        ]
    ))

    person = await models.Person.save(schemas.Person_create(
        name='Test person',
    ))


    # add cast member
    r = await client.put(f'/2/series/{series.id}/cast', json={
        'person_id': person.id,
        'roles': [{
            'character': 'Test character',
            'total_episodes': 1,
        }]
    })
    assert r.status_code == 204, r.content

    # add cast member again
    r = await client.put(f'/2/series/{series.id}/cast', json={
        'person_id': person.id,        
        'roles': [{
            'character': 'Test character',
            'total_episodes': 1,
        }]
    })
    assert r.status_code == 204

    # get cast members
    r = await client.get(f'/2/series/{series.id}/cast')
    assert r.status_code == 200
    cast = schemas.Page_cursor_result[schemas.Series_cast_person].model_validate(r.json())
    assert len(cast.items) == 1
    assert cast.items[0].person.id == person.id
    assert cast.items[0].roles[0].character == 'Test character'
    assert cast.items[0].roles[0].total_episodes == 1


if __name__ == '__main__':
    run_file(__file__)