import glob
import os
from pathlib import Path
import concurrent.futures
import string
from fastapi import File, UploadFile
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings


def ingest(file_contents, file: UploadFile = File(...)):
    assets_folder = Path('temp_store')

    uploaded_file_location = get_pdf_file_paths(assets_folder, file_contents, file)
    print(uploaded_file_location)
    load_split_push(uploaded_file_location)
    return 1



def load_split_push(filePath: string):
    filePathStr = str(filePath).replace('\\','/')
    pyMuPdfLoaderInstance = PyMuPDFLoader(filePathStr, extract_images=True)
    loaded_doc = pyMuPdfLoaderInstance.load()
    doc_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    splitted_docs = doc_splitter.split_documents(documents=loaded_doc)
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large"
    )
    print("Starting ingestion...")
    PGVector.from_documents(embedding=embeddings,
                            documents=splitted_docs,
                            collection_name=os.environ['POSTGRE_COLLECTION_NAME'], 
                            connection_string=os.environ['POSTGRE_CONNECTION_STRING'],
                            use_jsonb=True)
    print("Finished ingestion...")
    if(os.path.isfile(filePath)):
        os.remove(filePath)
        print(f"File with path: {filePath} removed successfully...")


def get_pdf_file_paths(folder_path,file_contents, file : UploadFile = File(...)):
    file_location = os.path.join(folder_path, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(file_contents)
    
    return file_location


def process_pdfs(all_pdfs_path_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(load_split_push, all_pdfs_path_list)



