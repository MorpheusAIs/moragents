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
        return hasattr(self, 'get_marketcap') and callable(getattr(self, 'get_marketcap'))

    def has_get_price(self) -> bool:
        return hasattr(self, 'get_price') and callable(getattr(self, 'get_price'))
