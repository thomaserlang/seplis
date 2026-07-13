import pytest

from seplis.api.page_cursor import PageCursor
from seplis.api.series import EpisodeCreate, Series, SeriesCreate, save_series
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_user_series_watched(client: AsyncClient) -> None:
    await user_signin(client)
    series1: Series = await save_series(
        SeriesCreate(
            title='Test series',
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

    r = await client.get(
        '/2/series?user_has_watched=true&expand=user_last_episode_watched'
    )
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[Series], r.json())
    assert data.records == []

    r = await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    assert r.status_code == 200, r.content

    r = await client.get(
        '/2/series?user_has_watched=true&expand=user_last_episode_watched'
    )
    assert r.status_code == 200, r.content
    data = parse_obj_as(PageCursor[Series], r.json())
    assert data.records[0].id == series1.id
    assert data.records[0].user_last_episode_watched.number == 1

    r = await client.post(f'/2/series/{series2.id}/episodes/2/watched')
    assert r.status_code == 200, r.content

    r = await client.get(
        '/2/series?user_has_watched=true&expand=user_last_episode_watched'
    )
    assert r.status_code == 200, r.content
    data = parse_obj_as(PageCursor[Series], r.json())
    assert len(data.records) == 2
    assert data.records[0].id == series1.id
    assert data.records[0].user_last_episode_watched.number == 1
    assert data.records[1].id == series2.id
    assert data.records[1].user_last_episode_watched.number == 2


if __name__ == '__main__':
    run_file(__file__)
