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
    results: list[schemas.Search_title_document] = []
    for a in r['hits']['hits']:
        results.append(schemas.Search_title_document.parse_obj(a['_source']))
    return results


def get_by_query(query: str):
    return {
        'dis_max': {
            'queries': [
                {                             
                    'nested': { 
                        'path': 'titles',   
                        'query': {
                            'bool': {
                                'should': [
                                    {'multi_match': {
                                        'boost': 4,
                                        'query': query,
                                        'operator': 'and',
                                        'fields': [
                                            'titles.title',
                                            'titles.title._2gram',
                                            'titles.title._3gram',
                                        ]
                                    }},
                                    {'multi_match': {
                                        'query': query,
                                        'type': 'bool_prefix',
                                        'minimum_should_match': '75%',
                                        'fields': [
                                            'titles.title',
                                            'titles.title._2gram',
                                            'titles.title._3gram',
                                        ]
                                    }},
                                ]
                            }
                        }
                    }
                },
                { 'term': { 'imdb': query} },
            ]
        }
    }


def get_by_title(title: str):
    return {
        'dis_max': {
            'queries': [                        
                {'nested': {
                    'path': 'titles',
                    'query': 
                        { 'match_phrase': { 'titles.title': title }},
                }},
                { 'term': { 'imdb': title} },
            ]
        }
    }