import pytest
from seplis.api import constants, schemas, models
from seplis.api.testbase import client, run_file, AsyncClient, user_signin

@pytest.mark.asyncio
async def test_movie_cast(client: AsyncClient):
    await user_signin(client, ['movie:edit'])

    movie = await models.Movie.save(schemas.Movie_create(
        title='Test movie',
    ))

    person = await models.Person.save(schemas.Person_create(
        name='Test person',
    ))

    # add cast member
    r = await client.put(f'/2/movies/{movie.id}/cast', json={
        'person_id': person.id,
        'character': 'Test character',
    })
    assert r.status_code == 204

    # add cast member again
    r = await client.put(f'/2/movies/{movie.id}/cast', json={
        'person_id': person.id,
        'character': 'Test character',
    })
    assert r.status_code == 204

    # get cast members
    r = await client.get(f'/2/movies/{movie.id}/cast')
    assert r.status_code == 200
    cast = schemas.Page_cursor_result[schemas.Movie_cast_person].model_validate(r.json())
    assert len(cast.items) == 1
    assert cast.items[0].person.id == person.id
    assert cast.items[0].character == 'Test character'


if __name__ == '__main__':
    run_file(__file__)