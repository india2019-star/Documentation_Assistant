from summary_graph.summary_state import GraphOverallSummaryState
from common_utilities import calc_max_token_cnt


async def assess_chain_type_func(state: GraphOverallSummaryState):
    token_cnt = calc_max_token_cnt(state['contents_in_doc_format'])
    chain_type=''
    if token_cnt > 3000:
        chain_type='map_reduce'
    else:
        chain_type='stuff'
    
    return {"chain_type": chain_type}
