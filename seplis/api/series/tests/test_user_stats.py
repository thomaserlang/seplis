from datetime import UTC, datetime, timedelta

import pytest

from seplis.api.series import (
    EpisodeCreate,
    Series,
    SeriesCreate,
    SeriesUserStats,
    save_series,
)
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_series_user_stats(client: AsyncClient) -> None:
    await user_signin(client)

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

    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code == 200
    data = parse_obj_as(SeriesUserStats, r.json())
    assert data.episode_watch_count == 0
    assert data.total_watch_minutes == 0

    # watched time
    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200
    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code, 200
    data = parse_obj_as(SeriesUserStats, r.json())
    assert data.episode_watch_count == 1, data
    assert data.total_watch_minutes == 30, data

    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code, 200
    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code, 200
    data = parse_obj_as(SeriesUserStats, r.json())
    assert data.episode_watch_count == 2, data
    assert data.total_watch_minutes == 60, data

    r = await client.post(f'/2/series/{series.id}/episodes/2/watched')
    assert r.status_code, 200
    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code, 200
    data = parse_obj_as(SeriesUserStats, r.json())
    assert data.episode_watch_count == 3, data
    assert data.total_watch_minutes == 90, data

    r = await client.post(f'/2/series/{series.id}/episodes/3/watched')
    assert r.status_code, 200
    r = await client.get(f'/2/series/{series.id}/user-stats')
    assert r.status_code, 200
    data = parse_obj_as(SeriesUserStats, r.json())
    assert data.episode_watch_count == 4, data
    assert data.total_watch_minutes == 130, data


@pytest.mark.asyncio
async def test_episode_progress_counts_all_episodes(client: AsyncClient) -> None:
    await user_signin(client)
    now = datetime.now(UTC)
    series = await save_series(
        SeriesCreate(
            title='Progress',
            episodes=[
                EpisodeCreate(
                    number=1, title='1', air_date=now.date() - timedelta(days=1)
                ),
                EpisodeCreate(number=2, title='2', air_datetime=now - timedelta(days=1)),
                EpisodeCreate(
                    number=3, title='3', air_date=now.date() + timedelta(days=1)
                ),
                EpisodeCreate(number=4, title='4'),
                EpisodeCreate(
                    number=5,
                    title='5',
                    air_date=now.date(),
                    air_datetime=now + timedelta(hours=1),
                ),
            ],
        ),
        series_id=None,
    )
    url = f'/2/series/{series.id}/user-stats'
    response = await client.get(url)
    assert response.status_code == 200
    assert response.json()['total_episodes'] == 5
    assert response.json()['episodes_watched'] == 0

    for number in [1, 1, 3, 4, 5]:
        response = await client.post(f'/2/series/{series.id}/episodes/{number}/watched')
        assert response.status_code == 200
    response = await client.get(url)
    assert response.json()['episodes_watched'] == 4
    assert response.json()['episode_watch_count'] == 5

    await client.post(f'/2/series/{series.id}/episodes/2/watched')
    response = await client.get(url)
    assert response.json()['episodes_watched'] == 5
    await client.delete(f'/2/series/{series.id}/episodes/2/watched')
    response = await client.get(url)
    assert response.json()['episodes_watched'] == 4


@pytest.mark.asyncio
async def test_progress_without_episodes(client: AsyncClient) -> None:
    await user_signin(client)
    series = await save_series(SeriesCreate(title='Empty'), series_id=None)
    response = await client.get(f'/2/series/{series.id}/user-stats')
    assert response.status_code == 200
    assert response.json()['total_episodes'] == 0
    assert response.json()['episodes_watched'] == 0


if __name__ == '__main__':
    run_file(__file__)
