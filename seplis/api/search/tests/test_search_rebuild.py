from typing import Literal

import pytest

from seplis import config
from seplis.api import movie as movie_module
from seplis.api.database import database
from seplis.api.movie import MovieCreate, save_movie
from seplis.api.movie.actions.movie_actions import delete_movie
from seplis.api.search import SearchTitleDocument
from seplis.api.search.actions.search_actions import search_titles
from seplis.api.search.actions.search_index_actions import redis_key, write_documents
from seplis.api.search.actions.search_mapping import index_document
from seplis.api.search.actions.search_rebuild_actions import rebuild_search
from seplis.api.series import SeriesCreate, save_series

pytestmark = pytest.mark.asyncio


async def lookup(title: str) -> list[SearchTitleDocument]:
    return await search_titles(query=None, title=title, title_type=None)


@pytest.mark.parametrize('additions', [1, 101])
async def test_rebuild_preserves_live_changes(
    db: None, monkeypatch: pytest.MonkeyPatch, additions: int
) -> None:
    renamed = await save_movie(MovieCreate(title='Before rebuild'))
    removed = await save_movie(MovieCreate(title='Remove during rebuild'))
    await save_series(SeriesCreate(title='Series survives'))
    stale = index_document(SearchTitleDocument(type='movie', id=999999, title='Stale'))
    await write_documents([stale])
    real_rebuild = movie_module.rebuild_movies

    async def rebuild_with_changes(collection: str | None = None) -> None:
        await real_rebuild(collection=collection)
        await save_movie({'title': 'Intermediate name'}, movie_id=renamed.id)
        await save_movie({'title': 'After rebuild'}, movie_id=renamed.id)
        await delete_movie(movie_id=removed.id)
        for i in range(additions):
            await save_movie(MovieCreate(title=f'Added during rebuild {i}'))
        # The old index continues serving while the replacement is being built.
        assert await lookup('Stale')
        assert await lookup('After rebuild')

    monkeypatch.setattr(movie_module, 'rebuild_movies', rebuild_with_changes)
    await rebuild_search()
    assert await lookup('Before rebuild') == []
    assert await lookup('Intermediate name') == []
    assert await lookup('Remove during rebuild') == []
    assert await lookup('Stale') == []
    for title in [
        'After rebuild',
        f'Added during rebuild {additions - 1}',
        'Series survives',
    ]:
        assert await lookup(title), title
    assert not await database.redis.exists(redis_key('building'))
    assert not await database.redis.exists(redis_key('changes'))


@pytest.mark.parametrize('failure', ['import', 'journal'])
async def test_failed_rebuild_keeps_live_index(
    db: None, monkeypatch: pytest.MonkeyPatch, failure: Literal['import', 'journal']
) -> None:
    await save_movie(MovieCreate(title='Still available'))
    alias = f'/aliases/{config.api.typesense.collection}'
    before = (await database.search.get(alias)).json()

    async def fail(collection: str | None = None) -> None:
        if failure == 'import':
            raise RuntimeError('broken import')
        await database.redis.delete(redis_key('building'))

    monkeypatch.setattr(movie_module, 'rebuild_movies', fail)
    with pytest.raises(RuntimeError, match='broken import|journal was lost'):
        await rebuild_search()
    assert (await database.search.get(alias)).json() == before
    assert await lookup('Still available')
    assert not await database.redis.exists(redis_key('building'))


async def test_cache_rebuild_preserves_jobs(db: None) -> None:
    from seplis.api.rebuild_cache import rebuild

    job = await database.redis_queue.enqueue_job('update_movie', 123)
    assert job is not None
    job_key = f'arq:job:{job.job_id}'
    await database.redis.set('seplis:tokens:stale:user', 'expired')
    assert await database.redis.exists(job_key)
    await rebuild()
    assert await database.redis.exists(job_key)
    assert not await database.redis.exists('seplis:tokens:stale:user')
