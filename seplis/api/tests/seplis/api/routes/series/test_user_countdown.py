from datetime import UTC, datetime, timedelta

import pytest

from seplis.api import models, schemas
from seplis.api.testbase import AsyncClient, run_file, user_signin


@pytest.mark.asyncio
async def test_user_series_watchlist(client: AsyncClient) -> None:
    await user_signin(client)
    dt = datetime.now(tz=UTC)
    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=dt-timedelta(days=1)),
            schemas.Episode_create(title='Episode 2', number=2, air_datetime=dt),
            schemas.Episode_create(title='Episode 3', number=3, air_datetime=dt+timedelta(days=1)),
        ]
    ), series_id=None)
    await models.Series.save(schemas.Series_create(
        title='Test series 2',
        episodes=[
            schemas.Episode_create(title='Episode 1', number=1, air_datetime=dt-timedelta(days=1)),
            schemas.Episode_create(title='Episode 2', number=2, air_datetime=dt),
            schemas.Episode_create(title='Episode 3', number=3, air_datetime=dt+timedelta(days=1)),
        ]
    ), series_id=None)

    r = await client.get('/2/series/countdown')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series_and_episode].model_validate(r.json())
    assert len(data.items) == 0

    r = await client.put(f'/2/series/{series1.id}/watchlist')
    assert r.status_code == 204, r.content
    
    r = await client.get('/2/series/countdown')
    assert r.status_code == 200
    data = schemas.Page_cursor_result[schemas.Series_and_episode].model_validate(r.json())
    assert data.items[0].series.title == 'Test series'
    assert data.items[0].episode.number == 3


if __name__ == '__main__':
    run_file(__file__)