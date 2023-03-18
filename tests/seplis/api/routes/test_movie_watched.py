import pytest
from freezegun import freeze_time
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models
from datetime import datetime, timezone

@freeze_time(datetime(2022, 6, 5, 13, 0, tzinfo=timezone.utc))
@pytest.mark.asyncio
async def test_movie_watched(client: AsyncClient):
    user_id = await user_signin(client, [str(constants.LEVEL_USER)])

    movie = await models.Movie.save(schemas.Movie_create(
        title='Movie',
    ), movie_id=None)

    await models.Movie_watchlist.add(user_id, movie.id)

    r = await client.get(f'/2/movies/{movie.id}/watched')
    data = schemas.Movie_watched.parse_obj(r.json())
    assert data.times == 0
    assert data.position == 0
    assert data.watched_at == None

    r = await client.post(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = schemas.Movie_watched.parse_obj(r.json())
    assert data.times == 1
    assert data.watched_at != None
    
    r = await client.get(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = schemas.Movie_watched.parse_obj(r.json())
    assert data.times == 1
    assert data.position == 0
    assert data.watched_at != None

    r = await client.post(f'/2/movies/{movie.id}/watched', json={
        'watched_at': '2022-06-05T22:00:00+02',
    })
    assert r.status_code == 200
    data = schemas.Movie_watched.parse_obj(r.json())
    assert data.times == 2
    assert data.watched_at == datetime(2022, 6, 5, 20, 0, tzinfo=timezone.utc), data.watched_at
    
    r = await client.get(f'/2/movies?user_watchlist=true')
    assert r.status_code == 200
    assert len(r.json()['items']) == 0

    r = await client.post(f'/2/movies/{movie.id}/watched', json={
        'watched_at': '2022-06-05T21:00:00Z',
    })
    assert r.status_code == 200
    data = schemas.Movie_watched.parse_obj(r.json())
    assert data.times == 3
    assert data.position == 0
    assert data.watched_at == datetime(2022, 6, 5, 21, 0, 0, tzinfo=timezone.utc)

    r = await client.delete(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = schemas.Movie_watched.parse_obj(r.json())
    assert data.times == 2
    assert data.position == 0
    assert data.watched_at == datetime(2022, 6, 5, 20, 0, 0, tzinfo=timezone.utc)

    r = await client.delete(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = schemas.Movie_watched.parse_obj(r.json())
    assert data.times == 1
    assert data.position == 0
    assert data.watched_at == datetime(2022, 6, 5, 13, 0, tzinfo=timezone.utc)

    r = await client.put(f'/2/movies/{movie.id}/watched-position', json={'position': 200})
    assert r.status_code == 204, r.content

    r = await client.delete(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200

    r = await client.get(f'/2/movies/{movie.id}/watched')
    w = schemas.Movie_watched.parse_obj(r.json())
    assert w.times == 1
    assert w.position == 0

    r = await client.delete(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = schemas.Movie_watched.parse_obj(r.json())
    assert data.times == 0
    assert data.position == 0
    assert data.watched_at == None

    r = await client.get(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200
    data = schemas.Movie_watched.parse_obj(r.json())
    assert data.times == 0
    assert data.position == 0
    assert data.watched_at == None
    

if __name__ == '__main__':
    run_file(__file__)