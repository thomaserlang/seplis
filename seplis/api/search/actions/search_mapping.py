import hashlib
import re
import unicodedata
from typing import Any

from seplis import utils

from ..schemas.search_schemas import SearchTitleDocument


def normalize_name(value: str) -> str:
    chars = []
    latin = False
    for char in unicodedata.normalize('NFD', value.casefold()):
        if not unicodedata.combining(char):
            latin = 'LATIN' in unicodedata.name(char, '')
        if not unicodedata.combining(char) or not latin:
            chars.append(char)
    value = unicodedata.normalize('NFC', ''.join(chars)).replace('&', ' and ')
    value = re.sub(r"['\u2019`]", '', value)
    return ' '.join(
        ''.join(
            c if c.isalnum() or unicodedata.category(c).startswith('M') else ' '
            for c in value
        ).split()
    )


def name_keys(value: str) -> list[str]:
    # Dots can separate filename words or be part of an acronym (U.S.).
    names = {normalize_name(value), normalize_name(value.replace('.', ''))}
    return sorted(hashlib.sha256(n.encode()).hexdigest() for n in names if n)


def index_document(
    document: SearchTitleDocument, original_title: str | None = None
) -> dict[str, Any]:
    primary = [document.title or '', original_title or '']
    names = list(dict.fromkeys(primary + [t.title for t in document.titles or []]))
    year = str(document.release_date.year) if document.release_date else ''
    names = [
        n
        for n in names
        if n in primary
        or not (year and n.endswith(' ' + year) and n[: -(len(year) + 1)] in names)
    ]
    return {
        'id': f'{document.type}-{document.id}',
        'title': normalize_name(document.title or ''),
        'aliases': list(dict.fromkeys(normalize_name(n) for n in names if n)),
        'primary_keys': sorted({k for n in primary for k in name_keys(n)}),
        'name_keys': sorted({k for n in names for k in name_keys(n)}),
        'type': document.type,
        'year': document.release_date.year if document.release_date else 0,
        'imdb': (document.imdb or '').lower(),
        'popularity': max(0.0, document.popularity or 0.0),
        'payload': utils.json_dumps(document),
    }
