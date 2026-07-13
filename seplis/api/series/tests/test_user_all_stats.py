import pytest

from seplis.api.series import EpisodeCreate, Series, SeriesCreate, save_series
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin
from seplis.api.user import UserSeriesStats


@pytest.mark.asyncio
async def test_series_user_stats(client: AsyncClient) -> None:
    await user_signin(client)

    series1: Series = await save_series(
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
    series2: Series = await save_series(
        SeriesCreate(
            title='Test series',
            runtime=30,
            episodes=[
                EpisodeCreate(number=1, title='1'),
            ],
        ),
        series_id=None,
    )

    r = await client.get('/2/series/user-stats')
    assert r.status_code == 200
    data = parse_obj_as(UserSeriesStats, r.json())
    assert data.episodes_watched == 0
    assert data.episodes_watched_minutes == 0
    assert data.series_finished == 0
    assert data.series_watched == 0
    assert data.series_watchlist == 0

    await client.put(f'/2/series/{series1.id}/watchlist')
    r = await client.get('/2/series/user-stats')
    assert r.status_code == 200
    data = parse_obj_as(UserSeriesStats, r.json())
    assert data.series_watchlist == 1

    await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    r = await client.get('/2/series/user-stats')
    assert r.status_code == 200
    data = parse_obj_as(UserSeriesStats, r.json())
    assert data.episodes_watched == 1
    assert data.episodes_watched_minutes == 30
    assert data.series_watched == 1
    assert data.series_finished == 0

    await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    r = await client.get('/2/series/user-stats')
    assert r.status_code == 200
    data = parse_obj_as(UserSeriesStats, r.json())
    assert data.episodes_watched == 2
    assert data.episodes_watched_minutes == 60
    assert data.series_watched == 1
    assert data.series_finished == 0

    await client.post(f'/2/series/{series1.id}/episodes/2/watched')
    r = await client.get('/2/series/user-stats')
    assert r.status_code == 200
    data = parse_obj_as(UserSeriesStats, r.json())
    assert data.episodes_watched == 3
    assert data.episodes_watched_minutes == 90
    assert data.series_watched == 1
    assert data.series_finished == 0

    await client.post(f'/2/series/{series1.id}/episodes/3/watched')
    r = await client.get('/2/series/user-stats')
    assert r.status_code == 200
    data = parse_obj_as(UserSeriesStats, r.json())
    assert data.episodes_watched == 4
    assert data.episodes_watched_minutes == 130
    assert data.series_watched == 1
    assert data.series_finished == 1

    await client.post(f'/2/series/{series2.id}/episodes/1/watched')
    r = await client.get('/2/series/user-stats')
    assert r.status_code == 200
    data = parse_obj_as(UserSeriesStats, r.json())
    assert data.episodes_watched == 5
    assert data.episodes_watched_minutes == 160
    assert data.series_watched == 2
    assert data.series_finished == 2


if __name__ == '__main__':
    run_file(__file__)
