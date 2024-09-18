
import fastapi
from ingestion import ingest
from retrieval import retrieval_func
from schemas import chat_request, chat_response
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware

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
def process_and_retrieve(req : chat_request.ChatRequest):
    print(req)
    chat_history_tuple_list = []
    chat_history: List[Dict[str,str]] = req.chat_history
    for item in chat_history:
        for key, value in item.items():
            chat_history_tuple_list.append((key, value))
    print(chat_history_tuple_list)
    result = retrieval_func(req.question, chat_history_tuple_list)
    if(result and result["answer"]):
        print(result)
        return chat_response.ChatResponse(answer=result["answer"], responseCode=200, responseStatus="OK")
    raise fastapi.HTTPException(status_code=500, detail="SOME ERROR OCCURRED!!!!")





@app.get("/ingest-code", response_model= chat_response.ChatResponse)
def process_and_ingest():
    if(ingest() == 1):
        return chat_response.ChatResponse(answer="DONE", responseCode=200, responseStatus="OK")
    raise fastapi.HTTPException(status_code=500, detail="SOME ERROR OCCURRED!!!!")









            
        