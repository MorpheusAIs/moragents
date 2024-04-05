import requests
import logging
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain.pydantic_v1 import BaseModel, Field
from langchain.agents import Tool
from config import Config

def get_most_similar(text, data):
    """Find the most similar item in a list of data to a given text."""
    vectorizer = TfidfVectorizer()
    vectorizer.fit(data)
    sentence_vectors = vectorizer.transform(data)
    text_vector = vectorizer.transform([text])
    similarity_scores = cosine_similarity(text_vector, sentence_vectors)
    top_indices = similarity_scores.argsort()[0][-20:][::-1]
    res = [data[item] for item in top_indices]
    sim = [SequenceMatcher(None, text, item).ratio() for item in res]
    max_index = max(range(len(sim)), key=sim.__getitem__)
    return res[max_index]

def get_coingecko_id(text, type="coin"):
    """Get the CoinGecko ID for a given coin or NFT."""
    url = f"{Config.COINGECKO_BASE_URL}/search"
    params = {"query": text}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if type == "coin":
            return data['coins'][0]['id'] if data['coins'] else None
        elif type == "nft":
            return data['nfts'][0]['id'] if data.get('nfts') else None
        else:
            raise ValueError("Invalid type specified")
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
        raise

def get_price(coin):
    """Get the price of a coin from CoinGecko API."""
    coin_id = get_coingecko_id(coin, type="coin")
    if not coin_id:
        return None
    url = f"{Config.COINGECKO_BASE_URL}/simple/price"
    params = {'ids': coin_id, 'vs_currencies': 'USD'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()[coin_id]['usd']
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve price: {str(e)}")
        raise

def get_floor_price(nft):
    """Get the floor price of an NFT from CoinGecko API."""
    nft_id = get_coingecko_id(str(nft), type="nft")
    if not nft_id:
        return None
    url = f"{Config.COINGECKO_BASE_URL}/nfts/{nft_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["floor_price"]["usd"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve floor price: {str(e)}")
        raise

def get_fdv(coin):
    """Get the fully diluted valuation of a coin from CoinGecko API."""
    coin_id = get_coingecko_id(coin, type="coin")
    if not coin_id:
        return None
    url = f"{Config.COINGECKO_BASE_URL}/coins/{coin_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("market_data", {}).get("fully_diluted_valuation", {}).get("usd")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve FDV: {str(e)}")
        raise

def get_market_cap(coin):
    """Get the market cap of a coin from CoinGecko API."""
    coin_id = get_coingecko_id(coin, type="coin")
    if not coin_id:
        return None
    url = f"{Config.COINGECKO_BASE_URL}/coins/markets"
    params = {'ids': coin_id, 'vs_currency': 'USD'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()[0]['market_cap']
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve market cap: {str(e)}")
        raise

def get_protocols_list():
    """Get the list of protocols from DefiLlama API."""
    url = f"{Config.DEFILLAMA_BASE_URL}/protocols"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [item['slug'] for item in data] ,[item['gecko_id'] for item in data]
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve protocols list: {str(e)}")
        raise

def get_protocol_tvl(protocol_name):
    """Get the TVL (Total Value Locked) of a protocol from DefiLlama API."""
    id,gecko = get_protocols_list()
    tag = get_coingecko_id(protocol_name)
    if not tag:
        return None
    protocol_id = next((i for i, j in zip(id, gecko) if j == tag), None)
    if not protocol_id:
        return None
    url = f"{Config.DEFILLAMA_BASE_URL}/tvl/{protocol_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve protocol TVL: {str(e)}")
        raise

class GetPrice(BaseModel):
    """Input schema for the get_coin_price_tool."""
    coin: str = Field(description="Name of the coin")

def get_coin_price_tool(coin_name):
    """Get the price of a cryptocurrency."""
    try:
        price = get_price(coin_name)
        if price is None:
            return Config.PRICE_FAILURE_MESSAGE
        return Config.PRICE_SUCCESS_MESSAGE.format(coin_name=coin_name, price=price)
    except requests.exceptions.RequestException:
        return Config.API_ERROR_MESSAGE

class GetFloorPrice(BaseModel):
    """Input schema for the get_nft_floor_price_tool."""
    nft: str = Field(description="Name of the NFT")

def get_nft_floor_price_tool(nft_name):
    """Get the floor price of an NFT."""
    try:
        floor_price = get_floor_price(nft_name)
        if floor_price is None:
            return Config.FLOOR_PRICE_FAILURE_MESSAGE
        return Config.FLOOR_PRICE_SUCCESS_MESSAGE.format(nft_name=nft_name, floor_price=floor_price)
    except requests.exceptions.RequestException:
        return Config.API_ERROR_MESSAGE

class GetTVL(BaseModel):
    """Input schema for the get_protocol_total_value_locked_tool."""
    protocol: str = Field(description="Name of the protocol")

def get_protocol_total_value_locked_tool(protocol_name):
    """Get the TVL (Total Value Locked) of a protocol."""
    try:
        tvl = get_protocol_tvl(protocol_name)
        if tvl is None:
            return Config.TVL_FAILURE_MESSAGE
        return Config.TVL_SUCCESS_MESSAGE.format(protocol_name=protocol_name, tvl=tvl)
    except requests.exceptions.RequestException:
        return Config.API_ERROR_MESSAGE

class GetFDV(BaseModel):
    """Input schema for the get_fully_diluted_valuation_tool."""
    coin: str = Field(description="Name of the coin")

def get_fully_diluted_valuation_tool(coin_name):
    """Get the fully diluted valuation of a coin."""
    try:
        fdv = get_fdv(coin_name)
        if fdv is None:
            return Config.FDV_FAILURE_MESSAGE
        return Config.FDV_SUCCESS_MESSAGE.format(coin_name=coin_name, fdv=fdv)
    except requests.exceptions.RequestException:
        return Config.API_ERROR_MESSAGE

class GetMarketCap(BaseModel):
    """Input schema for the get_coin_market_cap_tool."""
    coin: str = Field(description="Name of the coin")

def get_coin_market_cap_tool(coin_name):
    """Get the market cap of a coin."""
    try:
        market_cap = get_market_cap(coin_name)
        if market_cap is None:
            return Config.MARKET_CAP_FAILURE_MESSAGE
        return Config.MARKET_CAP_SUCCESS_MESSAGE.format(coin_name=coin_name, market_cap=market_cap)
    except requests.exceptions.RequestException:
        return Config.API_ERROR_MESSAGE

def get_tools():
    """Return a list of tools for the agent."""
    return [
        Tool(
            name="get_price",
            func=get_coin_price_tool,
            description="Get the price of a cryptocurrency",
            args_schema=GetPrice,
            return_direct=True
        ),
        Tool(
            name="get_floor_price",
            func=get_nft_floor_price_tool,
            description="Get the floor price of an NFT",
            args_schema=GetFloorPrice,
            return_direct=True
        ),
        Tool(
            name="get_tvl",
            func=get_protocol_total_value_locked_tool,
            description="Get the TVL of a protocol",
            args_schema=GetTVL,
            return_direct=True
        ),
        Tool(
            name="get_fdv",
            func=get_fully_diluted_valuation_tool,
            description="Get the fully diluted valuation of a coin",
            args_schema=GetFDV,
            return_direct=True
        ),
        Tool(
            name="get_market_cap",
            func=get_coin_market_cap_tool,
            description="Get the market cap of a coin",
            args_schema=GetMarketCap,
            return_direct=True
        )
    ]