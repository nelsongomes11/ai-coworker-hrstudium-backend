from typing import Optional
from fastapi import APIRouter, Depends, HTTPException,Header

from pydantic import BaseModel

import services.chat_model_request

# import services ( the functions for each chat )


router = APIRouter(prefix="/chat_requests", tags=["Chat Request"])

class InputMessage(BaseModel):
    input:str
    session_id: Optional[int] = None



@router.post("/input")
async def post_message(input:InputMessage, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authentication")
    
    bearer_token = authorization.replace("Bearer ", "")


        
    
    return services.chat_model_request.handle_chat_model_request(input,bearer_token=bearer_token)

@router.get("/chat_history/{session_id}")
async def get_chat_history(session_id: int, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authentication")
    
    bearer_token = authorization.replace("Bearer ", "")
    
    return services.chat_model_request.get_chat_history(session_id=session_id, bearer_token=bearer_token)
    
