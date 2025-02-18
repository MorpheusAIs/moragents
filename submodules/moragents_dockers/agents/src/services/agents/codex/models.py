from pydantic import BaseModel
from typing import Optional, List, Union, Any


class TokenMetadata(BaseModel):
    address: str
    createdAt: int
    decimals: int
    id: str
    imageBannerUrl: Optional[str]
    imageLargeUrl: Optional[str]
    imageSmallUrl: Optional[str]
    imageThumbUrl: Optional[str]
    isScam: Optional[bool]
    lastTransaction: int
    liquidity: str
    marketCap: Optional[str]
    name: str
    networkId: int
    price: float
    priceChange: float
    priceChange1: Optional[float]
    priceChange4: Optional[float]
    priceChange12: Optional[float]
    priceChange24: Optional[float]
    quoteToken: Optional[str]
    resolution: str
    symbol: str
    topPairId: str
    txnCount1: Optional[int]
    txnCount4: Optional[int]
    txnCount12: Optional[int]
    txnCount24: Optional[int]
    uniqueBuys1: Optional[int]
    uniqueBuys4: Optional[int]
    uniqueBuys12: Optional[int]
    uniqueBuys24: Optional[int]
    uniqueSells1: Optional[int]
    uniqueSells4: Optional[int]
    uniqueSells12: Optional[int]
    uniqueSells24: Optional[int]
    volume: str

    @property
    def formatted_response(self) -> str:
        formatted = f"## ${self.symbol} ({self.name})\n\n"
        formatted += f"Price: ${self.price:,.6f}\n"
        formatted += f"Market Cap: {self.marketCap or 'N/A'}\n"
        formatted += f"Liquidity: {self.liquidity}\n"
        formatted += f"24h Volume: {self.volume}\n\n"
        formatted += "**Price Changes**:\n"
        if self.priceChange1 is not None:
            formatted += f"- 1h: {self.priceChange1:+.2f}%\n"
        if self.priceChange4 is not None:
            formatted += f"- 4h: {self.priceChange4:+.2f}%\n"
        if self.priceChange12 is not None:
            formatted += f"- 12h: {self.priceChange12:+.2f}%\n"
        if self.priceChange24 is not None:
            formatted += f"- 24h: {self.priceChange24:+.2f}%\n"
        formatted += "\n"
        formatted += "**Transaction Activity**:\n"
        if self.txnCount24 is not None:
            formatted += f"- 24h Transactions: {self.txnCount24:,}\n"
        if self.uniqueBuys24 is not None and self.uniqueSells24 is not None:
            formatted += f"- 24h Unique Buyers: {self.uniqueBuys24:,}\n"
            formatted += f"- 24h Unique Sellers: {self.uniqueSells24:,}\n"
        formatted += "\n"
        formatted += f"Network ID: {self.networkId}\n"
        formatted += f"Contract: {self.address}\n\n"
        formatted += "---\n\n"
        return formatted


# *************
# Top Tokens Response
# *************


class TopTokensResponse(BaseModel):
    success: bool
    data: List[TokenMetadata]

    @property
    def formatted_response(self) -> str:
        if not self.success:
            return "Failed to get top tokens."

        if not self.data:
            return "No top tokens found."

        formatted = "# Top Trending Tokens\n\n"
        for token in self.data:
            formatted += token.formatted_response
        return formatted


# *************
# Top Holders Response
# *************


class TopHoldersResponse(BaseModel):
    success: bool
    data: float  # Percentage owned by top 10 holders

    @property
    def formatted_response(self) -> str:
        if not self.success:
            return "Failed to get top holders data."

        formatted = "# Token Holder Concentration\n\n"
        formatted += f"Top 10 holders own {self.data:.2f}% of the total supply.\n\n"

        # Add interpretation
        if self.data > 80:
            formatted += "⚠️ **High Concentration Warning**: "
            formatted += "Token ownership is highly concentrated, which could indicate higher volatility risk.\n"
        elif self.data > 50:
            formatted += "⚠️ **Moderate Concentration**: "
            formatted += "Token ownership shows notable concentration among top holders.\n"
        else:
            formatted += "✅ **Well Distributed**: "
            formatted += "Token ownership appears to be relatively well distributed.\n"

        return formatted


# *************
# Nft Search Response
# *************


class NftSearchItem(BaseModel):
    address: str
    average: str
    ceiling: str
    floor: str
    id: str
    imageUrl: Optional[str]
    name: Optional[str]
    networkId: int
    symbol: Optional[str]
    tradeCount: str
    tradeCountChange: float
    volume: str
    volumeChange: float
    window: str

    @property
    def formatted_response(self) -> str:
        formatted = f"## {self.name or 'Unnamed Collection'}\n\n"
        if self.symbol:
            formatted += f"Symbol: {self.symbol}\n"
        formatted += f"Floor Price: {self.floor}\n"
        formatted += f"Ceiling Price: {self.ceiling}\n"
        formatted += f"Average Price: {self.average}\n\n"
        formatted += "**Trading Activity**:\n"
        formatted += f"- Volume: {self.volume}\n"
        formatted += f"- Volume Change: {self.volumeChange:+.2f}%\n"
        formatted += f"- Trade Count: {self.tradeCount}\n"
        formatted += f"- Trade Count Change: {self.tradeCountChange:+.2f}%\n\n"
        formatted += f"Network ID: {self.networkId}\n"
        formatted += f"Contract: {self.address}\n\n"
        formatted += "---\n\n"
        return formatted


class NftSearchResponse(BaseModel):
    success: bool
    hasMore: int
    items: List[NftSearchItem]

    @property
    def formatted_response(self) -> str:
        if not self.success:
            return "Failed to search NFT collections."

        if not self.items:
            return "No NFT collections found matching your search."

        formatted = "# NFT Collection Search Results\n\n"
        for item in self.items:
            formatted += item.formatted_response

        if self.hasMore > 0:
            formatted += f"\n*{self.hasMore} more results available*\n"

        return formatted
