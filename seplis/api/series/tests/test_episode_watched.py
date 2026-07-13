import pytest

from seplis.api.series import (
    EpisodeCreate,
    EpisodeWatched,
    Series,
    SeriesCreate,
    save_series,
)
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_episode_watched(client: AsyncClient) -> None:
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

    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    data = parse_obj_as(EpisodeWatched, r.json())
    assert data.times == 2
    assert data.position == 0
    assert data.watched_at is not None

    r = await client.get(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    data = parse_obj_as(EpisodeWatched, r.json())
    assert data.times == 2
    assert data.position == 0
    assert data.watched_at is not None

    r = await client.delete(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    data = parse_obj_as(EpisodeWatched, r.json())
    assert data.times == 1
    assert data.position == 0
    assert data.watched_at is not None

    r = await client.delete(f'/2/series/{series.id}/episodes/1/watched')
    data = parse_obj_as(EpisodeWatched, r.json())
    assert data.times == 0
    assert data.position == 0
    assert data.watched_at is None

    r = await client.get(f'/2/series/{series.id}/episodes/1/watched')
    data = parse_obj_as(EpisodeWatched, r.json())
    assert data.times == 0
    assert data.position == 0
    assert data.watched_at is None

    r = await client.post(
        f'/2/series/{series.id}/episodes/watched-range',
        json={
            'from_episode_number': 1,
            'to_episode_number': 3,
        },
    )
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    data = parse_obj_as(EpisodeWatched, r.json())
    assert data.times == 1

    r = await client.get(f'/2/series/{series.id}/episodes/2/watched')
    assert r.status_code == 200, r.content
    data = parse_obj_as(EpisodeWatched, r.json())
    assert data.times == 1

    r = await client.get(f'/2/series/{series.id}/episodes/3/watched')
    assert r.status_code == 200, r.content
    data = parse_obj_as(EpisodeWatched, r.json())
    assert data.times == 1


if __name__ == '__main__':
    run_file(__file__)
