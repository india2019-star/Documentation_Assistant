from summary_graph.summary_state import GraphOverallSummaryState
from summary_graph.chains.reduce_chain import final_reduce_chain
from typing import List
from langchain.schema import Document

async def generate_final_summary_func(state: GraphOverallSummaryState):
    final_collected_summaries: List[Document] = []
    if state['chain_type'] == "map_reduce":
        final_collected_summaries = state['collapsed_summaries']
    else:
        final_collected_summaries = state['contents_in_doc_format']
    response = await final_reduce_chain.ainvoke({'summary_type': state['summary_type'], 'docs' : [item.page_content for item in final_collected_summaries]})
    return {"final_summary": response}