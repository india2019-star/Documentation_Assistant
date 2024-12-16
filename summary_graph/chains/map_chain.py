from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts.summarization_custom_prompts import individual_summary_template
from common_utilities import get_llm_for_answer

llm = get_llm_for_answer()

map_prompt_template = PromptTemplate(
    template=individual_summary_template,
    input_variables=['text']
)

map_summaries_chain = (
    map_prompt_template 
    | llm 
    | StrOutputParser()
).with_config(
    tags=["map_summaries_chain"]
)