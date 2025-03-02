from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.schema.runnable import RunnableParallel, RunnableSequence, RunnableLambda
from langchain.schema import StrOutputParser
import datetime
import asyncio
import json

##############################################################################################
import re
import base64
import pandas as pd
import json
import psycopg2
import aiohttp

import requests
from requests.auth import HTTPBasicAuth
from minio import Minio
from io import BytesIO

import os
os.environ["NO_PROXY"] = "*"

LLM_MODEL = "qwen2.5:1.5b"
LLM_URL = "http://localhost:11434"

router = APIRouter()

async def create_answering_chain(query,
                                history,
                                focusMode,
                                optimizaionMode,
                                extraMessage):
    #콜백 핸들러 설정
    callback = AsyncIteratorCallbackHandler()

    streaming_llm = RunnableLambda(lambda _: ChatOllama(
        model = LLM_MODEL,
        base_url = LLM_URL,
        streaming = True,
        callbacks = [callback],
        keep_alive = -1
    )).with_config({
        "runName": "StreamingLLM"
    })

    print(f"LLM_MODEL: {LLM_MODEL}")
    print(f"LLM_URL: {LLM_URL}")

    #프롬프트 템플릿 설정
    prompt = ChatPromptTemplate.from_messages([
        ("system","""
            당신은 R&D AI 어시스턴트입니다.
            질문 "{query}"에 대한 답변을 해주세요
            """
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human","{query}")
    ]).with_config({
        "runName": 'PromptTemplate'
    })

    chain = (
        prompt |
        streaming_llm |
        StrOutputParser()
    ).with_config(
        run_name="FinalResponseGenerator"
    )

    task = asyncio.create_task(
        chain.ainvoke({
            "chat_history": history,
            "query": query,
        })
    )

    async def stream_response():
        try:
            async for chunk in callback.aiter():
                print(chunk)
                content = chunk if isinstance(chunk, str) else chunk.content

                #스트리밍 응답 포매팅
                if not isinstance(content, str):
                    content = str(content)
                
                yield json.dumps({
                    "type": "response",
                    "data": content
                }) + "\n"
        except Exception as e:
            print(f"Streaming error:{e}")
        finally:
            callback.done.set()

    return StreamingResponse(stream_response(), media_type="text/event-stream")

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    query = data.get("message","")
    history = data.get("history",[])
    focusMode = data.get("focusMode",[])
    optimizationMode = data.get("optimizationMode",[])
    extraMessage = data.get("extraMessage",[])

    print(f"/api/writingAssistant/chat query: {query}")
    print(f"/api/writingAssistant/chat history: {history}")
    print(f"/api/writingAssistant/chat focusMode: {focusMode}")
    print(f"/api/writingAssistant/chat optimizationMode: {optimizationMode}")
    print(f"/api/writingAssistant/chat extraMessage: {extraMessage}")

    #히스토리를 LangChain 메시지 형식으로 변환
    formatted_history = []
    print(len(history))
    if len(history) > 0:
        print(history)
        for msg in history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_history.append(SystemMessage(content=msg["content"]))
    
    return await create_answering_chain(query,
                                        formatted_history,
                                        focusMode,
                                        optimizationMode,
                                        extraMessage)