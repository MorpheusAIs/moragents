from abc import ABC, abstractmethod


class BaseAdapter(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def get_price(self, coin_id: str) -> float:
        pass

    def get_marketcap(self, coin_id: str) -> float:
        pass

    def has_get_marketcap(self) -> bool:
        pass

    def has_get_price(self) -> bool:
        pass
