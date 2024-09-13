from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_community.vectorstores import PGVector
from langchain import hub
import os


def retrieval_func(question, chat_history: list[dict[str, any]] = []):
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
        llm, vector_store.as_retriever(search_kwargs={"k": 1}), history_chat_prompt
    )
    retrieval_chain = create_retrieval_chain(
        history_retrieval_chat, combine_docs_chain=combine_stuff_documents
    )
    result = retrieval_chain.invoke(input={"input":question, "chat_history": chat_history})
    print(result)
    return result
