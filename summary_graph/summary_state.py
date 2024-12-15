import operator
from typing import List, TypedDict, Annotated
from langchain.schema import Document


class GraphOverallSummaryState(TypedDict):
    summary_type: str
    contents: List[str]
    collapsed_summaries: List[Document]
    intermediate_summaries: Annotated[list, operator.add]
    final_summary: str


class GraphIndividualSummaryState(TypedDict):
    content: str