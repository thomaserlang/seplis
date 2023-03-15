import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models

@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore:Duplicate")
async def test_series_favorite(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
    ), series_id=None)

    r = await client.get(f'/2/series/{series.id}/favorite')
    assert r.status_code == 200
    f = schemas.Series_favorite.parse_obj(r.json())
    assert f.favorite == False
    assert f.created_at == None


    r = await client.put(f'/2/series/{series.id}/favorite')
    assert r.status_code == 204

    # Test handling duplicate
    r = await client.put(f'/2/series/{series.id}/favorite')
    assert r.status_code == 204


    r = await client.get(f'/2/series/{series.id}/favorite')
    assert r.status_code == 200
    f = schemas.Series_favorite.parse_obj(r.json())
    assert f.favorite == True
    assert f.created_at != None


    r = await client.delete(f'/2/series/{series.id}/favorite')
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/favorite')
    assert r.status_code == 200
    f = schemas.Series_favorite.parse_obj(r.json())
    assert f.favorite == False
    assert f.created_at == None


if __name__ == '__main__':
    run_file(__file__)