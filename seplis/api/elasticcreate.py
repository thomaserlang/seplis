import asyncio
from seplis import config

async def create_indices(es):
    await asyncio.gather(
        es.options(ignore_status=[400,404]).indices.delete(index=config.data.api.elasticsearch.index_prefix+'shows'),
        es.options(ignore_status=[400,404]).indices.delete(index=config.data.api.elasticsearch.index_prefix+'episodes'),
        es.options(ignore_status=[400,404]).indices.delete(index=config.data.api.elasticsearch.index_prefix+'images'),
        es.options(ignore_status=[400,404]).indices.delete(index=config.data.api.elasticsearch.index_prefix+'users'),
        es.options(ignore_status=[400,404]).indices.delete(index=config.data.api.elasticsearch.index_prefix+'titles'),
    )

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
            'tokenizer': {
                'autocomplete_ngram': { 
                    'type': 'edge_ngram',
                    'min_gram': 1,
                    'max_gram': 10,
                    'token_chars': [
                        'letter',
                        'digit'
                    ]
                },
            },
            'analyzer': {
                'autocomplete_index': {
                    'type' : 'custom',
                    'tokenizer': 'autocomplete_ngram',
                    'char_filter': ['strip_stuff'],
                    'filter': [
                        'lowercase',
                        'asciifolding',
                    ],
                },
                'autocomplete_search': {
                    'type' : 'standard',
                    'tokenizer': 'standard',
                    'char_filter': ['strip_stuff'],
                    'filter': [
                        'lowercase',
                        'asciifolding',
                    ],
                },
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

    await es.indices.create(index=config.data.api.elasticsearch.index_prefix+'shows', settings=settings, mappings={
        'properties': {
            'title': {
                'type': 'text',
                'analyzer': 'title_search',
                'fields': {
                    'raw' : {
                        'type': 'keyword', 
                        'index': True,
                    },
                    'suggest': {
                        'type': 'text', 
                        'analyzer': 'autocomplete_index',
                        'search_analyzer': 'autocomplete_search',
                    },
                    'length': { 
                        'type': 'token_count',
                        'analyzer': 'standard'
                    },
                }
            },
            'id': { 'type': 'integer' },
            'description': {
                'dynamic' : False,
                'properties' : {
                    'text': { 'type': 'text' },
                    'url': { 
                        'type': 'keyword',
                    },
                    'title': { 
                        'type': 'keyword',
                    },
                }
            },
            'premiered': { 'type': 'date' },
            'ended': { 'type': 'date' },
            'externals': {
                'dynamic' : True,
                'type': 'object',
            },
            'import_from': {
                'dynamic': False,
                'properties': {
                    'info': { 'type': 'text' },
                    'episodes': { 'type': 'text' },
                    'images': { 'type': 'text' },
                },
            },
            'status': { 'type': 'integer' },
            'runtime': { 'type': 'integer' },
            'seasons': {
                'properties': {
                    'season': { 'type': 'integer' },
                    'from': { 'type': 'integer' },
                    'to': { 'type': 'integer' },
                    'total': { 'type': 'integer' },
                },
            },
            'alternative_titles': {
                'type': 'text',
                'analyzer': 'title_search',
                'fields': {
                    'suggest': {
                        'type': 'text', 
                        'analyzer': 'autocomplete_index',
                        'search_analyzer': 'autocomplete_search',
                    },
                    'length': { 
                        'type': 'token_count',
                        'analyzer': 'standard',
                    },
                },
            },
            'genres': {
                'type': 'keyword',
            },                    
            'episode_type': { 'type': 'integer' },
            'created_at': { 'type': 'date' },
            'updated_at': { 'type': 'date' },
            'fans': { 'type': 'integer' },
        }
    })

    await es.indices.create(index=config.data.api.elasticsearch.index_prefix+'episodes', mappings={
        'properties' : {
            'title': {
                'type': 'text',
            },
            'number': { 'type': 'integer' },
            'air_date': { 'type': 'date', },
            'air_datetime': { 'type': 'date', 'format': 'date_time_no_millis', },
            'description': {
                'dynamic' : False,
                'properties' : {
                    'text': { 'type': 'text' },
                    'url': { 'type': 'keyword' },
                    'title': { 'type': 'keyword' },
                },
            },
            'season': { 'type': 'integer' },
            'episode': { 'type': 'integer' },
            'show_id': { 'type': 'integer' },
            'runtime': { 'type': 'integer' },
        },
    })

    await es.indices.create(index=config.data.api.elasticsearch.index_prefix+'images', mappings={
        'properties' : {
            'id': { 'type': 'integer' },
            'relation_type': { 'type': 'keyword' },
            'relation_id': { 'type': 'integer' },
            'external_name': { 'type': 'keyword' },
            'external_id': { 'type': 'keyword' },
            'height': { 'type': 'integer' },
            'width': { 'type': 'integer' },
            'hash': { 'type': 'keyword' },
            'source_title': { 'type': 'keyword' },
            'source_url': { 'type': 'keyword' },
            'type': { 'type': 'integer' },
            'created_at': { 'type': 'date' },
        }
    })

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
                    }
                }
            },
            'imdb': { 'type': 'keyword' },
            'premiered': { 'type': 'date' },
            'poster_image': {
                'type': 'object',
                'enabled': False,
            }
        }
     })

if __name__ == '__main__':
    create_indices()