from fastapi import Depends, HTTPException
import requests
from ai.models.chat_model_approve import get_chat_model_approve

from db.database import SessionLocal
from db.utils import save_message, get_messages,get_session,get_session_messages



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def handle_chat_model_approve(input:dict,bearer_token):

    with SessionLocal() as db:

        user_input = input.input
        session_id = input.session_id

        response = requests.get("https://api-dev.hrstudium.pt/users",
                headers={
                    "company":"dev",
                    "Authorization":"Bearer "+bearer_token
                }

            )

        if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get("id")

        else:
                
                raise HTTPException(status_code=401, detail="Invalid or missing authentication")


        save_response=save_message(db,user_id=user_id,content=user_input,role="user",session_id=session_id,type_chat="approve",bearer_token=bearer_token)

        session_id=save_response.get("session_id")

        history = get_messages(db, session_id=session_id)
        
        chat_model_response=get_chat_model_approve(bearer_token,user_input,history=history)

        save_ai_response=save_message(db,user_id=user_id,content=chat_model_response,role="assistant",session_id=session_id)

        return {
            "chat_ai_message": save_ai_response
        }


def get_chat_history(session_id,bearer_token):
    with SessionLocal() as db:
         
        response = requests.get("https://api-dev.hrstudium.pt/users",
                headers={
                    "company":"dev",
                    "Authorization":"Bearer "+bearer_token
                }

            )

        if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get("id")

        else:
                
               raise HTTPException(status_code=401, detail="Invalid or missing authentication")

        session_response=get_session(db,session_id=session_id)

        if not session_response:
            raise HTTPException(status_code=404, detail="Invalid session id")
        
        if session_response.get("user_id") != user_id:
            raise HTTPException(status_code=401, detail="Not Authorized")
        
        return get_session_messages(db, session_id=session_id)

        

        



        