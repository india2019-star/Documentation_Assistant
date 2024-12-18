from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts.summarization_custom_prompts import collapse_summary_template
from common_utilities import get_llm_for_answer

llm = get_llm_for_answer()

collapse_prompt_template = PromptTemplate(
    template=collapse_summary_template,
    input_variables=['docs']
)

collapse_summaries_chain = (
    collapse_prompt_template 
    | llm 
    | StrOutputParser()
).with_config(
    tags=["collapse_summaries_chain"]
)