import pytest
import sqlalchemy as sa
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models
from seplis.api.database import database


@pytest.mark.asyncio
async def test_play_server_register_episodes(client: AsyncClient):
    user_id = await user_signin(client)

    play_server: schemas.Play_server = await models.Play_server.save(data=schemas.Play_server_create(
        name='Test play',
        url='http://example.net',
        secret='2'*20
    ), user_id=user_id)

    series1: schemas.Series = await models.Series.save(data=schemas.Series_create(
        title='Test 1',
        episodes=[schemas.Episode_create(title='EP', number=1)]
    ))    
    series2: schemas.Series = await models.Series.save(data=schemas.Series_create(
        title='Test 2',
        episodes=[schemas.Episode_create(title='EP2', number=1)]
    ))    

    r = await client.put(f'/2/play-servers/{play_server.id}/episodes', json=[
        {'series_id': series1.id, 'episode_number': 1},
    ], headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_episode))
        assert r.all()[0].series_id == series1.id

    r = await client.patch(f'/2/play-servers/{play_server.id}/episodes', json=[
        {'series_id': series2.id, 'episode_number': 1},
    ], headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_episode).where(
            models.Play_server_episode.play_server_id == play_server.id
        ))
        r = r.all()
        assert r[0].series_id == series1.id
        assert r[1].series_id == series2.id


    r = await client.patch(f'/2/play-servers/{play_server.id}/episodes', json=[
        {'series_id': series2.id, 'episode_number': 1},
    ], headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_episode).where(
            models.Play_server_episode.play_server_id == play_server.id
        ))
        r = r.all()
        assert r[0].series_id == series1.id
        assert r[1].series_id == series2.id

    r = await client.delete(f'/2/play-servers/{play_server.id}/series/{series1.id}/episodes/1', headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_episode).where(
            models.Play_server_episode.play_server_id == play_server.id
        ))
        r = r.all()
        assert r[0].series_id == series2.id

    r = await client.put(f'/2/play-servers/{play_server.id}/episodes', json=[], headers={
        'Authorization': f'Secret {"2"*20}',
    })
    assert r.status_code == 204, r.content

    async with database.session() as session:
        r = await session.scalars(sa.select(models.Play_server_episode).where(
            models.Play_server_episode.play_server_id == play_server.id
        ))
        assert len(r.all()) == 0


if __name__ == '__main__':
    run_file(__file__)