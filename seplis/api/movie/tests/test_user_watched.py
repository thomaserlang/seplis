from datetime import UTC, datetime

import pytest
from freezegun import freeze_time

from seplis.api.movie import MovieCreate, MovieWatched, add_movie_watchlist, save_movie
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@freeze_time(datetime(2022, 6, 5, 13, 0, tzinfo=UTC))
@pytest.mark.asyncio
async def test_movie_watched(client: AsyncClient) -> None:
    user_id = await user_signin(client)

    movie = await save_movie(
        MovieCreate(
            title='Movie',
        ),
        movie_id=None,
    )

    await add_movie_watchlist(user_id=user_id, movie_id=movie.id)

    r = await client.get(f'/2/movies/{movie.id}/watched')
    data = parse_obj_as(MovieWatched, r.json())
    assert data.times == 0
    assert data.position == 0
    assert data.watched_at is None

    r = await client.post(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = parse_obj_as(MovieWatched, r.json())
    assert data.times == 1
    assert data.watched_at is not None

    r = await client.get(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = parse_obj_as(MovieWatched, r.json())
    assert data.times == 1
    assert data.position == 0
    assert data.watched_at is not None

    r = await client.post(
        f'/2/movies/{movie.id}/watched',
        json={
            'watched_at': '2022-06-05T22:00:00+02:00',
        },
    )
    assert r.status_code == 200
    data = parse_obj_as(MovieWatched, r.json())
    assert data.times == 2
    assert data.watched_at == datetime(2022, 6, 5, 20, 0, tzinfo=UTC), data.watched_at

    r = await client.get('/2/movies?user_watchlist=true')
    assert r.status_code == 200, r.content
    assert len(r.json()['records']) == 0

    r = await client.post(
        f'/2/movies/{movie.id}/watched',
        json={
            'watched_at': '2022-06-05T21:00:00Z',
        },
    )
    assert r.status_code == 200
    data = parse_obj_as(MovieWatched, r.json())
    assert data.times == 3
    assert data.position == 0
    assert data.watched_at == datetime(2022, 6, 5, 21, 0, 0, tzinfo=UTC)

    r = await client.delete(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = parse_obj_as(MovieWatched, r.json())
    assert data.times == 2
    assert data.position == 0
    assert data.watched_at == datetime(2022, 6, 5, 20, 0, 0, tzinfo=UTC)

    r = await client.delete(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = parse_obj_as(MovieWatched, r.json())
    assert data.times == 1
    assert data.position == 0
    assert data.watched_at == datetime(2022, 6, 5, 13, 0, tzinfo=UTC)

    r = await client.put(f'/2/movies/{movie.id}/watched-position', json={'position': 200})
    assert r.status_code == 204, r.content

    r = await client.delete(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200

    r = await client.get(f'/2/movies/{movie.id}/watched')
    w = parse_obj_as(MovieWatched, r.json())
    assert w.times == 1
    assert w.position == 0

    r = await client.delete(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = parse_obj_as(MovieWatched, r.json())
    assert data.times == 0
    assert data.position == 0
    assert data.watched_at is None

    r = await client.get(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = parse_obj_as(MovieWatched, r.json())
    assert data.times == 0
    assert data.position == 0
    assert data.watched_at is None


if __name__ == '__main__':
    run_file(__file__)
