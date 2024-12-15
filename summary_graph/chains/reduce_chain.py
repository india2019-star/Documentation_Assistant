from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts.summarization_custom_prompts import combined_summary_template

llm = ChatOllama(model="qwen2:0.5b", temperature=0)

reduce_prompt_template = PromptTemplate(
    template=combined_summary_template,
    input_variables=['summary_type', 'docs']
)

final_reduce_chain = (
    reduce_prompt_template 
    | llm 
    | StrOutputParser()
).with_config(
    tags=["final_reduce_chain"]
)