import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models
from pydantic import parse_obj_as


@pytest.mark.asyncio
async def test_episode_play_servers(client: AsyncClient):
    user_id = await user_signin(client, [str(constants.LEVEL_EDIT_USER)])

    movie: schemas.Movie = await models.Movie.save(schemas.Movie_create(
        title='Movie',
    ), movie_id=None)

    play_server = await models.Play_server.save(schemas.Play_server_create(
        name='Test',
        url='http://example.net',
        secret='1'*20,
    ), id_=None, user_id=user_id)

    # Let's get the server that the user has access to
    # with a play id, that we can use when contacting the server.
    r = await client.get(f'/2/movies/{movie.id}/play-servers')
    assert r.status_code, 200
    servers = parse_obj_as(list[schemas.Play_request], r.json())
    assert len(servers) == 1
    assert servers[0].play_url == 'http://example.net'
    assert type(servers[0].play_id) == str


if __name__ == '__main__':
    run_file(__file__)