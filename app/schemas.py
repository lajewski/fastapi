from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Optional, Union

class PostBase(BaseModel):  # ensures that the 'title' and 'content' fields are present and that they're both strings
    title: str
    content: str  # mandatory field
    published: bool = True  # optional field w default set as true

class PostCreate(PostBase):
    pass

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

class Post(PostBase): #inherits the title, content & published fields from PostBase
    post_id: int
    post_created_at: datetime
    user_id: int
    id: int
    email: EmailStr
    created_at: datetime
    votes: int

class MainPost(PostBase): #inherits the title, content & published fields from PostBase
    post_id: int
    post_created_at: datetime
    user_id: int

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    #id: Optional[str]
    id: Union[int,str]

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1) #direction of vote. 1 means a like, 0 means remove vote. le=1 means anything less than 1 is allowed (but really we only want values of 0 or 1...)