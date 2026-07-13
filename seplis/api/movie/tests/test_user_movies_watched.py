import pytest

from seplis.api.movie import Movie, MovieCreate, save_movie
from seplis.api.page_cursor import PageCursor
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_movie_watched(client: AsyncClient) -> None:
    await user_signin(client)

    movie1: Movie = await save_movie(
        MovieCreate(
            title='Movie 1',
        ),
        movie_id=None,
    )

    movie2: Movie = await save_movie(
        MovieCreate(
            title='Movie 2',
        ),
        movie_id=None,
    )

    r = await client.get('/2/movies?user_has_watched=true')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Movie], r.json())
    assert len(data.records) == 0

    r = await client.post(f'/2/movies/{movie1.id}/watched')
    assert r.status_code == 200, r.content

    r = await client.post(f'/2/movies/{movie2.id}/watched')
    assert r.status_code == 200, r.content

    r = await client.get('/2/movies?user_has_watched=true&expand=user_watched')
    assert r.status_code == 200, r.content
    data = parse_obj_as(PageCursor[Movie], r.json())
    assert len(data.records) == 2
    assert data.records[0].title == 'Movie 1'
    assert data.records[0].user_watched.times == 1
    assert data.records[1].title == 'Movie 2'
    assert data.records[1].user_watched.times == 1


if __name__ == '__main__':
    run_file(__file__)
