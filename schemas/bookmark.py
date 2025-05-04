from pydantic import BaseModel
from typing import Optional


class BookmarkBase(BaseModel):
    url: str
    title: Optional[str] = None
    user_id: Optional[int] = None


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkRead(BookmarkBase):
    id: int

    class Config:
        orm_mode = True
    
class BookmarkUpdate(BaseModel):
    id:int
    url: Optional[str] = None
    title: Optional[str] = None
    # user_id: Optional[str] = None
