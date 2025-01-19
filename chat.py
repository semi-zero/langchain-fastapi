#chat.py
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks import AsyncIteratorCallbackHandler
# from langchain.schema.runnable import RunnableMap, RunnableSequence, RunnableLambda
from langchain.schema.runnable import RunnableParallel, RunnableSequence, RunnableLambda
from langchain.schema import StrOutputParser
import datetime
import asyncio
import json

router = APIRouter()

async def create_answering_chain(llm, query, history):
    # 콜백 핸들러 설정
    callback = AsyncIteratorCallbackHandler()
    
    # LLM 설정
    # streaming_llm = ChatOllama(
    #     model="phi3:latest",
    #     base_url='http://localhost:11434',
    #     streaming=True,
    #     callbacks=[callback],
    #     temperature=0
    # ).withConfig({
    #     "runName": "StreamingLLM"
    # })
    streaming_llm = RunnableLambda(lambda _: ChatOllama(
        model="phi3:latest",
        base_url='http://localhost:11434',
        streaming=True,
        callbacks=[callback],
        temperature=0
    )).with_config({
        "runName": "StreamingLLM"
    })

    input_processor = RunnableParallel({
        "query": RunnableLambda(lambda x: x["query"]).with_config({
            "runName": 'QueryProcessor'
        }),
        "chat_history": RunnableLambda(lambda x: x["chat_history"]).with_config({
            "runName": 'HistoryProcessor'
        }),
        "timestamp": RunnableLambda(lambda _: datetime.datetime.now().isoformat()).with_config({
            "runName": 'TimestampGenerator'
        })
    }).with_config({
        "runName": 'InputProcessor'
    })
    # 프롬프트 템플릿 설정
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{query}")
    ]).with_config({
        "runName": 'PromptTemplate'
    })

    # 체인 실행
    # chain = prompt | streaming_llm
    # chain = RunnableSequence([
    #     input_processor,
    #     prompt,
    #     streaming_llm,
    #     StrOutputParser().with_config({
    #         "runName": 'ResponseParser'
    #     })
    # ]).with_config({
    #     "runName": 'MainChain'
    # })
    chain = (
        input_processor | 
        prompt | 
        streaming_llm | 
        StrOutputParser().with_config(run_name="ResponseParser")
    ).with_config(
        run_name="FinalResponseGenerator"
    )
    
    task = asyncio.create_task(
        chain.ainvoke({
            "chat_history": history,
            "query": query
        })
    )

    async def stream_response():
        try:
            async for chunk in callback.aiter():
                print(chunk) #유용함
                content = chunk if isinstance(chunk, str) else chunk.content
                # 스트리밍 응답 포맷팅
                if not isinstance(content, str):
                    content = str(content)
                yield json.dumps({
                    "type": "response",
                    "data": content
                }) + "\n"
            
            # 스트림 종료 시그널
            yield json.dumps({"type": "end"}) + "\n"
        except Exception as e:
            print(f"Streaming error: {e}")
        finally:
            callback.done.set()

    return StreamingResponse(stream_response(), media_type="text/event-stream")

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    query = data.get("message", "")
    history = data.get("history", [])
    
    # 히스토리를 LangChain 메시지 형식으로 변환
    formatted_history = []
    print(len(history))
    if len(history) > 0:
        print(history)
        for msg in history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_history.append(SystemMessage(content=msg["content"]))

    llm = ChatOllama(
        model="phi3:latest",
        base_url='http://localhost:11434',
        streaming=True,
        temperature=0
    )
    return await create_answering_chain(llm, query, formatted_history)