from pydantic import BaseModel, ConfigDict


class Movie_collection(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)