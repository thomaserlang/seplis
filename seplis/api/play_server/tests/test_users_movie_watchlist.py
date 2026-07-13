import pytest

from seplis.api.movie import Movie, MovieCreate, add_movie_watchlist, save_movie
from seplis.api.page_cursor import PageCursor
from seplis.api.play_server import PlayServer
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_play_server(client: AsyncClient) -> None:
    user_id = await user_signin(client)
    r = await client.post(
        '/2/play-servers',
        json={
            'name': 'Thomas',
            'url': 'http://example.net',
            'secret': 'a' * 32,
        },
    )
    assert r.status_code == 201, r.content
    play_server = parse_obj_as(PlayServer, r.json())

    movie = await save_movie(
        data=MovieCreate(
            title='Test',
            externals={'themoviedb': '1'},
        ),
        movie_id=None,
    )

    await add_movie_watchlist(user_id=user_id, movie_id=movie.id)

    r = await client.get(f'/2/play-servers/{play_server.id}/users-movie-watchlist')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Movie], r.json())
    assert data.records[0].id == movie.id

    r = await client.get(
        f'/2/play-servers/{play_server.id}/users-movie-watchlist?added_at_ge=2023-03-19T00:00:00'
    )
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Movie], r.json())
    assert data.records[0].id == movie.id

    r = await client.get(
        f'/2/play-servers/{play_server.id}/users-movie-watchlist?added_at_le=2023-03-19T00:00:00'
    )
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Movie], r.json())
    assert len(data.records) == 0

    r = await client.get(
        f'/2/play-servers/{play_server.id}/users-movie-watchlist?response_format=radarr'
    )
    assert r.status_code == 200, r.content
    data = r.json()
    assert data[0]['tmdbid'] == 1
    assert data[0]['id'] == 1


if __name__ == '__main__':
    run_file(__file__)
