from llama_cpp import Llama
from llama_cpp.llama_tokenizer import LlamaHFTokenizer
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from data_agent.src import tools
from config import Config
import json



tools_provided=tools.get_tools()
messages_ui=[]

def get_response(message,llm):
    global tools_provided
    messages=[{"role": "system", "content": "Don't make assumptions about the value of the arguments for the function thy should always be supplied by the user and do not alter the value of the arguments . Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."}]
    messages.extend(message)
    result = llm.create_chat_completion(
      messages = messages,
      tools=tools_provided,
      tool_choice="auto"
    )
    if "tool_calls" in result["choices"][0]["message"].keys():
        func=result["choices"][0]["message"]["tool_calls"][0]['function']
        if func["name"]=='get_price':
            args=json.loads(func["arguments"])
            return tools.get_coin_price_tool(args['coin_name']),"assistant"
        elif func["name"]=='get_floor_price':
            args=json.loads(func["arguments"])
            return tools.get_nft_floor_price_tool(args['nft_name']),"assistant"
        elif func["name"]=='get_fdv':
            args=json.loads(func["arguments"])
            return tools.get_fully_diluted_valuation_tool(args['coin_name']),"assistant"
        elif func["name"]=='get_tvl':
            args=json.loads(func["arguments"])
            return tools.get_protocol_total_value_locked_tool(args['protocol_name']),"assistant"
        elif func["name"]=='get_market_cap':
            args=json.loads(func["arguments"])
            return tools.get_coin_market_cap_tool(args['coin_name']),"assistant"
    return result["choices"][0]["message"]['content'],"assistant"

def generate_response(prompt,llm):
    global messages_ui
    messages_ui.append(prompt)
    response,role = get_response([prompt],llm)
    messages_ui.append({"role":role,"content":response})
    return response,role
    
def chat(request,llm):
    try:
        data = request.get_json()
        if 'prompt' in data:
            prompt = data['prompt']
            response,role = generate_response(prompt,llm)
            return jsonify({"role":role,"content":response})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    

def get_messages():
    global messages_ui
    return jsonify({"messages":messages_ui})

def clear_messages():
    global messages_ui
    messages_ui=[]
    return jsonify({"response":"successfully cleared message history"})
