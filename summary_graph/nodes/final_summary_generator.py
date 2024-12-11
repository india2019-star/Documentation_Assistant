from summary_graph.summary_state import GraphOverallSummaryState
from summary_graph.chains.reduce_chain import final_reduce_chain

async def generate_final_summary_func(state: GraphOverallSummaryState):
    response = await final_reduce_chain.ainvoke({'summary_type': state['summary_type'], 'docs' : state['intermediate_summaries']})
    return {"final_summary": response}