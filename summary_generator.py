from fastapi import File, UploadFile
import fastapi
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from common_utilities import parse_documents_return_documents
from prompts.summarization_custom_prompts import individual_summary_template, combined_summary_template

def generate_summary(file_contents, summary_type: str, file: UploadFile = File(...)):
    chunked_docs = parse_documents_return_documents(file_contents, file)
    print(len(chunked_docs))
    llm = ChatOllama(model="qwen2:0.5b", temperature=0)
    individual_summary_prompt_template = PromptTemplate(
        template=individual_summary_template,
        input_variables=["text"]
    )

    combined_summary_prompt_template = PromptTemplate(
        template=combined_summary_template,
        input_variables=["text"]
    )

    chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=individual_summary_prompt_template,
        combine_prompt=combined_summary_prompt_template,
        verbose=False
    )

    result = ""
    try:
        result= chain.invoke({"summary_type": summary_type, "input_documents": chunked_docs})
    except:
        raise fastapi.HTTPException(status_code=0, detail="SOME ERROR OCCURRED WHILE GENERATING RESPONSE!!!!")

    if result != "":
        return result['output_text']
    
    return ""

    