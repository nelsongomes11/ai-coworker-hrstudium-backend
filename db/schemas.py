from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    session_id: int

class Message(MessageBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class SessionBase(BaseModel):
    type_chat: str

class SessionCreate(SessionBase):
    user_id: int

class Session(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    class Config:

        orm_mode = True

class UserBase(BaseModel):
    full_name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    sessions: List[Session] = []

    class Config:
        orm_mode = True

class ChatEmployeesMessageBase(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    file_url: Optional[str] = None
    timestamp: datetime

    class Config:
        orm_mode = True
