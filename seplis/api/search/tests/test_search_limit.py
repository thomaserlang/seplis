from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from seplis.api.search.actions.search_actions import search_titles
from seplis.api.search.router import router


@pytest.mark.asyncio
async def test_search_passes_limit_to_elasticsearch() -> None:
    with patch(
        'seplis.api.search.actions.search_actions.database',
    ) as database:
        search = AsyncMock(return_value={'hits': {'hits': []}})
        database.es.search = search
        assert await search_titles('treasure', None, None, limit=60) == []
        assert search.call_args.kwargs['size'] == 60


@pytest.mark.asyncio
async def test_search_limit_defaults_and_validation() -> None:
    app = FastAPI()
    app.include_router(router)
    with patch(
        'seplis.api.search.router.search_titles', new_callable=AsyncMock, return_value=[]
    ) as search:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url='http://test'
        ) as client:
            response = await client.get('/search', params={'query': 'treasure'})
            assert response.status_code == 200
            assert search.call_args.kwargs['limit'] == 10
            response = await client.get(
                '/search', params={'query': 'treasure', 'limit': 60}
            )
            assert response.status_code == 200
            assert search.call_args.kwargs['limit'] == 60
            for limit in [0, 101]:
                response = await client.get(
                    '/search', params={'query': 'treasure', 'limit': limit}
                )
                assert response.status_code == 422
            assert search.await_count == 2
