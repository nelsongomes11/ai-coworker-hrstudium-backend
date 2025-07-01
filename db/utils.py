from fastapi import HTTPException
import requests
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models import User, Session as ChatSession, Message, ChatEmployeesMessages
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory

def user_exists(db: Session, user_id: int) -> bool:
    return db.query(User).filter(User.id == user_id).first() is not None

def create_user(db: Session, user_id: int, nome_completo: str) -> int:
    new_user = User(id=user_id, nome_completo=nome_completo)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id

def create_session(db: Session, user_id: int, type_chat: str = "default") -> int:
    new_session = ChatSession(user_id=user_id, type_chat=type_chat)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session.id


def save_message(
    db: Session,
    user_id: int,
    content: str,
    role: str,
    session_id: Optional[int] = None,
    type_chat: str = "default",
    bearer_token: Optional[str] = None
):
    if not user_exists(db, user_id):

        response = requests.get("https://api-dev.hrstudium.pt/users",
                headers={
                    "company":"dev",
                    "Authorization":"Bearer "+bearer_token
                }

            )

        if response.status_code == 200:
                user_data = response.json()
                nome_completo = user_data.get("nome_completo")

                user_id = create_user(db, user_id=user_id, nome_completo=nome_completo)

        else:
                raise HTTPException(status_code=401, detail="Invalid or missing authentication")
        
    # If session_id not provided, create a new session
    if not session_id:
        session_id = create_session(db, user_id, type_chat)

    message = Message(
        session_id=session_id,
        role=role,
        content=content,
        created_at=datetime.now()
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    return {
        "session_id": session_id,
        "message_id": message.id,
        "content": message.content
    }

def get_session(db: Session, session_id: int) -> Optional[ChatSession]:
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        return None
    return {
        "id": session.id,
        "user_id": session.user_id,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "type_chat": session.type_chat
    }

def get_sessions(db: Session, user_id: int) -> List[dict]:
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    return [{"id": s.id, "created_at": s.created_at, "updated_at": s.updated_at, "type_chat": s.type_chat} for s in sessions]


def get_session_messages(db: Session, session_id: int) -> List[Message]:
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    return [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]

def get_messages(db: Session, session_id: int) -> List:
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    history = ChatMessageHistory()

    for m in messages:
        if m.role == "user":
            history.add_user_message(m.content)
        elif m.role == "assistant":
            history.add_ai_message(m.content)

    return history


## CHAT EMPLOYEES 

def save_chat_employee_message(
    db:Session,
    sender_id: int,
    receiver_id: int,
    message: str,
    file_url: Optional[str] = None
    
):
    chat_message= ChatEmployeesMessages(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message,
        file_url=file_url,
        timestamp=datetime.now()
    )

    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)

    return {
        "id": chat_message.id,
        "sender_id": chat_message.sender_id,
        "receiver_id": chat_message.receiver_id,
        "message": chat_message.message,
        "file_url": chat_message.file_url,

    }


def get_chat_employee_messages(
    db: Session,
    sender_id: int,
    receiver_id: int
) -> List[ChatEmployeesMessages]:
    
    messages = db.query(ChatEmployeesMessages).filter(
        (ChatEmployeesMessages.sender_id == sender_id) & 
        (ChatEmployeesMessages.receiver_id == receiver_id)
    ).order_by(ChatEmployeesMessages.timestamp.asc()).all()

    messagesReceiver = db.query(ChatEmployeesMessages).filter(
        (ChatEmployeesMessages.sender_id == receiver_id) &
        (ChatEmployeesMessages.receiver_id == sender_id)
    ).order_by(ChatEmployeesMessages.timestamp.asc()).all()

    messages.extend(messagesReceiver)
    messages.sort(key=lambda x: x.timestamp)

    return [{
        "id": m.id,
        "sender_id": m.sender_id,
        "receiver_id": m.receiver_id,
        "message": m.message,
        "file_url": m.file_url,
        "timestamp": m.timestamp
    } for m in messages]