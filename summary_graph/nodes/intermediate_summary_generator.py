from summary_graph.summary_state import GraphIndividualSummaryState, GraphOverallSummaryState
from summary_graph.chains.map_chain import map_summaries_chain
from langgraph.constants import Send
from summary_graph.summary_consts import GENERATE_INTERMEDIATE_SUMMARY


async def generate_intermediate_summary_func(state: GraphIndividualSummaryState):
    response = await map_summaries_chain.ainvoke(state["content"])
    return {"intermediate_summaries": [response]}


def map_summaries(state: GraphOverallSummaryState):
    # We will return a list of `Send` objects
    # Each `Send` object consists of the name of a node in the graph
    # as well as the state to send to that node
    return [
        Send(GENERATE_INTERMEDIATE_SUMMARY, {"content": content}) for content in state["contents"]
    ]