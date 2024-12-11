import json
from fastapi import File, UploadFile
from common_utilities import serialize_message_chunk_while_streaming
from langgraph.graph import START, END, StateGraph
from common_utilities import parse_documents_return_documents
from summary_graph.summary_state import GraphOverallSummaryState
from summary_graph.summary_consts import GENERATE_FINAL_SUMMARY, GENERATE_INTERMEDIATE_SUMMARY
from summary_graph.nodes import map_summaries, generate_intermediate_summary_func, generate_final_summary_func

async def summary_generation_langgraph(file_contents, summary_type: str, file: UploadFile = File(...)):


    builder = StateGraph(GraphOverallSummaryState)

    builder.add_node(GENERATE_INTERMEDIATE_SUMMARY, generate_intermediate_summary_func)
    builder.add_node(GENERATE_FINAL_SUMMARY, generate_final_summary_func)

    builder.add_conditional_edges(START,map_summaries,[GENERATE_INTERMEDIATE_SUMMARY])
    builder.add_edge(GENERATE_INTERMEDIATE_SUMMARY, GENERATE_FINAL_SUMMARY)
    builder.add_edge(GENERATE_FINAL_SUMMARY, END)


    graph = builder.compile()

    # graph.get_graph().draw_mermaid_png(output_file_path="summary_generation_graph.png")

    parsed_docs_result = parse_documents_return_documents(file_contents, file)

    chunked_docs = parsed_docs_result["documents_from_splitted_texts"]

    async for event in graph.astream_events({"summary_type": summary_type, "contents": [item.page_content for item in chunked_docs]}, version='v2'):
        sources_tags = ["seq:step:2", "final_reduce_chain"]

        if  all(val in event["tags"] for val in sources_tags) and  event["event"] == "on_chat_model_stream":
            chunk_content = serialize_message_chunk_while_streaming(event["data"]["chunk"])
            data_dict = {"data" : chunk_content}
            data_json = json.dumps(data_dict.get("data"))
            yield f"data: {data_json}\n\n"








