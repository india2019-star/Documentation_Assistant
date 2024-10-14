import os
import asyncio
import fastapi
import json
from queue import Queue
from threading import Thread
from langchain_ollama import ChatOllama, OllamaEmbeddings
from common_utilities import format_source_documents
from handler import CustomCallBackHandler
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_community.vectorstores import PGVector
from langchain_core.messages import AIMessageChunk
from langchain import hub
from typing import List, Dict



async def response_generator_func(question, chat_history: List[Dict[str, str]], streamer_queue : Queue, customHandler : CustomCallBackHandler):

    thread = Thread(target=streaming_retrieval_func, kwargs={"question": question, 
                                                             "chat_history": chat_history,
                                                             "customHandler": customHandler})
    
    thread.start()

    while True:
        value = streamer_queue.get()
        if value == None:
            break
        data_dict = {"data": value}
        data_json = json.dumps(data_dict)
        yield f"data: {data_json}\n\n"
        streamer_queue.task_done()

        await asyncio.sleep(0.1)



def streaming_retrieval_func(question, chat_history: List[Dict[str, str]], customHandler : CustomCallBackHandler):
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large"
    )
    

    llm = ChatOllama(model="qwen2.5:0.5b", temperature=0,callbacks=[customHandler], disable_streaming=False)
    vector_store_retriever = PGVector(connection_string=os.environ['POSTGRE_CONNECTION_STRING'],
                            collection_name=os.environ['POSTGRE_COLLECTION_NAME'],
                            embedding_function=embeddings).as_retriever(search_type="similarity_score_threshold",search_kwargs={
                                                                                                "k": 5,
                                                                                                "score_threshold": 0.61})
    

    
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_stuff_documents = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
    history_chat_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    history_retrieval_chat = create_history_aware_retriever(
        llm, vector_store_retriever, history_chat_prompt
    )
    retrieval_chain = create_retrieval_chain(
        history_retrieval_chat, combine_docs_chain=combine_stuff_documents
    )
    result = retrieval_chain.invoke(input={"input":question, "chat_history": chat_history})
    # chunk_result = ""
    # async for event in retrieval_chain.astream_events(
    #     input={"input":question, "chat_history": chat_history},
    #     version="v2"
    # ):
    #     if "data" in event and "chunk" in event["data"]:
    #         chunk_result = serialize_chunks(event["data"]["chunk"])
    #         if chunk_result is not None and  len(chunk_result) != 0:
    #                 data_dict = {"data": chunk_result}
    #                 data_json = json.dumps(data_dict)
    #                 yield f"data: {data_json}\n\n"



        
    # if(not result):
    #     raise fastapi.HTTPException(status_code=500, detail="INTERNAL SERVER ERROR")
    
    
    # return {
    #     "question" : question,
    #     "answer" : result["answer"], 
    #     "source_documents" : format_source_documents(result["context"])
    # }



def serialize_chunks(chunk):
    print(chunk)
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    else:
        fastapi.HTTPException(status_code=404, detail="Unformatted type")


