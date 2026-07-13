import pytest

from seplis.api.page_cursor import PageCursor
from seplis.api.series import Episode, EpisodeCreate, Series, SeriesCreate, save_series
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_episode_to_watch(client: AsyncClient) -> None:
    series: Series = await save_series(
        SeriesCreate(
            title='Test series',
            runtime=30,
            episodes=[
                EpisodeCreate(number=1, title='1'),
                EpisodeCreate(number=2, title='2'),
                EpisodeCreate(number=3, title='3', runtime=40),
            ],
        ),
        series_id=None,
    )

    r = await client.get(f'/2/series/{series.id}/episodes')
    assert r.status_code == 200, r.content
    data = parse_obj_as(PageCursor[Episode], r.json())
    for episode in data.records:
        assert episode.user_watched is None

    r = await client.get(
        f'/2/series/{series.id}/episodes', params={'expand': 'user_watched'}
    )
    assert r.status_code == 401

    await user_signin(client)

    r = await client.get(
        f'/2/series/{series.id}/episodes', params={'expand': 'something, user_watched'}
    )
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Episode], r.json())
    for episode in data.records:
        assert episode.user_watched.times == 0

    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content

    r = await client.get(
        f'/2/series/{series.id}/episodes', params={'expand': 'user_watched'}
    )
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Episode], r.json())
    for episode in data.records:
        if episode.number == 1:
            assert episode.user_watched.times == 1
        else:
            assert episode.user_watched.times == 0


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient) -> None:
    series: Series = await save_series(
        SeriesCreate(
            title='Test series',
            runtime=30,
            episodes=[
                EpisodeCreate(number=1, title='1'),
                EpisodeCreate(number=2, title='2'),
                EpisodeCreate(number=3, title='3'),
                EpisodeCreate(number=4, title='4'),
                EpisodeCreate(number=5, title='5'),
            ],
        ),
        series_id=None,
    )

    r = await client.get(
        f'/2/series/{series.id}/episodes',
        params={
            'per_page': 1,
        },
    )
    data = parse_obj_as(PageCursor[Episode], r.json())
    assert len(data.records) == 1
    assert data.records[0].number == 1
    assert len(data.cursor) > 1

    r = await client.get(
        f'/2/series/{series.id}/episodes',
        params={
            'per_page': 1,
            'cursor': data.cursor,
        },
    )
    data = parse_obj_as(PageCursor[Episode], r.json())
    assert len(data.records) == 1
    assert data.records[0].number == 2


if __name__ == '__main__':
    run_file(__file__)
