import pytest

from seplis.api import models, schemas
from seplis.api.testbase import AsyncClient, run_file, user_signin
from seplis.api.user import UserSeriesSettings


@pytest.mark.asyncio
async def test_user_series_settings(client: AsyncClient) -> None:
    await user_signin(client)

    series: schemas.Series = await models.MSeries.save(
        schemas.Series_create(
            title='Test series',
        ),
        series_id=None,
    )

    url = f'/2/series/{series.id}/user-settings'
    r = await client.get(url)
    assert r.status_code == 200
    data = UserSeriesSettings.model_validate(r.json())
    assert data.subtitle_lang is None
    assert data.audio_lang is None

    r = await client.put(
        url,
        json={
            'subtitle_lang': 'eng',
            'audio_lang': 'jpn',
        },
    )
    assert r.status_code == 200
    data = UserSeriesSettings.model_validate(r.json())
    assert data.subtitle_lang == 'eng'
    assert data.audio_lang == 'jpn'

    r = await client.get(url)
    assert r.status_code == 200
    data = UserSeriesSettings.model_validate(r.json())
    assert data.subtitle_lang == 'eng'
    assert data.audio_lang == 'jpn'

    r = await client.put(
        url,
        json={
            'subtitle_lang': 'eng',
        },
    )
    assert r.status_code == 200
    data = UserSeriesSettings.model_validate(r.json())
    assert data.subtitle_lang == 'eng'
    assert data.audio_lang == 'jpn'


if __name__ == '__main__':
    run_file(__file__)
