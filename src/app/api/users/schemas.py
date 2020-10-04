from datetime import datetime
from pydantic import BaseModel, Field, validator


class UserIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserOut(UserIn):
    id: int = Field(..., gt=0)
    created_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()
