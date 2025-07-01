from typing import Optional
from fastapi import APIRouter, Depends, HTTPException,Header,UploadFile, File, Form

from pydantic import BaseModel

import services.chat_model_request

# import services ( the functions for each chat )


router = APIRouter(prefix="/chat_requests", tags=["Chat Request"])

@router.post("/input")
async def post_message(
    input: str = Form(...),
    session_id: Optional[int] = Form(None),
    uploaded_files: Optional[list[UploadFile]] = File(None),
    authorization: Optional[str] = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authentication")
    
    bearer_token = authorization.replace("Bearer ", "")

    input_data = {
        "input": input,
        "session_id": session_id
    }
    if uploaded_files :
        input_data["uploaded_files"] = [file.filename for file in uploaded_files]
        print(f"Received Files: {[file.filename for file in uploaded_files]}")

        
    return services.chat_model_request.handle_chat_model_request(
        input=input_data,
        bearer_token=bearer_token,
        uploaded_files=uploaded_files
    )

@router.get("/chat_history/{session_id}")
async def get_chat_history(session_id: int, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authentication")
    
    bearer_token = authorization.replace("Bearer ", "")
    
    return services.chat_model_request.get_chat_history(session_id=session_id, bearer_token=bearer_token)
    
