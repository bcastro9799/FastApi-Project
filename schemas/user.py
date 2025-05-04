from pydantic import BaseModel, EmailStr
from typing import List, Optional

from schemas.bookmark import BookmarkRead

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    bookmarks: List[BookmarkRead] = []
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    id:int
    username: Optional[str]  = None
    email: Optional[EmailStr] = None