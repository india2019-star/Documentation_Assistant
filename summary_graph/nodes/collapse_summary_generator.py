from summary_graph.summary_state import GraphOverallSummaryState
from summary_graph.chains.collapse_chain import collapse_summaries_chain
from langchain.schema import Document
from langchain.chains.combine_documents.reduce import (
    acollapse_docs,
    split_list_of_docs,
)
from typing import List
from common_utilities import calc_max_token_cnt

async def generate_collapse_summary_func(state: GraphOverallSummaryState):
    doc_lists: List[List[Document]] = split_list_of_docs(
        state["collapsed_summaries"], calc_max_token_cnt, 3000
    )
    results = []
    for doc_list in doc_lists:
        results.append(Document(await collapse_summaries_chain.ainvoke({'docs' : [doc_list.page_content for item in doc_list]})))

    return {"collapsed_summaries": results}


def collect_summaries(state: GraphOverallSummaryState):
    return {
        "collapsed_summaries": [Document(page_content=summary) for summary in state["intermediate_summaries"]]
    }



