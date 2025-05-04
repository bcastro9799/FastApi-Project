from typing import List, Optional


from pydantic import BaseModel


class Roles(BaseModel):
    roles: Optional[List[str]] = None

class TokenData(BaseModel):
    sid:Optional[str] = None
    sub: Optional[str] = None
    active: bool = False
    scope: Optional[str] = None
    username:Optional[str] = None
    realm_access: Roles = None
    bdp_token:Optional[str] = None
    groups:Optional[List[str]] = None
    user_id: Optional[int] = None