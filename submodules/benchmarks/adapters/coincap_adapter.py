import requests
from .base_adapter import BaseAdapter

# TODO: this needs a coingecko_id -> coincap_id translation layer to be more accurate
# It mostly works as-is because coincap often shares the same identifier as coingecko
class CoincapAdapter(BaseAdapter):

    @property
    def name(self) -> str:
        return "Coincap"

    def get_price(self, coingecko_id: str) -> float:
        request_url = f"https://api.coincap.io/v2/rates/{coingecko_id}"
        response = requests.get(request_url)
        response.raise_for_status()
        data = response.json()
        price = float(data['data']['rateUsd'])
        return price

    def get_marketcap(self, coingecko_id: str) -> float:
        request_url = f"https://api.coincap.io/v2/assets/{coingecko_id}"
        response = requests.get(request_url)
        response.raise_for_status()
        data = response.json()
        marketcap = float(data['data']['marketCapUsd'])
        return marketcap

    def has_get_marketcap(self) -> bool:
        return True

    def has_get_price(self) -> bool:
        return True