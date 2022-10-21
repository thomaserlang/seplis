import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_series_user_rating(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_EDIT_USER)])

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
    ), series_id=None)

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = schemas.Series_user_rating.parse_obj(r.json())
    assert data.rating == None

    r = await client.put(f'/2/series/{series.id}/user-rating', json={
        'rating': 5
    })
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = schemas.Series_user_rating.parse_obj(r.json())
    assert data.rating == 5

    r = await client.put(f'/2/series/{series.id}/user-rating', json={
        'rating': 7
    })
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = schemas.Series_user_rating.parse_obj(r.json())
    assert data.rating == 7

    r = await client.delete(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/user-rating')
    assert r.status_code == 200
    data = schemas.Series_user_rating.parse_obj(r.json())
    assert data.rating == None


if __name__ == '__main__':
    run_file(__file__)