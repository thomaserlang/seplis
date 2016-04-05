from seplis.config import config
from seplis.api.connections import database

def create_indices():
    database.es.indices.delete('shows', ignore=404)
    database.es.indices.delete('episodes', ignore=404)
    database.es.indices.delete('images', ignore=404)
    database.es.indices.delete('users', ignore=404)

    settings = {
        'analysis': {
            'char_filter': {
                'strip_apostrophe': {
                    'type': 'mapping',
                    'mappings': ['`=>', '’=>', '\'=>']
                }
            },
            'tokenizer': {
                'autocomplete_ngram': { 
                    'type': 'nGram',
                    'min_gram': 1,
                    'max_gram': 5,
                },
            },
            'analyzer': {
                'autocomplete_index': {
                    'type' : 'custom',
                    'tokenizer': 'autocomplete_ngram',
                    'filter': [
                        'lowercase',
                        'asciifolding',
                        'word_delimiter',
                    ],
                },
                'autocomplete_search': {
                    'type' : 'custom',
                    'tokenizer': 'standard',
                    'filter': [
                        'lowercase',
                        'asciifolding',
                        'word_delimiter',
                    ],
                },
                'title_search': {
                    'type' : 'custom',
                    'tokenizer': 'keyword',
                    'char_filter': ['strip_apostrophe'],
                    'filter': [
                        'lowercase',
                        'asciifolding',
                        'word_delimiter',
                    ],
                },
            },
        }
    }

    database.es.indices.create('shows', body={
        'settings': settings,
        'mappings': {
            'show': {
                'properties': {
                    'title': {
                        'type': 'string',
                        'analyzer': 'title_search',
                        'fields': {
                            'raw' : {
                                'type': 'string', 
                                'index': 'not_analyzed',
                            },
                            'suggest': {
                                'type': 'string', 
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
                                'type': 'string',
                                'index': 'not_analyzed',
                            },
                            'url': { 
                                'type': 'string',
                            },
                            'title': { 
                                'type': 'string',
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
                    'alternative_titles': {
                        'type': 'string',
                        'analyzer': 'title_search',
                        'fields': {
                            'suggest': {
                                'type': 'string', 
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
                        'type': 'string',
                    },                    
                    'episode_type': { 'type': 'integer' },
                    'created_at': { 'type': 'date' },
                    'updated_at': { 'type': 'date' },
                    'fans': { 'type': 'integer' },
                }
            }
        }
    })

    database.es.indices.create('episodes', body={
        'mappings': {
            'episode': {
                'properties' : {
                    'title': {
                        'type': 'string',
                    },
                    'number': { 'type': 'integer' },
                    'air_date': { 'type': 'date' },
                    'description': {
                        'dynamic' : False,
                        'properties' : {
                            'text': { 
                                'type': 'string',
                                'index': 'not_analyzed', 
                            },
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

    database.es.indices.create('images', body={
        'mappings': {
            'image': {
                'properties' : {
                    'id': { 'type': 'integer' },
                    'relation_type': { 'type': 'string' },
                    'relation_id': { 'type': 'integer' },
                    'external_name': { 'type': 'string' },
                    'external_id': { 'type': 'string' },
                    'height': { 'type': 'integer' },
                    'width': { 'type': 'integer' },
                    'hash': { 'type': 'string' },
                    'source_title': { 'type': 'string' },
                    'source_url': { 'type': 'string' },
                    'type': { 'type': 'integer' },
                    'created_at': { 'type': 'date' },
                },
            }
        }
    })

    database.es.indices.create('users', body={
        'settings': settings,
        'mappings': {
            'user': {
                'properties': {
                    'id': { 'type': 'integer' },
                    'name': {
                        'type': 'string',      
                        'fields': {
                            'raw' : {
                                'type': 'string', 
                                'index': 'not_analyzed',
                            },
                            'suggest': {
                                'type': 'string', 
                                'analyzer': 'autocomplete_index',
                                'search_analyzer': 'autocomplete_search',
                            }
                        }
                    },
                    'email': { 'type': 'string' },
                    'level': { 'type': 'integer' },
                    'created_at': { 'type':  'date' },
                }
            }
        }
    })


if __name__ == '__main__':
    create_indices()