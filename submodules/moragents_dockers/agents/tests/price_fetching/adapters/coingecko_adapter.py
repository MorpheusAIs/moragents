import requests

from .base_adapter import BaseAdapter


# defillama and coingecko share the same identifiers
class CoingeckoAdapter(BaseAdapter):

    @property
    def name(self) -> str:
        return "Coingecko"

    def get_price(self, coingecko_id: str) -> float:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coingecko_id, "vs_currencies": "usd"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()[coingecko_id]["usd"]

    def get_marketcap(self, coin_id: str) -> float:
        request_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        response = requests.get(request_url)
        response.raise_for_status()
        data = response.json()
        marketcap = data["market_data"]["market_cap"]["usd"]
        return marketcap

    def has_get_marketcap(self) -> bool:
        return True

    def has_get_price(self) -> bool:
        return True
