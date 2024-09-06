import glob
import os
from pathlib import Path
import concurrent.futures
import string
from langchain_community.document_loaders import PyPDFLoader
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from pinecone import Pinecone

pc = Pinecone(
    api_key=os.environ['PINECONE_API_KEY']
)
index = pc.Index(os.environ['INDEX_NAME4'])

def ingest(index_name):
    assets_folder = Path('assets')

    all_files = get_pdf_file_paths(assets_folder)
    all_vectors = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for result in executor.map(load_split_push, all_files):
            all_vectors.append(result)
    
    # ingest_vectors_in_batches(all_vectors, 5)
    print('Done ingesting all')
    return 1



def load_split_push(filePath: string):
    filePathStr = str(filePath).replace('\\','/')
    pyPdfLoaderInstance = PyPDFLoader(filePathStr)
    loaded_doc = pyPdfLoaderInstance.load()
    doc_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200,separator="\n", length_function=len)
    splitted_docs = doc_splitter.split_documents(documents=loaded_doc)
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )



    vectors = []
    cnt = 0
    for doc in splitted_docs:
        text = doc.page_content
        metadata = {"source": filePathStr}
        
        embedding = embeddings.embed_query(text)
        
        vectors.append((f"{filePathStr}-{cnt}", embedding, metadata))
        cnt = cnt+1

    # print("Starting ingestion...")
    # PineconeVectorStore.from_documents(splitted_docs,embeddings,index_name=index_name)
    # print("Finished ingestion...")
    return vectors


def ingest_vectors_in_batches(vectors,batch_size=5):
    
    for i in range(0,len(vectors), batch_size):
        batches = vectors[i:i + batch_size]
        for j in batches:
            index.upsert(vectors=j)
        
def get_pdf_file_paths(folder_path):
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    return [os.path.abspath(pdf) for pdf in pdf_files]



