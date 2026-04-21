import pytest

from seplis.api import models, schemas
from seplis.api.testbase import AsyncClient, run_file, user_signin


@pytest.mark.asyncio
@pytest.mark.filterwarnings('ignore:Duplicate')
async def test_series_watchlist(client: AsyncClient) -> None:
    await user_signin(client)

    series: schemas.Series = await models.MSeries.save(
        schemas.Series_create(
            title='Test series',
        ),
        series_id=None,
    )

    r = await client.get(f'/2/series/{series.id}/watchlist')
    assert r.status_code == 200
    f = schemas.Series_watchlist.model_validate(r.json())
    assert not f.on_watchlist
    assert f.created_at is None

    r = await client.put(f'/2/series/{series.id}/watchlist')
    assert r.status_code == 204

    # Test handling duplicate
    r = await client.put(f'/2/series/{series.id}/watchlist')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/watchlist')
    assert r.status_code == 200
    f = schemas.Series_watchlist.model_validate(r.json())
    assert f.on_watchlist
    assert f.created_at is not None

    r = await client.delete(f'/2/series/{series.id}/watchlist')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/watchlist')
    assert r.status_code == 200
    f = schemas.Series_watchlist.model_validate(r.json())
    assert not f.on_watchlist
    assert f.created_at is None


if __name__ == '__main__':
    run_file(__file__)
