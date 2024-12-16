from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts.summarization_custom_prompts import combined_summary_template
from common_utilities import get_llm_for_answer

llm = get_llm_for_answer()

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