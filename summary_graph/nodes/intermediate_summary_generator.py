from summary_graph.summary_state import GraphIndividualSummaryState, GraphOverallSummaryState
from summary_graph.chains.map_chain import map_summaries_chain
from langgraph.constants import Send
from summary_graph.summary_consts import GENERATE_INTERMEDIATE_SUMMARY, GENERATE_FINAL_SUMMARY


async def generate_intermediate_summary_func(state: GraphIndividualSummaryState):
    response = await map_summaries_chain.ainvoke(state["content"])
    return {"intermediate_summaries": [response]}


def map_summaries(state: GraphOverallSummaryState):
    if (state["chain_type"] == "map_reduce"):
        return [
            Send(GENERATE_INTERMEDIATE_SUMMARY, {"content": content}) for content in state["contents"]
        ]
    else:
        return [
            GENERATE_FINAL_SUMMARY
        ]