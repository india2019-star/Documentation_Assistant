import asyncio
import json
from queue import Queue
from threading import Thread
from fastapi import File, UploadFile
import fastapi
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from handler import CustomCallBackHandler
from langchain.chains.summarize import load_summarize_chain
from common_utilities import parse_documents_return_documents
from prompts.summarization_custom_prompts import individual_summary_template, combined_summary_template



async def summary_streaming_generator_func(file_contents, summary_type: str,streamer_queue: Queue ,customHandler: CustomCallBackHandler, file: UploadFile = File(...)):

    thread = Thread(target=_generate_summary, kwargs={"file_contents": file_contents, 
                                                      "summary_type": summary_type,
                                                      "customHandler": customHandler,
                                                      "file": file})
    
    thread.start()

    while True:
        value = streamer_queue.get()
        print(f" {value} ")
        if value == None:
            break
        data_dict = {"data": value}
        data_json = json.dumps(data_dict.get("data"))
        yield f"data: {data_json}\n\n"
        streamer_queue.task_done()

        await asyncio.sleep(0.1)

def _generate_summary(file_contents, summary_type: str, customHandler: CustomCallBackHandler, file: UploadFile = File(...)):
    chunked_docs = parse_documents_return_documents(file_contents, file)
    print(len(chunked_docs))
    llm = ChatOllama(model="llama3.1:latest", temperature=0,callbacks=[customHandler], disable_streaming=False)
    individual_summary_prompt_template = PromptTemplate(
        template=individual_summary_template,
        input_variables=["text"]
    )

    combined_summary_prompt_template = PromptTemplate(
        template=combined_summary_template,
        input_variables=["summary_type" "text"]
    )

    chain = load_summarize_chain(
        llm=llm,
        chain_type='stuff',
        prompt=combined_summary_prompt_template,
        verbose=False
    )

    chain.invoke({"summary_type": summary_type, "input_documents": chunked_docs})

    
   

    