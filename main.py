from fastapi import FastAPI
from fastapi import APIRouter
from routes.chat_requests import router as chat_requests_router
from routes.chat_approve import router as chat_approve_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def root():
    return {"message": "HRStudium Vacation and Absence Management System"}

app.include_router(chat_requests_router)
app.include_router(chat_approve_router)