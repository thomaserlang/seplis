from urllib import response
import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_user_series_settings(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
    ), series_id=None)

    url = f'/2/series/{series.id}/user-settings'
    r = await client.get(url)
    assert r.status_code == 200
    data = schemas.User_series_settings.parse_obj(r.json())
    assert data.subtitle_lang == None
    assert data.audio_lang == None

    r = await client.put(url, json={
        'subtitle_lang': 'eng',
        'audio_lang': 'jpn',
    })
    assert r.status_code == 200
    data = schemas.User_series_settings.parse_obj(r.json())
    assert data.subtitle_lang == 'eng'
    assert data.audio_lang == 'jpn'

    r = await client.get(url)
    assert r.status_code == 200
    data = schemas.User_series_settings.parse_obj(r.json())
    assert data.subtitle_lang == 'eng'
    assert data.audio_lang == 'jpn'


if __name__ == '__main__':
    run_file(__file__)