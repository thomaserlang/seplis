from seplis.config import config
from seplis.api.connections import database

def create_indices():
    database.es.indices.delete(index='shows', ignore=404)
    database.es.indices.delete(index='episodes', ignore=404)
    database.es.indices.delete(index='images', ignore=404)
    database.es.indices.delete(index='users', ignore=404)

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
                    "token_chars": [
                        "letter",
                        "digit"
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
                        'word_delimiter',
                    ],
                },
            },
        }
    }

    database.es.indices.create(index='shows', settings=settings, mappings={
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
                    'text': { 
                        'type': 'keyword',
                        'index': True,
                    },
                    'url': { 
                        'type': 'text',
                    },
                    'title': { 
                        'type': 'text',
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
                'type': 'text',
            },                    
            'episode_type': { 'type': 'integer' },
            'created_at': { 'type': 'date' },
            'updated_at': { 'type': 'date' },
            'fans': { 'type': 'integer' },
        }
    })

    database.es.indices.create(index='episodes', mappings={
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
                    'text': { 
                        'type': 'keyword',
                        'index': True, 
                    },
                    'url': { 'type': 'text' },
                    'title': { 'type': 'text' },
                },
            },
            'season': { 'type': 'integer' },
            'episode': { 'type': 'integer' },
            'show_id': { 'type': 'integer' },
            'runtime': { 'type': 'integer' },
        },
    })

    database.es.indices.create(index='images', mappings={
        'properties' : {
            'id': { 'type': 'integer' },
            'relation_type': { 'type': 'text' },
            'relation_id': { 'type': 'integer' },
            'external_name': { 'type': 'text' },
            'external_id': { 'type': 'text' },
            'height': { 'type': 'integer' },
            'width': { 'type': 'integer' },
            'hash': { 'type': 'text' },
            'source_title': { 'type': 'text' },
            'source_url': { 'type': 'text' },
            'type': { 'type': 'integer' },
            'created_at': { 'type': 'date' },
        },
    })

if __name__ == '__main__':
    create_indices()