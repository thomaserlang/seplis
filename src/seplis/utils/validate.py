import inspect
from typing import Optional
import good
import pydantic

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
        if inspect.isclass(schema) and issubclass(schema, pydantic.BaseModel):
            return schema.parse_obj(data)
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
    except pydantic.ValidationError as e:
        data = []
        for e in e.errors():
            data.append({
                'field': '.'.join(str(x) for x in e['loc']),
                'message': e['msg'],
            })            
        raise Validation_exception(errors=data)


class AllOptional(pydantic.main.ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)