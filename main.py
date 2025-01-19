#main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import chat

app = FastAPI()
  

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api")