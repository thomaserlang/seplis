from pydantic import BaseModel


class Movie_collection(BaseModel, orm_mode=True):
    id: int
    name: str