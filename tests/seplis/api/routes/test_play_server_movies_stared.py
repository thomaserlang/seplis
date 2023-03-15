import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models


@pytest.mark.asyncio
async def test_play_server(client: AsyncClient):
    user_id = await user_signin(client)
    r = await client.post('/2/play-servers', json={
        'name': 'Thomas',
        'url': 'http://example.net',
        'secret': 'a'*20,
    })
    assert r.status_code == 201, r.content
    play_server = schemas.Play_server.parse_obj(r.json())

    movie = await models.Movie.save(data=schemas.Movie_create(
        title='Test',
    ), movie_id=None)

    await models.Movie_watchlist.add(user_id=user_id, movie_id=movie.id)

    r = await client.get(f'/2/play-servers/{play_server.id}/users-movie-watchlist')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Movie].parse_obj(r.json())
    assert data.items[0].id == movie.id


if __name__ == '__main__':
    run_file(__file__)