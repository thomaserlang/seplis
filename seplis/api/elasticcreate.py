import asyncio
from seplis import config

async def create_indices(es):
    await es.options(ignore_status=[400,404]).indices.delete(index=config.data.api.elasticsearch.index_prefix+'titles')
    
    settings = {
        'analysis': {
            'char_filter': {
                'strip_stuff': {
                    'type': 'mapping',
                    'mappings': [
                        '`=>', 
                        '’=>', 
                        '\'=>',
                        '&=>and',
                    ]
                }
            },
            'normalizer': {
                'exact': {
                    'type': 'custom',
                    'char_filter': ['strip_stuff'],
                    'filter': [
                        'lowercase',
                        'asciifolding',
                    ]
                }
            },
            'analyzer': {
                'title_search': {
                    'type' : 'custom',
                    'tokenizer': 'standard',
                    'char_filter': ['strip_stuff'],
                    'filter': [
                        'lowercase',
                        'asciifolding',
                        'word_delimiter_graph',
                    ],
                },
            },
        }
    }

    await es.indices.create(index=config.data.api.elasticsearch.index_prefix+'titles', settings=settings, mappings={
        'properties': {
            'id': { 'type': 'integer' },
            'type': { 'type': 'keyword' },
            'title': { 
                'type': 'text',
                'analyzer': 'title_search',
            },
            'titles': {
                'type': 'nested',
                'properties': {
                    'title': {
                        'type': 'search_as_you_type',
                        'analyzer': 'title_search',          
                        'fields': {
                            'exact': {
                                'type': 'keyword',
                                'normalizer': 'exact',
                            }
                        }
                    }
                }
            },
            'imdb': { 'type': 'keyword' },
            'premiered': { 'type': 'date' },
            'poster_image': {
                'type': 'object',
                'enabled': False,
            },
            'popularity': { 'type': 'float' },
            'genres': {
                'type': 'object',
                'enabled': False,
            },
            'seasons': {
                'enabled': False,
            },
            'episodes': {
                'enabled': False,
            },
            'imdb_rating': {
                'enabled': False,
            },
            'imdb_rating_votes': {
                'enabled': False,
            },
            'runtime': {
                'enabled': False,
            },
            'language': {
                'enabled': False,
            }
        }
     })