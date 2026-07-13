from datetime import UTC, datetime, timedelta

import pytest

from seplis.api.page_cursor import PageCursor
from seplis.api.series import (
    EpisodeCreate,
    Series,
    SeriesAndEpisode,
    SeriesCreate,
    save_series,
)
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_user_series_to_watch(client: AsyncClient) -> None:
    await user_signin(client)
    dt = datetime.now(tz=UTC)
    series1: Series = await save_series(
        SeriesCreate(
            title='Test series',
            episodes=[
                EpisodeCreate(
                    title='Episode 1', number=1, air_datetime=dt - timedelta(days=2)
                ),
                EpisodeCreate(title='Episode 2', number=2, air_datetime=dt),
                EpisodeCreate(
                    title='Episode 3', number=3, air_datetime=dt + timedelta(days=1)
                ),
            ],
        ),
        series_id=None,
    )
    series2: Series = await save_series(
        SeriesCreate(
            title='Test series 2',
            episodes=[
                EpisodeCreate(
                    title='Episode 1', number=1, air_datetime=dt - timedelta(days=1)
                ),
                EpisodeCreate(title='Episode 2', number=2, air_datetime=dt),
                EpisodeCreate(
                    title='Episode 3', number=3, air_datetime=dt + timedelta(days=1)
                ),
            ],
        ),
        series_id=None,
    )

    r = await client.get('/2/series/to-watch')
    assert r.status_code == 200, r.content
    data = parse_obj_as(PageCursor[SeriesAndEpisode], r.json())
    assert len(data.records) == 0

    r = await client.put(f'/2/series/{series1.id}/watchlist')
    assert r.status_code == 204, r.content
    r = await client.put(f'/2/series/{series2.id}/watchlist')
    assert r.status_code == 204, r.content

    r = await client.post(f'/2/series/{series1.id}/episodes/1/watched')
    assert r.status_code == 200, r.content
    r = await client.post(f'/2/series/{series2.id}/episodes/2/watched')
    assert r.status_code == 200, r.content

    r = await client.get('/2/series/to-watch')
    assert r.status_code == 200
    data = parse_obj_as(PageCursor[SeriesAndEpisode], r.json())
    assert data.records[0].series.title == 'Test series'
    assert data.records[0].episode.number == 2


if __name__ == '__main__':
    run_file(__file__)
