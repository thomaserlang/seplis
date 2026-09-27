import re
from typing import Any, Literal

from pydantic import TypeAdapter

from seplis import config
from seplis.api.exceptions import SearchException

from ..schemas.search_schemas import SearchTitleDocument
from .search_index_actions import request
from .search_mapping import name_keys, normalize_name

TitleType = Literal['series', 'movie']
YEAR = r'(18\d{2}|19\d{2}|20\d{2})'
DOCUMENT = TypeAdapter(SearchTitleDocument)


async def search(
    params: dict[str, Any], filters: list[str], limit: int = 10
) -> list[SearchTitleDocument]:
    response = await request(
        'GET',
        f'/collections/{config.api.typesense.collection}/documents/search',
        params={
            'q': '*',
            'per_page': limit,
            'sort_by': 'popularity:desc',
            'include_fields': 'payload',
            **params,
            'filter_by': ' && '.join(filters),
        },
    )
    return [
        DOCUMENT.validate_json(h['document']['payload']) for h in response.json()['hits']
    ]


async def exact_names(
    title: str, filters: list[str], limit: int = 10
) -> list[SearchTitleDocument]:
    keys = name_keys(title)
    if not keys:
        return []
    for field in ('primary_keys', 'name_keys'):
        result = await search({}, [*filters, f'{field}:=[{",".join(keys)}]'], limit)
        if result:
            return result
    return []


async def identify(
    title: str, filters: list[str], limit: int = 10
) -> list[SearchTitleDocument]:
    match = re.fullmatch(rf'(.+?)\s+\({YEAR}\)', title)
    if match:
        return await exact_names(match[1], [*filters, f'year:={match[2]}'], limit)
    # A trailing number may be part of the actual title (Blade Runner 2049).
    literal = await exact_names(title, filters, limit)
    if literal:
        return literal
    match = re.fullmatch(rf'(.+?)[\s._-]+{YEAR}', title)
    if match:
        return await exact_names(match[1], [*filters, f'year:={match[2]}'], limit)
    return []


async def interactive(
    query: str, filters: list[str], limit: int = 10
) -> list[SearchTitleDocument]:
    params = {
        'query_by': 'title,aliases',
        'query_by_weights': '2,1',
        'sort_by': '_text_match:desc,popularity:desc',
        'drop_tokens_threshold': 0,
        'enable_typos_for_numerical_tokens': 'false',
        'min_len_1typo': 3,
        'max_candidates': 64,
        'typo_tokens_threshold': 10,
        'split_join_tokens': 'always',
    }
    explicit = re.fullmatch(rf'(.+?)\s+\({YEAR}\)', query)
    if explicit:
        text = normalize_name(explicit[1])
        if not text:
            return []
        return await search(
            {**params, 'q': text}, [*filters, f'year:={explicit[2]}'], limit
        )
    text = normalize_name(query)
    if not text:
        return []
    match = re.fullmatch(rf'(.+?)[\s._-]+{YEAR}', query)
    if match and normalize_name(match[1]):
        literal = await search(
            {}, [*filters, f'primary_keys:=[{",".join(name_keys(query))}]'], limit
        )
        if not literal:
            result = await search(
                {**params, 'q': normalize_name(match[1])},
                [*filters, f'year:={match[2]}'],
                limit,
            )
            if result:
                return result
    return await search({**params, 'q': text}, filters, limit)


async def search_titles(
    query: str | None,
    title: str | None,
    title_type: TitleType | None,
    limit: int = 10,
) -> list[SearchTitleDocument]:
    value = (query or title or '').strip()
    if not query and not title:
        raise SearchException(message='No query')
    if not value:
        return []
    filters = [f'type:={title_type}'] if title_type else []
    if re.fullmatch(r'tt\d+', value, re.IGNORECASE):
        return await search({}, [*filters, f'imdb:={value.lower()}'], limit)
    if query:
        return await interactive(value, filters, limit)
    return await identify(value, filters, limit)
