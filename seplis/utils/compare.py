from dataclasses import asdict, is_dataclass
from typing import Any


def _to_dict(value: Any, *, exclude_unset: bool = False) -> dict[str, Any]:
    if hasattr(value, 'model_dump'):
        return value.model_dump(exclude_unset=exclude_unset)
    if is_dataclass(value):
        return asdict(value)
    return dict(value)


def compare(new: Any, old: Any, skip_keys: list[str] | None = None) -> dict[str, Any]:
    """
    Returns what is different in a compared to b.
    """
    if skip_keys is None:
        skip_keys = []
    new_dict = _to_dict(new, exclude_unset=True)
    old_dict = _to_dict(old)

    keys = new_dict.keys() & old_dict.keys()

    def is_equal(a: Any, b: Any) -> bool:
        if isinstance(a, list) and isinstance(b, list):
            return sorted(a) == sorted(b)
        return a == b

    return {
        k: new_dict[k]
        for k in keys
        if k not in skip_keys and not is_equal(new_dict[k], old_dict[k])
    }
