from pydantic import BaseModel, ConfigDict

class Genre(BaseModel):
    id: int
    name: str
    number_of: int = 0	

    model_config = ConfigDict(from_attributes=True)