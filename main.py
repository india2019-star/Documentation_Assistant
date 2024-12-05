
from queue import Queue
import fastapi
import os
from handler import CustomCallBackHandler
from ingestion import ingest
from retrieval import retrieval_func
from schemas import chat_request, chat_response
from typing import List, Dict, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, Form, UploadFile
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from functionality import Functionality
from streaming_retrieval import response_generator_func
from summary_generator import summary_streaming_generator_func

load_dotenv(override=True)

DB_COLLECTION_NAME= os.getenv('POSTGRE_COLLECTION_NAME')
DB_CONN_STRING= os.getenv('POSTGRE_CONNECTION_STRING')

app = fastapi.FastAPI()

origins = [
    "http://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],
)


@app.post("/user-prompt", response_model=chat_response.ChatResponse)
async def process_and_retrieve(req : chat_request.ChatRequest):
    print(req)
    if req.question in ["Hi", "Hello"]:
        return chat_response.ChatResponse(answer="Hi there, How can I help you?", responseCode=200, responseStatus="OK", sourceDocuments="")
    elif req.question in ["Thanks", "Ok Thanks", "Bye", "Nice talking to you"]:
        return chat_response.ChatResponse(answer="Glad I could help, Bye Bye...", responseCode=200, responseStatus="OK", sourceDocuments="")
    
    chat_history_tuple_list = []
    chat_history: List[Dict[str,str]] = req.chat_history
    for item in chat_history:
        for key, value in item.items():
            chat_history_tuple_list.append((key, value))
    # return StreamingResponse(retrieval_func(req.question, chat_history_tuple_list), media_type="text/plain")
    result = await retrieval_func(req.question, DB_COLLECTION_NAME, DB_CONN_STRING, chat_history_tuple_list)
    return chat_response.ChatResponse(answer=result["answer"], responseCode=200, responseStatus="OK", sourceDocuments=result['source_documents'])



@app.post("/file-upload")
async def ingest_docs_and_insert(file: UploadFile = File(...)):
    if file is None:
        raise fastapi.HTTPException(status_code=404, detail="NO VALID FILE UPLOADED!!!")
    contents = await file.read()
    if(len(contents) == 0):
        raise fastapi.HTTPException(status_code=400, detail="UPLOADED FILE IS EMPTY!!!") 
    else:
        if(ingest(contents, DB_COLLECTION_NAME, DB_CONN_STRING, file) == 1):
            return {"filename" : file.filename}
    raise fastapi.HTTPException(status_code=500, detail="SOME ERROR OCCURRED!!!!")


@app.post("/streaming-test")
async def process_and_retrieve(req : chat_request.ChatRequest):
    print(req)
    streamer_queue = Queue()
    customHandler = CustomCallBackHandler(queue=streamer_queue)
    chat_history_tuple_list = []
    chat_history: List[Dict[str,str]] = req.chat_history
    for item in chat_history:
        for key, value in item.items():
            chat_history_tuple_list.append((key, value))
    return StreamingResponse(response_generator_func(req.question, chat_history_tuple_list, streamer_queue, customHandler), media_type="text/event-stream")
    # return chat_response.ChatResponse(answer=result["answer"], responseCode=200, responseStatus="OK", sourceDocuments=result['source_documents'])



@app.post("/summarization")
async def upload_and_summarize(file: UploadFile = File(...), summary_type: str = Form(...)):
    if file is None:
        raise fastapi.HTTPException(status_code=404, detail="NO VALID FILE UPLOADED!!!")
    contents = await file.read()
    if(len(contents) == 0):
        raise fastapi.HTTPException(status_code=400, detail="UPLOADED FILE IS EMPTY!!!") 
    else:
        print(f"\n{summary_type}\n")
        streamer_queue = Queue()
        customHandler = CustomCallBackHandler(queue=streamer_queue)
        # result = generate_summary(contents, summary_type, file)
        return StreamingResponse(summary_streaming_generator_func(contents, summary_type, streamer_queue, customHandler, file), media_type="text/event-stream")
    








            
        