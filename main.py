from fastapi import FastAPI
from fastapi import APIRouter
from routes.chat_requests import router as chat_requests_router


app = FastAPI()



@app.get("/")
async def root():
    return {"message": "HRStudium Vacation and Absence Management System"}

app.include_router(chat_requests_router)