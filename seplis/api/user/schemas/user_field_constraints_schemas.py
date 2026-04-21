from typing import Annotated

from pydantic import Field

type ConstrainedLang = Annotated[str, Field(min_length=1, max_length=20)]
type PasswordStr = Annotated[str, Field(min_length=10)]
