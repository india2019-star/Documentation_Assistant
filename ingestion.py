import glob
import os
from pathlib import Path
import concurrent.futures
import string
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import PGVector
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings


def ingest():
    assets_folder = Path('assets')

    all_files = get_pdf_file_paths(assets_folder)
    for item in all_files:
        load_split_push(item)
    # process_pdfs(all_files)
    # embeddings = OllamaEmbeddings(
    #     model="mxbai-embed-large"
    # )
    # vector_result = embeddings.embed_query('When has the RAILWAY WOMEN\'S WELFARE CENTRAL ORGANISATION has decided to conduct the All India On SPot essay competition?')
    print('Done ingesting all')
    return 1



def load_split_push(filePath: string):
    filePathStr = str(filePath).replace('\\','/')
    pyMuPdfLoaderInstance = PyMuPDFLoader(filePathStr, extract_images=True)
    loaded_doc = pyMuPdfLoaderInstance.load()
    doc_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200,separator="\n", length_function=len)
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


def get_pdf_file_paths(folder_path):
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    return [os.path.abspath(pdf) for pdf in pdf_files]


def process_pdfs(all_pdfs_path_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(load_split_push, all_pdfs_path_list)



