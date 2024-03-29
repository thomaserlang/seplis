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
    play_server = schemas.Play_server.model_validate(r.json())

    movie = await models.Movie.save(data=schemas.Movie_create(
        title='Test',
        externals={'themoviedb': '1'},
    ), movie_id=None)

    await models.Movie_watchlist.add(user_id=user_id, movie_id=movie.id)

    r = await client.get(f'/2/play-servers/{play_server.id}/users-movie-watchlist')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Movie].model_validate(r.json())
    assert data.items[0].id == movie.id

    r = await client.get(f'/2/play-servers/{play_server.id}/users-movie-watchlist?added_at_ge=2023-03-19T00:00:00')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Movie].model_validate(r.json())
    assert data.items[0].id == movie.id

    r = await client.get(f'/2/play-servers/{play_server.id}/users-movie-watchlist?added_at_le=2023-03-19T00:00:00')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Movie].model_validate(r.json())
    assert len(data.items) == 0


    r = await client.get(f'/2/play-servers/{play_server.id}/users-movie-watchlist?response_format=radarr')
    assert r.status_code == 200, r.content
    data = r.json()
    assert data[0]['tmdbid'] == 1
    assert data[0]['id'] == 1


if __name__ == '__main__':
    run_file(__file__)