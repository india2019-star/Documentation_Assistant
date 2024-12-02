import concurrent.futures
import string
from typing import List
from fastapi import File, UploadFile
from langchain_community.vectorstores import PGVector
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
from common_utilities import parse_documents_return_documents


def ingest(file_contents, collection_name, conn_string, file: UploadFile = File(...)):
    chunked_docs: List[Document] = parse_documents_return_documents(file_contents, file)
    _load_split_push(chunked_docs, collection_name, conn_string)

    return 1



def _load_split_push(chunked_docs: List[Document], collection_name: string, conn_string: string):
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large"
    )
    print("Starting ingestion...")
    print(f'\n{collection_name}\n')
    PGVector.from_documents(embedding=embeddings,
                            documents=chunked_docs,
                            collection_name=collection_name, 
                            connection_string=conn_string,
                            use_jsonb=True)
    print("Finished ingestion...")
    


def _process_pdfs(all_pdfs_path_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(_load_split_push, all_pdfs_path_list)



