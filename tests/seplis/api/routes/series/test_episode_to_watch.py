import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import constants, schemas, models

@pytest.mark.asyncio
async def test_episode_to_watch(client: AsyncClient):
    await user_signin(client)

    series: schemas.Series = await models.Series.save(schemas.Series_create(
        title='Test series',
        runtime=30,
        episodes=[
            schemas.Episode_create(number=1, title='1'),
            schemas.Episode_create(number=2, title='2'),
            schemas.Episode_create(number=3, title='3', runtime=40),
        ]
    ), series_id=None)


    # without having watched anything we should get
    # the first episode.
    next_to_watch_url = f'/2/series/{series.id}/episode-to-watch'
    r = await client.get(next_to_watch_url)
    assert r.status_code == 200, r.content
    ntw = schemas.Episode.model_validate(r.json())
    assert ntw.number == 1
    assert ntw.user_watched.times == 0
    assert ntw.user_watched.position == 0

    # set episode 1 as watching
    r = await client.put(
        f'/2/series/{series.id}/episodes/1/watched-position', 
        json={'position': 200}
    )
    assert r.status_code == 204

    # next to watch should be episode 1 at position 200
    r = await client.get(next_to_watch_url)
    ntw = schemas.Episode.model_validate(r.json())
    assert ntw.number == 1
    assert ntw.user_watched.position == 200

    # complete episode 1
    r = await client.post(f'/2/series/{series.id}/episodes/1/watched')
    assert r.status_code, 200

    # next to watch should be episode 2
    r = await client.get(next_to_watch_url)
    ntw = schemas.Episode.model_validate(r.json())
    assert ntw.number == 2
    assert ntw.user_watched.times == 0
    assert ntw.user_watched.position == 0


    r = await client.post(f'/2/series/{series.id}/episodes/3/watched')
    assert r.status_code, 200

    r = await client.put(f'/2/series/{series.id}/episodes/3/watched-position', 
        json={'position': 200}
    )
    assert r.status_code == 204
    r = await client.get(next_to_watch_url)
    ntw = schemas.Episode.model_validate(r.json())
    assert ntw.number == 3
    assert ntw.user_watched.times == 1
    assert ntw.user_watched.position == 200

    r = await client.delete(f'/2/series/{series.id}/episodes/3/watched')
    assert r.status_code == 200
    w = schemas.Episode_watched.model_validate(r.json())
    assert w.times == 1
    assert w.position == 0

    r = await client.get(next_to_watch_url)
    assert r.status_code == 204

    r = await client.get(f'/2/series/{series.id}/episode-last-watched')
    assert r.status_code == 200
    ntw = schemas.Episode.model_validate(r.json())
    assert ntw.number == 3

    
    r = await client.post(f'/2/series/{series.id}/episodes/watched-range', json={
        'from_episode_number': 1,
        'to_episode_number': 3,
    })
    assert r.status_code == 204
    
    r = await client.get(next_to_watch_url)
    assert r.status_code == 204


if __name__ == '__main__':
    run_file(__file__)