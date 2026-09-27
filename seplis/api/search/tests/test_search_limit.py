from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response

from seplis.api.search.actions.search_actions import search_titles
from seplis.api.search.router import router


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('query', 'title'),
    [
        ('treasure', None),
        ('treasure (2020)', None),
        (None, 'treasure'),
        (None, 'treasure (2020)'),
        ('tt1234567', None),
    ],
)
async def test_search_passes_limit_to_typesense(
    query: str | None, title: str | None
) -> None:
    with patch(
        'seplis.api.search.actions.search_actions.request',
        new_callable=AsyncMock,
        return_value=Response(200, json={'hits': []}),
    ) as request:
        assert await search_titles(query, title, None, limit=60) == []
        assert request.await_count > 0
        assert all(
            call.kwargs['params']['per_page'] == 60
            for call in request.await_args_list
        )


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
            assert search.call_args.kwargs['limit'] == 25
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
