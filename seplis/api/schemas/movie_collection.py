from pydantic import BaseModel, ConfigDict


class MMovieCollection(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
