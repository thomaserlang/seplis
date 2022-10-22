import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models

@pytest.mark.asyncio
async def test_movie_watched(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    movie: schemas.Movie = await models.Movie.save(schemas.Movie_create(
        title='Movie',
    ), movie_id=None)

    r = await client.get(f'/2/movies/{movie.id}/stared')
    assert r.status_code == 200, r.body
    data = schemas.Movie_stared.parse_obj(r.json())
    assert data.stared == False
    assert data.created_at == None
    
    r = await client.put(f'/2/movies/{movie.id}/stared')
    assert r.status_code == 204, r.body
    
    r = await client.get(f'/2/movies/{movie.id}/stared')
    assert r.status_code == 200
    data = schemas.Movie_stared.parse_obj(r.json())
    assert data.stared == True
    assert data.created_at != None
    
    r = await client.delete(f'/2/movies/{movie.id}/stared')
    assert r.status_code == 204

    r = await client.get(f'/2/movies/{movie.id}/stared')
    assert r.status_code == 200
    data = schemas.Movie_stared.parse_obj(r.json())
    assert data.stared == False
    assert data.created_at == None


if __name__ == '__main__':
    run_file(__file__)