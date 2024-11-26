import os
import gc
import pytesseract
from pathlib import Path
import concurrent.futures
import string
import pypdfium2 as pdfium
from PIL import Image
from io import BytesIO
from pytesseract import image_to_string
from fastapi import File, UploadFile
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def ingest(file_contents, collection_name, conn_string, file: UploadFile = File(...)):
    assets_folder = Path('temp_store')

    uploaded_file_location = _get_pdf_file_paths(assets_folder, file_contents, file)
    print(uploaded_file_location)
    _load_split_push(uploaded_file_location, collection_name, conn_string)
    if(os.path.isfile(uploaded_file_location)):
        try:
            os.remove(uploaded_file_location)
            print(f"File with path: {uploaded_file_location} removed successfully...")
        except:
            print(f"Permission Denied...")
    return 1



def _load_split_push(filePath: string, collection_name: string, conn_string: string):
    filePathStr = str(filePath).replace('\\','/')
    converted_result_from_pdf_to_image = _convert_entire_pdf_to_image(filePathStr)
    extracted_text_from_image = _extract_text_with_pytesseract(converted_result_from_pdf_to_image)
    recursive_text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
    splitted_texts = recursive_text_splitter.split_text(extracted_text_from_image)
    documents_from_splitted_texts = [Document(page_content=text_item, metadata={"source": filePathStr, "page_number": i+1})  
                                         for i, text_item in enumerate(splitted_texts)]


    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large"
    )
    print("Starting ingestion...")
    print(f'\n{collection_name}\n')
    PGVector.from_documents(embedding=embeddings,
                            documents=documents_from_splitted_texts,
                            collection_name=collection_name, 
                            connection_string=conn_string,
                            use_jsonb=True)
    print("Finished ingestion...")
    


def _get_pdf_file_paths(folder_path,file_contents, file : UploadFile = File(...)):
    file_location = os.path.join(folder_path, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(file_contents)
    gc.collect()
    print("File closed:", buffer.closed)
    return file_location

def _convert_entire_pdf_to_image(file_path: str, scale=300/72):
    final_list_of_images = []
    loaded_doc = pdfium.PdfDocument(file_path)
    
    pdf_indices_list = [i for i in range(len(loaded_doc))]
    renderer = loaded_doc.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=pdf_indices_list,
        scale=scale
    )
    
    for index, image in zip(pdf_indices_list, renderer):
        image_byte_array = BytesIO()
        image.save(image_byte_array, format='jpeg', optimize=True)
        image_byte_array = image_byte_array.getvalue()
        final_list_of_images.append(dict({index: image_byte_array}))
    loaded_doc.close()
    return final_list_of_images


def _extract_text_with_pytesseract(list_dict_final_images):
    
    image_list = [list(data.values())[0] for data in list_dict_final_images]
    image_content = []
    
    for index, image_bytes in enumerate(image_list):
        
        image = Image.open(BytesIO(image_bytes))
        raw_text = str(image_to_string(image))
        image_content.append(raw_text)
    
    return "\n".join(image_content)



def _process_pdfs(all_pdfs_path_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(_load_split_push, all_pdfs_path_list)



