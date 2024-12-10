import requests

from .base_adapter import BaseAdapter


class DefillamaAdapter(BaseAdapter):

    @property
    def name(self) -> str:
        return "Defillama"

    def get_price(self, coingecko_id: str) -> float:
        request_url = f"https://coins.llama.fi/prices/current/coingecko:{coingecko_id}"
        response = requests.get(request_url)
        response.raise_for_status()
        data = response.json()
        price = data["coins"][f"coingecko:{coingecko_id}"]["price"]
        return price

    def has_get_marketcap(self) -> bool:
        return False

    def has_get_price(self) -> bool:
        return True
