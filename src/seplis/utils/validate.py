import good

class Validation_exception(Exception):

    def __init__(self, errors):
        super().__init__('Failed schema validation. See `errors` for more info')
        self.errors = errors

def validate_schema(schema, data, **kwargs):
    """Validates `schema` against `data`. Returns
    the data modified by the validator.

    ``schema`` can be a dict or an instance of `good.Schema`.
    If it's a dict a `good.Schema` instance will be created from it.

    Raises `Validation_exception`

    """
    try:
        if not isinstance(schema, good.Schema):        
            schema = good.Schema(schema, **kwargs)
        return schema(data)    
    except good.MultipleInvalid as ee:
        data = []
        for e in ee:
            data.append({
                'field': u'.'.join(str(x) for x in e.path),
                'message': e.message,
            })
        raise Validation_exception(errors=data)
    except good.Invalid as e:
        data = [{
            'field': u'.'.join(str(x) for x in e.path),
            'message': e.message,
        }]            
        raise Validation_exception(errors=data)