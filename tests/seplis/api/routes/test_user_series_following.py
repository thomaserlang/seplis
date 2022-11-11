import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models
from seplis import logger

@pytest.mark.asyncio
async def test_user_series_following(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    series1: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
    ), series_id=None)
    series2: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series 2',
    ), series_id=None)

    r = await client.put(f'/2/series/{series1.id}/following')
    assert r.status_code == 204

    r = await client.get(f'/2/users/me/series-following')
    assert r.status_code == 200
    data = schemas.Page_result[schemas.Series_user].parse_obj(r.json())
    assert data.total == 1, data
    assert data.items[0].series.id == series1.id

    r = await client.put(f'/2/series/{series2.id}/following')
    assert r.status_code == 204

    r = await client.get(f'/2/users/me/series-following?per_page=1&sort=followed_at_asc')
    assert r.status_code == 200, r.content
    data = schemas.Page_result[schemas.Series_user].parse_obj(r.json())
    assert data.total == 2, data
    assert data.items[0].series.id == series1.id

    r = await client.get(f'/2/users/me/series-following?page=2&per_page=1&sort=followed_at_asc')
    assert r.status_code == 200
    data = schemas.Page_result[schemas.Series_user].parse_obj(r.json())
    assert data.total == 2, data
    assert data.items[0].series.id == series2.id


if __name__ == '__main__':
    run_file(__file__)