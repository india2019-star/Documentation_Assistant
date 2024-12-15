from summary_graph.summary_state import GraphOverallSummaryState
from summary_graph.chains.reduce_chain import final_reduce_chain
from typing import List
from langchain.schema import Document

async def generate_final_summary_func(state: GraphOverallSummaryState):
    collapsed_summaries: List[Document] = state['collapsed_summaries']
    response = await final_reduce_chain.ainvoke({'summary_type': state['summary_type'], 'docs' : [item.page_content for item in collapsed_summaries]})
    return {"final_summary": response}