from flask import Flask, request, jsonify
from llama_cpp import Llama
from llama_cpp.llama_tokenizer import LlamaHFTokenizer
import requests
from swap_agent.src import tools
from swap_agent.src.tools import InsufficientFundsError, TokenNotFoundError, SwapNotPossibleError
from config import Config
import json


tools_provided = tools.get_tools()
messages = [{'role':"assistant","content":"This highly experimental chatbot is not intended for making important decisions, and its responses are generated based on incomplete data and algorithms that may evolve rapidly. By using this chatbot, you acknowledge that you use it at your own discretion and assume all risks associated with its limitations and potential errors."}]
context = []

def api_request_url(method_name, query_params, chain_id):
    base_url = Config.APIBASEURL + str(chain_id)
    return f"{base_url}{method_name}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"

def check_allowance(token_address, wallet_address, chain_id):
    url = api_request_url("/approve/allowance", {"tokenAddress": token_address, "walletAddress": wallet_address}, chain_id)
    response = requests.get(url, headers=Config.HEADERS)
    data = response.json()
    return data

def approve_transaction(token_address, chain_id, amount=None):
    query_params = {"tokenAddress": token_address, "amount": amount} if amount else {"tokenAddress": token_address}
    url = api_request_url("/approve/transaction", query_params, chain_id)
    response = requests.get(url, headers=Config.HEADERS)
    transaction = response.json()
    return transaction

def build_tx_for_swap(swap_params, chain_id):
    url = api_request_url("/swap", swap_params, chain_id)
    swap_transaction = requests.get(url, headers=Config.HEADERS).json()
    return swap_transaction

def get_response(message, chain_id, wallet_address,llm):
    global tools_provided , messages, context
    prompt = [{"role": "system", "content": "Don't make assumptions about the value of the arguments for the function they should always be supplied by the user and do not alter the value of the arguments. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. you only need the value of token1 we dont need the value of token2. After starting from scratch do not assume the name of token1 or token2"}]
    prompt.extend(message)
    result = llm.create_chat_completion(
      messages=prompt,
      tools=tools_provided,
      tool_choice="auto",
      temperature=0.01
    )
    if "tool_calls" in result["choices"][0]["message"].keys():
        func = result["choices"][0]["message"]["tool_calls"][0]['function']
        if func["name"] == "swap_agent":
            args = json.loads(func["arguments"])
            tok1 = args["token1"]
            tok2 = args["token2"]
            value = args["value"]
            try:
                res, role = tools.swap_coins(tok1, tok2, float(value), chain_id, wallet_address)
                messages.append({"role": role, "content": res})
            except (tools.InsufficientFundsError, tools.TokenNotFoundError,tools.SwapNotPossibleError) as e:
                context = []
                messages.append({"role": "assistant", "content": str(e)})
                return str(e), "assistant"
            return res, role
    messages.append({"role": "assistant", "content": result["choices"][0]["message"]['content']})
    context.append({"role": "assistant", "content": result["choices"][0]["message"]['content']})
    return result["choices"][0]["message"]['content'], "assistant"

def get_status(flag, tx_hash, tx_type):
    global messages, context
    response = ''
    
    if flag == "cancelled":
        response = f"The {tx_type} transaction has been cancelled."
    elif flag == "success":
        response = f"The {tx_type} transaction was successful."
    elif flag == "failed":
        response = f"The {tx_type} transaction has failed."
    elif flag == "initiated":
        response = f"Transaction has been sent, please wait for it to be confirmed."

    if tx_hash:
        response = response + f" The transaction hash is {tx_hash}."
    
    if flag == "success" and tx_type == "approve":  
        response = response + " Please proceed with the swap transaction."
    elif flag != "initiated":
        response = response + " Is there anything else I can help you with?"

    if flag != "initiated":
        context = []
        messages.append({"role": "assistant", "content": response})
        context.append({"role": "assistant", "content": response})
        context.append({"role": "user", "content": "okay lets start again from scratch"})
    else:
        messages.append({"role": "assistant", "content": response})
    
    return response

def generate_response(prompt,chainid,walletAddress,llm):
    global messages,context
    messages.append(prompt)
    context.append(prompt)
    response,role = get_response(context,chainid,walletAddress,llm)
    return response,role

    
def chat(request,llm):
    try:
        data = request.get_json()
        if 'prompt' in data:
            prompt = data['prompt']
            wallet_address = data['wallet_address']
            chain_id = data['chain_id']
            response, role = generate_response(prompt, chain_id, wallet_address,llm)
            return jsonify({"role": role, "content": response})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500     


def tx_status(request):
    try:
        data = request.get_json()
        if 'status' in data:
            prompt = data['status']
            tx_hash = data.get('tx_hash', '')
            tx_type = data.get('tx_type', '')
            response = get_status(prompt, tx_hash, tx_type)
            return jsonify({"role": "assistant", "content": response})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 

def get_messages():
    global messages
    try:
        return jsonify({"messages": messages})
    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    
def clear_messages():
    global messages, context
    try:
        messages = [{'role':"assistant","content":"This highly experimental chatbot is not intended for making important decisions, and its responses are generated based on incomplete data and algorithms that may evolve rapidly. By using this chatbot, you acknowledge that you use it at your own discretion and assume all risks associated with its limitations and potential errors."}]
        context = []
        return jsonify({"response": "successfully cleared message history"})
    except Exception as e:
        return jsonify({"Error": str(e)}), 500 

def get_allowance(request):
    try:
        data = request.get_json()
        if 'tokenAddress' in data:
            token = data['tokenAddress']
            wallet_address = data['walletAddress']
            chain_id = data["chain_id"]
            res = check_allowance(token, wallet_address, chain_id)
            return jsonify({"response": res})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 

def approve(request):
    try:
        data = request.get_json()
        if 'tokenAddress' in data:
            token = data['tokenAddress']
            chain_id = data['chain_id']
            amount = data['amount']
            res = approve_transaction(token, chain_id, amount)
            return jsonify({"response": res})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 
    
def swap(request):   
    try:
        data = request.get_json()
        if 'src' in data:  
            token1 = data['src']
            token2 = data['dst']
            wallet_address = data['walletAddress']
            amount = data['amount']
            slippage = data['slippage']
            chain_id = data['chain_id']
            swap_params = {
                "src": token1,
                "dst": token2,
                "amount": amount,
                "from": wallet_address,
                "slippage": slippage,
                "disableEstimate": False,
                "allowPartialFill": False,
            }
            swap_transaction = build_tx_for_swap(swap_params, chain_id)
            return swap_transaction
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500 