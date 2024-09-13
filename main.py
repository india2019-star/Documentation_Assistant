import os
import json

from ingestion import ingest
from retrieval import retrieval_func
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/user-prompt", methods=["POST"])
def process_and_retrieve():
    input_prompt = request.get_json()
    chat_history_tuple_list = []
    chat_history: list[dict[str,any]] = input_prompt["chatHistory"]
    for item in chat_history:
        for key, value in item.items():
            chat_history_tuple_list.append((key, value))
    print(chat_history_tuple_list)
    result = retrieval_func(input_prompt["question"], chat_history_tuple_list)
    if(result and result["answer"]):
        print(result)
        return jsonify(result["answer"]), 200
    return jsonify("Internal Server Error"), 500



@app.route("/")
def home():
    return "Home"

@app.route("/ingest-code")
def process_and_ingest():
    if(ingest() == 1):
        return jsonify("OK"),200
    return jsonify("INTERNAL SERVER ERROR"), 500 





if __name__ == '__main__':
    app.run(debug=True)
    # f = True
    # if(f == False):
    #    ingest(INDEX_NAME)


    # while(True):
    #     print("---------------------------MENU------------------------------------\n\n")
    #     print("1. Documentation assistant\n")
    #     print("0. Exit\n")
    #     ch = int(input("Enter your choice\n"))

    #     if(ch == 1):
    #         question = input("Enter your question...\n")
    #         retrieval_func(INDEX_NAME, question)
    #     elif(ch == 0):
    #         print("Thank you for using this utility...\n")
    #         break





            
        