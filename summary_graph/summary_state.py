import operator
from typing import List, TypedDict, Annotated
from langchain.schema import Document


class GraphOverallSummaryState(TypedDict):
    chain_type: str
    summary_type: str
    contents: List[str]
    contents_in_doc_format: List[Document]
    collapsed_summaries: List[Document]
    intermediate_summaries: Annotated[list, operator.add]
    final_summary: str


class GraphIndividualSummaryState(TypedDict):
    content: str