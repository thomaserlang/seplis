from seplis.config import config
from seplis.connections import database

def create_indices():
    settings = {
        'analysis': {
            'filter': {
                'nGram_filter': {
                    'type': 'nGram',
                    'min_gram': 2,
                    'max_gram': 20,
                    'token_chars': [
                        'letter',
                        'digit',
                        'punctuation',
                        'symbol'
                    ]
                }
            },
            'analyzer': {
                'nGram_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'whitespace',
                    'filter': [
                       'lowercase',
                       'asciifolding',
                       'nGram_filter'
                   ]
                },
                'whitespace_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'whitespace',
                    'filter': [
                    'lowercase',
                        'asciifolding'
                   ]
                }
            }
        }
    }

    database.es.indices.create('shows', body={
        'settings': settings,
        'mappings': {
            'show': {
                'properties' : {
                    'title': {
                        'type': 'string',
                        'index_analyzer': 'nGram_analyzer',
                        'search_analyzer': 'whitespace_analyzer',
                    },
                    'id': { 'type': 'integer' },
                    'description': {
                        'dynamic' : False,
                        'properties' : {
                            'text': { 'type': 'string' },
                            'url': { 'type': 'string' },
                            'title': { 'type': 'string' },
                        }
                    },
                    'premiered': { 'type': 'date' },
                    'ended': { 'type': 'date' },
                    'externals': {
                        'dynamic' : True,
                        'type': 'object',
                    },
                    'indices': {
                        'dynamic': False,
                        'properties': {
                            'info': { 'type': 'string' },
                            'episodes': { 'type': 'string' },
                            'images': { 'type': 'string' },
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
                    'alternate_titles': {
                        'type': 'string',
                        'index_name': 'alternate_title',
                    },
                    'genres': {
                        'type': 'string',
                        'index_name': 'genre',
                    },
                }
            }
        }
    })

    database.es.indices.create('episodes', body={
        'settings': settings,
        'mappings': {
            'episode': {
                'properties' : {
                    'title': {
                        'type': 'string',
                        'index_analyzer': 'nGram_analyzer',
                        'search_analyzer': 'whitespace_analyzer',
                    },
                    'number': { 'type': 'integer' },
                    'air_date': { 'type': 'date' },
                    'description': {
                        "dynamic" : False,
                        'properties' : {
                            'text': { 'type': 'string' },
                            'url': { 'type': 'string' },
                            'title': { 'type': 'string' },
                        },
                    },
                    'season': { 'type': 'integer' },
                    'episode': { 'type': 'integer' },
                    'show_id': { 'type': 'integer' },
                    'runtime': { 'type': 'integer' },
                },
            }
        }
    })

if __name__ == '__main__':
    create_indices()