from pydantic import BaseModel
from typing import List, Dict

class ChatRequest(BaseModel):
    question : str
    chat_history : List[Dict[str, str]]