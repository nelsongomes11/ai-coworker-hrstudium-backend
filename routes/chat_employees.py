from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.utils import get_chat_employee_messages, save_chat_employee_message  # import your utility function
from typing import Dict, List
from datetime import datetime
import json

router = APIRouter(prefix="/chat_employees", tags=["Chat Employees"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# user_id -> list of WebSocket connections
active_connections: Dict[int, List[WebSocket]] = {}

def connect(user_id: int, websocket: WebSocket):
    print(f"New WebSocket for user {user_id}")
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)

def disconnect(user_id: int, websocket: WebSocket):
    if user_id in active_connections:
        active_connections[user_id].remove(websocket)
        if not active_connections[user_id]:
            del active_connections[user_id]

async def send_to_user(user_id: int, message: dict):
    if user_id in active_connections:
        for ws in active_connections[user_id]:
            await ws.send_text(json.dumps(message))

@router.websocket("/ws/chat/{user_id}")
async def chat_ws(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            sender_id = payload["sender_id"]
            receiver_id = payload["receiver_id"]
            message_text = payload.get("message", "")
            file_url = payload.get("file_url")  # can be null

            # Save to DB using your utility
            response = save_chat_employee_message(
                db=db,
                sender_id=sender_id,
                receiver_id=receiver_id,
                message=message_text,
                file_url=file_url
            )

            print(f"Message saved: {response}")
            # Build response payload
            

            # Send to both users
            await send_to_user(sender_id, response)
            if sender_id != receiver_id:
                await send_to_user(receiver_id, response)

    except WebSocketDisconnect:
        disconnect(user_id, websocket)


@router.get("/chat_history/{sender_id}/{receiver_id}")
def get_chat_history(
    sender_id: int,
    receiver_id: int,
    db: Session = Depends(get_db)
):
    messages = get_chat_employee_messages(db=db, sender_id=sender_id, receiver_id=receiver_id)
    return messages