import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models

@pytest.mark.asyncio
async def test_movie_(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    movie: schemas.Movie = await models.Movie.save(schemas.Movie_create(
        title='Movie',
    ), movie_id=None)

    r = await client.get(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 200, r.content
    data = schemas.Movie_favorite.parse_obj(r.json())
    assert data.favorite == False
    assert data.created_at == None
    
    r = await client.put(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 204, r.content
    
    r = await client.get(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 200
    data = schemas.Movie_favorite.parse_obj(r.json())
    assert data.favorite == True
    assert data.created_at != None
    
    r = await client.delete(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 204

    r = await client.get(f'/2/movies/{movie.id}/favorite')
    assert r.status_code == 200
    data = schemas.Movie_favorite.parse_obj(r.json())
    assert data.favorite == False
    assert data.created_at == None


if __name__ == '__main__':
    run_file(__file__)