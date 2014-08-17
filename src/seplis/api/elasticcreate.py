from seplis.config import config
from seplis.connections import database

def create_indices():
    database.es.indices.create('shows', body={
        'settings': {
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
        },
        'mappings': {
            'show': {
                'properties' : {
                    'title_suggest': {
                        'type': 'completion',
                        'payloads': True
                    },
                    'title': {
                        'type': 'string',
                        'index_analyzer': 'nGram_analyzer',
                        'search_analyzer': 'whitespace_analyzer'
                    }
                }
            }
        }
    })

if __name__ == '__main__':
    create_indices()