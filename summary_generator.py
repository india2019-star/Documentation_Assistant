from fastapi import File, UploadFile
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from common_utilities import parse_documents_return_documents
from prompts.summarization_custom_prompts import individual_summary_template, combined_summary_template

def generate_summary(file_contents, summary_type: str, file: UploadFile = File(...)):
    llm = ChatOllama(model="llama3.1", temperature=0)
    individual_summary_prompt_template = PromptTemplate(
        template=individual_summary_template,
        input_variables=["text"]
    )

    combined_summary_prompt_template = PromptTemplate(
        template=combined_summary_template,
        input_variables=["summary_type", "text"]
    )

    chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=individual_summary_prompt_template,
        combine_prompt=combined_summary_prompt_template,
        verbose=False
    )


    chunked_docs = parse_documents_return_documents(file_contents, file)

    result = chain.invoke({"summary_type": summary_type, "text":chunked_docs})
    print(result)
    return result

    