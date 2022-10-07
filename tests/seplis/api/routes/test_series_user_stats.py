import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_series(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_EDIT_USER)])

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1),
            schemas.Episode_create(number=2),
            schemas.Episode_create(number=3, runtime=40),
        ]
    ), series_id=None)

    r = await client.get(f'/1/series/{series.id}')
    assert r.status_code == 200
    data = schemas.Series_user_stats.parse_obj(r.json())
    assert data.episodes_watched == 0
    assert data.episodes_watched_minutes == 0

    # TODO: add more tests when series episode watched has been implemented

if __name__ == '__main__':
    run_file(__file__)