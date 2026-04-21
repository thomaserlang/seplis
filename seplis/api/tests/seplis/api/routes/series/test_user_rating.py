import pytest

from seplis.api import models, schemas
from seplis.api.testbase import AsyncClient, run_file, user_signin


@pytest.mark.asyncio
async def test_series_user_rating(client: AsyncClient) -> None:
    await user_signin(client)

    series: schemas.Series = await models.MSeries.save(
        schemas.Series_create(
            title='Test series',
        ),
        series_id=None,
    )

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = schemas.Series_user_rating.model_validate(r.json())
    assert data.rating is None

    r = await client.put(f'/2/series/{series.id}/user-rating', json={'rating': 5})
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = schemas.Series_user_rating.model_validate(r.json())
    assert data.rating == 5

    r = await client.put(f'/2/series/{series.id}/user-rating', json={'rating': 7})
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = schemas.Series_user_rating.model_validate(r.json())
    assert data.rating == 7

    r = await client.delete(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = schemas.Series_user_rating.model_validate(r.json())
    assert data.rating is None


if __name__ == '__main__':
    run_file(__file__)
