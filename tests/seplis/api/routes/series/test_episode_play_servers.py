import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin, parse_obj_as
from seplis.api import constants, schemas, models


@pytest.mark.asyncio
async def test_episode_play_servers(client: AsyncClient):
    user_id = await user_signin(client)

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1, title='1'),
        ]
    ), series_id=None)

    play_server = await models.Play_server.save(schemas.Play_server_create(
        name='Test',
        url='http://example.net',
        secret='1'*20,
    ), play_server_id=None, user_id=user_id)

    await models.Play_server_episode.save(
        play_server_id=play_server.id,
        play_server_secret='1'*20,
        data=[
            schemas.Play_server_episode_create(
                series_id=series.id,
                episode_number=1,
            ),
            schemas.Play_server_episode_create(
                series_id=series.id,
                episode_number=2,
            ),
        ]
    )

    # Let's get the server that the user has access to
    # with a play id, that we can use when contacting the server.
    r = await client.get(f'/2/series/{series.id}/episodes/1/play-servers')
    assert r.status_code, 200
    servers = parse_obj_as (list[schemas.Play_request], r.json())
    assert len(servers) == 1
    assert servers[0].play_url == 'http://example.net'
    assert type(servers[0].play_id) == str


if __name__ == '__main__':
    run_file(__file__)