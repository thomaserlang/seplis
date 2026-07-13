import pytest

from seplis.api.play_server import (
    PlayRequest,
    PlayServerCreate,
    PlayServerEpisodeCreate,
    register_play_server_episodes,
    save_play_server,
)
from seplis.api.series import EpisodeCreate, Series, SeriesCreate, save_series
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_episode_play_servers(client: AsyncClient) -> None:
    user_id = await user_signin(client)

    series: Series = await save_series(
        SeriesCreate(
            title='Test series',
            runtime=30,
            episodes=[
                EpisodeCreate(number=1, title='1'),
            ],
        ),
        series_id=None,
    )

    play_server = await save_play_server(
        PlayServerCreate(
            name='Test',
            url='http://example.net',
            secret='1' * 32,
        ),
        play_server_id=None,
        user_id=user_id,
    )

    await register_play_server_episodes(
        play_server_id=play_server.id,
        secret='1' * 32,
        patch=True,
        data=[
            PlayServerEpisodeCreate(
                series_id=series.id,
                episode_number=1,
            ),
            PlayServerEpisodeCreate(
                series_id=series.id,
                episode_number=2,
            ),
        ],
    )

    # Let's get the server that the user has access to
    # with a play id, that we can use when contacting the server.
    r = await client.get(f'/2/series/{series.id}/episodes/1/play-servers')
    assert r.status_code, 200
    servers = parse_obj_as(list[PlayRequest], r.json())
    assert len(servers) == 1
    assert servers[0].play_url == 'http://example.net'
    assert isinstance(servers[0].play_id, str)


if __name__ == '__main__':
    run_file(__file__)
