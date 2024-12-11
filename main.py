
from pathlib import Path
from queue import Queue
import fastapi
import os
from handler import CustomCallBackHandler
from ingestion import ingest
from retrieval import retrieval_func
from schemas import chat_request, chat_response
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, Form, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from dotenv import load_dotenv
from streaming_retrieval import response_generator_func
from summary_graph.summ_graph_builder import  summary_generation_langgraph

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
        ingestion_result = ingest(contents, DB_COLLECTION_NAME, DB_CONN_STRING, file)
        if(ingestion_result != ''):
            return {"filename" : file.filename,
                    "download_url" : ingestion_result}
    raise fastapi.HTTPException(status_code=500, detail="SOME ERROR OCCURRED!!!!")


@app.get("/download/{file_name}")
async def download_file(file_name: str):

    download_file_path = Path('doc_format_store') / file_name

    print(f"\nDOWNLOAD FILE PATH -->{download_file_path}\n")

    if download_file_path.exists():
        return FileResponse(
            path=download_file_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=file_name
        )
    else:
        raise fastapi.HTTPException(status_code=404, detail="FILE NOT FOUND!!!!")



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
        return StreamingResponse(summary_generation_langgraph(contents, summary_type, file), media_type="text/event-stream")
    








            
        