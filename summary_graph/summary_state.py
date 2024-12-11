import operator
from typing import List, TypedDict, Annotated


class GraphOverallSummaryState(TypedDict):
    summary_type: str
    contents: List[str]
    intermediate_summaries: Annotated[list, operator.add]
    final_summary: str


class GraphIndividualSummaryState(TypedDict):
    content: str