import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models

@pytest.mark.asyncio
async def test_episode_last_watched(client: AsyncClient):
    await user_signin(client, [str(constants.LEVEL_USER)])

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1, title='1'),
            schemas.Episode_create(number=2, title='2'),
        ]
    ), series_id=None)


    # Test no watched episodes
    r = await client.get(f'/2/series/{series.id}/episode-last-watched')
    assert r.status_code == 204, r.content

    # set episode 1 as watching
    r = await client.put(f'/2/series/{series.id}/episodes/1/watched-position', 
        json={'position': 200}
    )
    assert r.status_code == 204

    # Since we have not completed the first episode 
    # and it's the only episode we have watched the result
    # should be empty 
    r = await client.get(f'/2/series/{series.id}/episode-last-watched')
    assert r.status_code == 204, r.content


    # Start watching episode 2.
    # Episode 1 should now be the latest watched even though it 
    # is not completed.
    r = await client.put(f'/2/series/{series.id}/episodes/2/watched-position', 
        json={'position': 202}
    )
    assert r.status_code == 204
    r = await client.get(f'/2/series/{series.id}/episode-last-watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode.parse_obj(r.json())
    assert data.number == 1
    assert data.user_watched.position == 200
    assert data.user_watched.times == 0

    # Set episode 2 as completed.
    # Episode 2 should now be the last watched
    r = await client.post(f'/2/series/{series.id}/episodes/2/watched')
    assert r.status_code == 200
    r = await client.get(f'/2/series/{series.id}/episode-last-watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode.parse_obj(r.json())
    assert data.number == 2
    assert data.user_watched.position == 0
    assert data.user_watched.times == 1


    # set episode 1 as watched
    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    # unwatch episode 2
    r = await client.delete(f'/2/series/{series.id}/episodes/2/watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode_watched.parse_obj(r.json())
    assert data.position == 0
    assert data.times == 0
    # episode 1 should now be the last watched
    r = await client.get(f'/2/series/{series.id}/episode-last-watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode.parse_obj(r.json())
    assert data.number, 1

    # watch episode 2 twice
    r = await client.post(f'/2/series/{series.id}/episodes/2/watched')
    assert r.status_code == 200
    r = await client.post(f'/2/series/{series.id}/episodes/2/watched')
    assert r.status_code == 200
    r = await client.get(f'/2/series/{series.id}/episode-last-watched')
    assert r.status_code == 200, r.content
    data = schemas.Episode.parse_obj(r.json())
    assert data.number == 2
    assert data.user_watched.position == 0


if __name__ == '__main__':
    run_file(__file__)