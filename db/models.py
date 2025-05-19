from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base

class User(Base):
    __tablename__ = "users"
    id=Column(Integer, primary_key=True, index=True)
    nome_completo=Column(String, index=True)
    sessions=relationship("Session", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    id=Column(Integer, primary_key=True, index=True)
    user_id=Column(Integer, ForeignKey("users.id"))
    created_at=Column(DateTime, default=datetime.now)
    updated_at=Column(DateTime, default=datetime.now, onupdate=datetime.now)
    type_chat=Column(String, index=True)
    user=relationship("User", back_populates="sessions")
    messages=relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    id=Column(Integer, primary_key=True, index=True)
    session_id=Column(Integer, ForeignKey("sessions.id"))
    role=Column(String, index=True)
    content=Column(String, index=True)
    created_at=Column(DateTime, default=datetime.now)
    session=relationship("Session", back_populates="messages")