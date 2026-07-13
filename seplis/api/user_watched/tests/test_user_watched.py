import pytest

from seplis.api.movie import Movie, MovieCreate, save_movie
from seplis.api.page_cursor import PageCursor
from seplis.api.series import EpisodeCreate, Series, SeriesCreate, save_series
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin
from seplis.api.user_watched import UserWatched


@pytest.mark.asyncio
async def test_user_watched(client: AsyncClient) -> None:
    await user_signin(client)

    series1: Series = await save_series(
        SeriesCreate(
            title='Test series 1',
            episodes=[
                EpisodeCreate(title='Episode 1', number=1),
                EpisodeCreate(title='Episode 2', number=2),
            ],
        ),
        series_id=None,
    )

    series2: Series = await save_series(
        SeriesCreate(
            title='Test series 2',
            episodes=[
                EpisodeCreate(title='Episode 1', number=1),
                EpisodeCreate(title='Episode 2', number=2),
            ],
        ),
        series_id=None,
    )

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

    r = await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    assert r.status_code == 200, r.content

    r = await client.post(f'/2/series/{series2.id}/episodes/2/watched')
    assert r.status_code == 200, r.content

    r = await client.post(f'/2/movies/{movie1.id}/watched')
    assert r.status_code == 200, r.content

    r = await client.post(f'/2/movies/{movie2.id}/watched')
    assert r.status_code == 200, r.content

    r = await client.get('/2/users/me/watched')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[UserWatched], r.json())
    assert len(data.records) == 4

    r = await client.get('/2/users/me/watched?user_can_watch=true')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[UserWatched], r.json())
    assert len(data.records) == 0


if __name__ == '__main__':
    run_file(__file__)
