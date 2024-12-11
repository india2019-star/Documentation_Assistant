from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts.summarization_custom_prompts import individual_summary_template

llm = ChatOllama(model="qwen2:0.5b", temperature=0)

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