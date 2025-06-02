from typing import Optional
from fastapi import APIRouter, Depends, HTTPException,Header,UploadFile, File, Form

from pydantic import BaseModel

import services.chat_model_approve

# import services ( the functions for each chat )


class InputMessage(BaseModel):
    input:str
    session_id: Optional[int] = None

router = APIRouter(prefix="/chat_approve", tags=["Chat Approve"])

@router.post("/input")
async def post_message(
    input: InputMessage,
    authorization: Optional[str] = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authentication")
    
    bearer_token = authorization.replace("Bearer ", "")

    return services.chat_model_approve.handle_chat_model_approve(
        input=input,
        bearer_token=bearer_token,
        
    )

@router.get("/chat_history/{session_id}")
async def get_chat_history(session_id: int, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authentication")
    
    bearer_token = authorization.replace("Bearer ", "")
    
    return services.chat_model_approve.get_chat_history(session_id=session_id, bearer_token=bearer_token)
    
