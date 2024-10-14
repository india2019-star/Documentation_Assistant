from langchain.callbacks.base import BaseCallbackHandler  
from langchain.schema.messages import BaseMessage  
from langchain.schema import LLMResult  
from typing import Dict, List, Any
from queue import Queue
from common_utilities import format_source_documents


class CustomCallBackHandler(BaseCallbackHandler):

    def __init__(self, queue) -> None:
        super().__init__()

        self._queue : Queue = queue
        self._stop_signal = None
        print("\n---Initialization Completed---\n")

    def on_llm_new_token(self, token, **kwargs):
        print(f"\n New Token => {token}\n")
        self._queue.put(token)

    def on_llm_end(self, response : LLMResult, **kwargs):
        print("\n\n---END---\n\n")
        self._queue.put(self._stop_signal)
    
    