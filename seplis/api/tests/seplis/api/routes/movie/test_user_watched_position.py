import pytest

from seplis.api import models, schemas
from seplis.api.testbase import AsyncClient, run_file, user_signin


@pytest.mark.asyncio
async def test_movie_watched_position(client: AsyncClient) -> None:
    await user_signin(client)

    movie: schemas.Movie = await models.MMovie.save(
        schemas.Movie_create(
            title='Test movie',
        ),
        movie_id=None,
    )

    url = f'/2/movies/{movie.id}/watched-position'
    # Return 204 if the episode has not been watched
    r = await client.get(url)
    assert r.status_code == 204, r.content

    r = await client.put(url, json={'position': 200})
    assert r.status_code == 204, r.content

    r = await client.get(url)
    assert r.status_code == 200
    w = schemas.Movie_watched.model_validate(r.json())
    assert w.times == 0
    assert w.position == 200
    assert w.watched_at is not None

    r = await client.put(url, json={'position': 201})
    assert r.status_code == 204, r.content

    r = await client.get(url)
    assert r.status_code == 200
    w = schemas.Movie_watched.model_validate(r.json())
    assert w.times == 0
    assert w.position == 201
    assert w.watched_at is not None

    r = await client.delete(url)
    assert r.status_code == 204, r.content
    r = await client.get(url)
    assert r.status_code == 204, r.content

    r = await client.put(url, json={'position': 200})
    assert r.status_code == 204, r.content

    r = await client.get(url)
    assert r.status_code == 200
    w = schemas.Movie_watched.model_validate(r.json())
    assert w.position == 200

    r = await client.put(url, json={'position': 0})
    assert r.status_code == 204, r.content

    r = await client.get(url)
    assert r.status_code == 204, r.content

    r = await client.post(f'/2/movies/{movie.id}/watched')
    assert r.status_code == 200, r.content

    r = await client.put(url, json={'position': 200})
    assert r.status_code == 204, r.content

    r = await client.get(url)
    w = schemas.Movie_watched.model_validate(r.json())
    assert w.times == 1
    assert w.position == 200

    r = await client.delete(url)
    assert r.status_code == 204, r.content

    r = await client.get(url)
    w = schemas.Movie_watched.model_validate(r.json())
    assert w.times == 1
    assert w.position == 0


if __name__ == '__main__':
    run_file(__file__)
