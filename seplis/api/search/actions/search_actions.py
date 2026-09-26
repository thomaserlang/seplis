from typing import Any, Literal

from pydantic import TypeAdapter

from seplis import config
from seplis.api import exceptions
from seplis.api.database import database

from ..schemas.search_schemas import SearchTitleDocument

_search_title_document_adapter = TypeAdapter(SearchTitleDocument)


async def search_titles(
    query: str | None,
    title: str | None,
    title_type: Literal['series', 'movie'] | None,
) -> list[SearchTitleDocument]:
    if query:
        elastic_query = get_by_query(query)
    elif title:
        elastic_query = get_by_title(title)
    else:
        raise exceptions.ElasticsearchException(message='No query')

    if title_type:
        elastic_query = {
            'bool': {
                'must': elastic_query,
                'filter': {
                    'term': {
                        'type': title_type,
                    }
                },
            }
        }

    result = await database.es.search(
        index=config.api.elasticsearch.index_prefix + 'titles', query=elastic_query
    )
    return [
        _search_title_document_adapter.validate_python(hit['_source'])
        for hit in result['hits']['hits']
    ]


def get_by_query(title: str) -> dict[str, Any]:
    return {
        'function_score': {
            'query': {
                'dis_max': {
                    'queries': [
                        {
                            'nested': {
                                'path': 'titles',
                                'score_mode': 'max',
                                'query': {
                                    'bool': {
                                        'should': [
                                            {
                                                'multi_match': {
                                                    'query': title,
                                                    'type': 'bool_prefix',
                                                    'operator': 'and',
                                                    'fuzziness': 'auto',
                                                    'fields': [
                                                        'titles.title',
                                                        'titles.title._2gram',
                                                        'titles.title._3gram',
                                                    ],
                                                },
                                            },
                                            {
                                                'term': {
                                                    'titles.title.exact': {
                                                        'value': title,
                                                        'boost': 2,
                                                    }
                                                }
                                            },
                                        ]
                                    }
                                },
                            }
                        },
                        {'term': {'imdb': title}},
                    ]
                }
            },
            'field_value_factor': {
                'field': 'popularity',
                'modifier': 'log1p',
                'factor': 2,
                'missing': 0,
            },
        }
    }


def get_by_title(title: str) -> dict[str, Any]:
    return {
        'function_score': {
            'query': {
                'dis_max': {
                    'queries': [
                        {
                            'nested': {
                                'path': 'titles',
                                'score_mode': 'max',
                                'query': {
                                    'bool': {
                                        'should': [
                                            {
                                                'match_phrase': {
                                                    'titles.title': {
                                                        'query': title,
                                                    }
                                                }
                                            },
                                            {
                                                'term': {
                                                    'titles.title.exact': {
                                                        'value': title,
                                                        'boost': 2,
                                                    }
                                                }
                                            },
                                        ]
                                    }
                                },
                            }
                        },
                        {'term': {'imdb': title}},
                    ]
                }
            },
            'field_value_factor': {
                'field': 'popularity',
                'modifier': 'log1p',
                'factor': 0.1,
                'missing': 0,
            },
        }
    }
