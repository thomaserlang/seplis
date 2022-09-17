import pytest
from seplis.api.testbase import client, client_async, run_file
from seplis.api.database import database

def test_health(client):    
    r = client.get('/health')
    assert r.status_code == 200, r.content

def test_health2(client):    
    r = client.get('/health')
    assert r.status_code == 200, r.content

def test_health3(client):    
    r = client.get('/health')
    assert r.status_code == 200, r.content

def test_health4(client):    
    r = client.get('/health')
    assert r.status_code == 200, r.content

@pytest.mark.asyncio
async def test_some_asyncio_code(client_async):
    async with database.session() as session:
        await session.execute('INSERT INTO shows (id) VALUES (1);')
        await session.commit()
    r = await client_async.get('/health')
    assert r.status_code == 200, r.content

@pytest.mark.asyncio
async def test_some_asyncio_code2(client_async):
    async with database.session() as session:
        await session.execute('INSERT INTO shows (id) VALUES (1);')
        await session.commit()
    r = await client_async.get('/health')
    assert r.status_code == 200, r.content

if __name__ == '__main__':
    run_file(__file__)