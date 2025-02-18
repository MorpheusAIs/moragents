from typing import TypedDict, List, Optional


class TokenLink(TypedDict):
    type: str
    label: str
    url: str


class TokenProfile(TypedDict):
    url: str
    chainId: str
    tokenAddress: str
    icon: Optional[str]
    header: Optional[str]
    description: Optional[str]
    links: Optional[List[TokenLink]]


class BoostedToken(TokenProfile):
    amount: float
    totalAmount: float
