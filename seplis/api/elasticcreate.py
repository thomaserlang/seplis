import asyncio
from seplis import config

async def create_indices(es):
    await asyncio.gather(
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