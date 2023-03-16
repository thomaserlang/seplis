import re
from fastapi import APIRouter
from pydantic import constr
from typing import Literal
from .. import schemas, exceptions
from ..database import database
from ... import config

router = APIRouter(prefix='/2/search')


@router.get('', response_model=list[schemas.Search_title_document])
async def search(
    query: constr(min_length=1, max_length=200) | None = None,
    title: constr(min_length=1, max_length=200) | None = None,
    type: Literal['series', 'movie'] | None = None,
):
    if query:
        q = get_by_query(query)
    elif title:
        q = get_by_title(title)

    if not q:
        raise exceptions.Elasticsearch_exception(message='No query')

    if type:
        q = {
            'bool': {
                'must': q,
                'filter': {
                    'term': {
                        'type': type,
                    }
                }
            }
        }

    r = await database.es.search(index=config.data.api.elasticsearch.index_prefix+'titles', query=q)
    return [schemas.Search_title_document.parse_obj(a['_source'])
            for a in r['hits']['hits']]


def get_by_query(title: str):
    return {
        'function_score': {
            'query': {
                'dis_max': {
                    'queries': [
                        {
                            'nested': {
                                'path': 'titles',
                                'query': {
                                    'multi_match': {
                                        'query': title,
                                        'type': 'bool_prefix',
                                        'operator': 'and',
                                        'fields': [
                                            'titles.title',
                                            'titles.title._2gram',
                                            'titles.title._3gram',
                                        ],
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
            }
        }
    }


def get_by_title(title: str):
    return {
        'dis_max': {
            'queries': [
                {'nested': {
                    'path': 'titles',
                    'query': {
                        'match_phrase': {
                            'titles.title': {
                                'query': title,
                            }
                        }
                    },
                }},
                {'term': {'imdb': title}},
            ]
        }
    }
