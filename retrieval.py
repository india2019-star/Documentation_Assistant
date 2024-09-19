from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_community.vectorstores import PGVector
from langchain import hub
from typing import List, Dict
import os
import fastapi


def retrieval_func(question, chat_history: List[Dict[str, str]] = []):
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large"
    )

    llm = ChatOllama(model="qwen2:0.5b", temperature=0)
    vector_store = PGVector(connection_string=os.environ['POSTGRE_CONNECTION_STRING'],
                            collection_name=os.environ['POSTGRE_COLLECTION_NAME'],
                            embedding_function=embeddings)
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_stuff_documents = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
    history_chat_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    history_retrieval_chat = create_history_aware_retriever(
        llm, vector_store.as_retriever(search_kwargs={"k": 2}), history_chat_prompt
    )
    retrieval_chain = create_retrieval_chain(
        history_retrieval_chat, combine_docs_chain=combine_stuff_documents
    )
    result = retrieval_chain.invoke(input={"input":question, "chat_history": chat_history})
    if(not result):
        raise fastapi.HTTPException(status_code=500, detail="INTERNAL SERVER ERROR")
    print(result)
    return {
        "question" : question,
        "answer" : result["answer"],
        "source_documents" : format_source_documents(result["context"])
    }

def format_source_documents(context):
    source_docs = set([item.metadata['source']  for item in context])
    if not source_docs:
        return ""
    source_docs_list = list(source_docs)
    source_docs_list.sort()
    source_docs_in_string_format = "Sources:\n"
    for index, item in enumerate(source_docs_list):
        source_docs_in_string_format += f"{index + 1}. {item}\n"
    return source_docs_in_string_format

