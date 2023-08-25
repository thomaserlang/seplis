from pydantic import BaseModel

from seplis import logger


def compare(new: BaseModel, old: BaseModel, skip_keys: list[str] = []):
    '''
    Returns what is different in a compared to b.
    '''
    new_dict = new.model_dump(exclude_unset=True)
    old_dict = old.model_dump()

    keys = new_dict.keys() & old_dict.keys()

    def is_equal(a, b):
        if isinstance(a, list) and isinstance(b, list):
            return sorted(a) == sorted(b)
        return a == b

    return {k: new_dict[k] for k in keys 
            if k not in skip_keys and 
                not is_equal(new_dict[k], old_dict[k])}
