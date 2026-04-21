from pydantic import BaseModel, ConfigDict, Field

from .user_field_constraints_schemas import PasswordStr


class UserAuthenticated(BaseModel):
    id: int
    token: str | None = None
    scopes: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)


class UserChangePassword(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: PasswordStr


class TokenCreate(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
