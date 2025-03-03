#main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat.writingAssistant import router as writing_router
from chat.pipelineSearch import router as pipeline_router
from chat.writingAssistant_vllm import router as writing_router_vllm
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
app.include_router(writing_router, prefix="/api/writingAssistant")
app.include_router(pipeline_router, prefix="/api/pipelineSearch")
app.include_router(writing_router_vllm, prefix="/api/writingAssistant_vllm")

# uvicorn main:app --reload