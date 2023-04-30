from pydantic import BaseModel


def compare(new: BaseModel, old: BaseModel):
    '''
    Returns what is different in a compared to b.
    '''
    new_dict = new.dict()
    old_dict = old.dict()

    keys = new_dict.keys() & old_dict.keys()

    return {k: new_dict[k] for k in keys if new_dict[k] != old_dict[k]}
