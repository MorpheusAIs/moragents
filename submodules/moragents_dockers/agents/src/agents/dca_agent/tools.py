import logging
from typing import Dict, Optional, Any
from datetime import timedelta
from dataclasses import dataclass
from decimal import Decimal
from src.stores import wallet_manager_instance
from src.agents.base_agent.tools import get_balance, swap_assets

logger = logging.getLogger(__name__)


@dataclass
class DCAParams:
    """Parameters for DCA strategy"""

    origin_token: str
    destination_token: str
    step_size: Decimal
    total_investment_amount: Optional[Decimal] = None
    frequency: str = "weekly"
    max_purchase_amount: Optional[Decimal] = None
    price_threshold: Optional[Decimal] = None
    pause_on_volatility: bool = False
    wallet_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "origin_token": self.origin_token,
            "destination_token": self.destination_token,
            "step_size": str(self.step_size),
            "total_investment_amount": (
                str(self.total_investment_amount) if self.total_investment_amount else None
            ),
            "frequency": self.frequency,
            "max_purchase_amount": (
                str(self.max_purchase_amount) if self.max_purchase_amount else None
            ),
            "price_threshold": str(self.price_threshold) if self.price_threshold else None,
            "pause_on_volatility": self.pause_on_volatility,
            "wallet_id": self.wallet_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DCAParams":
        return cls(
            origin_token=data["origin_token"].lower(),
            destination_token=data["destination_token"].lower(),
            step_size=Decimal(data["step_size"]),
            total_investment_amount=(
                Decimal(data["total_investment_amount"])
                if data.get("total_investment_amount")
                else None
            ),
            frequency=data["frequency"],
            max_purchase_amount=(
                Decimal(data["max_purchase_amount"]) if data.get("max_purchase_amount") else None
            ),
            price_threshold=(
                Decimal(data["price_threshold"]) if data.get("price_threshold") else None
            ),
            pause_on_volatility=data.get("pause_on_volatility", False),
            wallet_id=data.get("wallet_id"),
        )


class DCAActionHandler:
    """Handles DCA workflow actions"""

    def __init__(self):
        self.wallet_manager = wallet_manager_instance

    async def execute(self, params: Dict[str, Any]) -> None:
        """Execute DCA trade"""
        try:
            dca_params = DCAParams.from_dict(params)

            # Get wallet
            if not dca_params.wallet_id:
                raise ValueError("Wallet ID is required")

            wallet = self.wallet_manager.get_wallet(dca_params.wallet_id)
            if not wallet:
                raise ValueError(f"Wallet {dca_params.wallet_id} not found")

            # Check balance
            balance_result = get_balance(wallet, dca_params.origin_token)
            if Decimal(balance_result["balance"]) < dca_params.step_size:
                raise ValueError(f"Insufficient {dca_params.origin_token} balance")

            # TODO: Re-enable check price threshold
            # price = await wallet.get_token_price(dca_params.destination_token)
            # if dca_params.price_threshold and price > dca_params.price_threshold:
            #     logger.info(
            #         f"Price {price} above threshold {dca_params.price_threshold}, skipping trade"
            #     )
            #     return

            # TODO: Re-enable check for volatility if enabled
            # if dca_params.pause_on_volatility:
            #     volatility = await self._check_volatility(wallet, dca_params.destination_token)
            #     if volatility > 0.1:  # 10% threshold
            #         logger.info(f"High volatility detected ({volatility}), skipping trade")
            #         return

            # Execute trade using swap_assets
            swap_assets(
                agent_wallet=wallet,
                amount=str(dca_params.step_size),
                from_asset_id=dca_params.origin_token,
                to_asset_id=dca_params.destination_token,
            )

            logger.info(f"DCA trade executed successfully")

        except Exception as e:
            logger.error(f"DCA execution failed: {e}")
            raise

    async def _check_volatility(self, wallet, token: str) -> float:
        """Check price volatility over last 24h"""
        try:
            # Get 24h price data
            prices = await wallet.get_price_history(token, interval="1h", periods=24)

            if not prices:
                return 0

            # Calculate volatility
            mean = sum(prices) / len(prices)
            variance = sum((p - mean) ** 2 for p in prices) / len(prices)
            volatility = (variance**0.5) / mean

            return float(volatility)

        except Exception as e:
            logger.error(f"Failed to check volatility: {e}")
            return 0


def get_frequency_seconds(frequency: str) -> int:
    """Convert frequency string to seconds"""
    frequencies = {
        "minute": 60,
        "hourly": 3600,
        "daily": 86400,
        "weekly": 604800,
        "biweekly": 1209600,
        "monthly": 2592000,
    }
    return frequencies.get(frequency, 86400)


def create_dca_workflow(params: DCAParams) -> Dict[str, Any]:
    """Create workflow configuration for DCA strategy"""
    return {
        "name": f"DCA {params.origin_token} to {params.destination_token}",
        "description": f"Dollar cost average from {params.origin_token} to {params.destination_token}",
        "action": "dca_trade",
        "params": params.to_dict(),
        "interval": timedelta(seconds=get_frequency_seconds(params.frequency)),
    }
