import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models

@pytest.mark.asyncio
async def test_user_movies_watchlist(client: AsyncClient):
    await user_signin(client)

    movie1: schemas.Movie = await models.Movie.save(schemas.Movie_create(
        title='Movie 1',
    ), movie_id=None)

    movie2: schemas.Movie = await models.Movie.save(schemas.Movie_create(
        title='Movie 2',
    ), movie_id=None)
    
    r = await client.get(f'/2/movies?user_watchlist=true')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Movie].model_validate(r.json())
    assert len(data.items) == 0

    r = await client.put(f'/2/movies/{movie1.id}/watchlist')
    assert r.status_code == 204, r.body

    r = await client.put(f'/2/movies/{movie2.id}/watchlist')
    assert r.status_code == 204, r.body
    
    r = await client.get(f'/2/movies?user_watchlist=true')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Movie].model_validate(r.json())
    assert len(data.items) == 2
    assert data.items[0].title == 'Movie 1'
    assert data.items[1].title == 'Movie 2'
    

if __name__ == '__main__':
    run_file(__file__)