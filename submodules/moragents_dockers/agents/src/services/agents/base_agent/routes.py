import logging
from decimal import Decimal
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.stores import wallet_manager_instance
from src.agents.base_agent.tools import swap_assets, transfer_asset

router = APIRouter(prefix="/base", tags=["base"])
logger = logging.getLogger(__name__)


@router.post("/swap")
async def swap(data: dict):
    """Swap one asset for another"""
    try:
        logger.info(f"Base Agent: Received swap request with data: {data}")

        # Get active wallet
        wallet = wallet_manager_instance.get_active_wallet()
        if not wallet:
            logger.error("No active wallet found for swap request")
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No active wallet found"},
            )

        logger.info(f"Using wallet address: {wallet.default_address.address_id}")
        logger.info(f"Attempting swap: {data['amount']} {data['fromAsset']} -> {data['toAsset']}")

        # Execute swap
        result = swap_assets(
            agent_wallet=wallet,
            amount=str(data["amount"]),
            from_asset_id=data["fromAsset"],
            to_asset_id=data["toAsset"],
        )

        logger.info(f"Swap executed successfully.")
        return {
            "status": "success",
            "message": "Swap executed successfully",
            "result": result,
        }

    except Exception as e:
        logger.error(f"Failed to execute swap: {str(e)}", exc_info=True)
        logger.error(f"Request data that caused error: {data}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to execute swap: {str(e)}"},
        )


@router.post("/transfer")
async def transfer(data: dict):
    """Transfer assets to another address"""
    try:
        logger.info(f"Base Agent: Received transfer request with data: {data}")

        # Get active wallet
        wallet = wallet_manager_instance.get_active_wallet()
        if not wallet:
            logger.error("No active wallet found for transfer request")
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No active wallet found"},
            )

        logger.info(f"Using wallet address: {wallet.default_address.address_id}")
        logger.info(
            f"Attempting transfer: {data['amount']} {data['asset']} -> {data['destinationAddress']}"
        )

        # Execute transfer
        result = transfer_asset(
            agent_wallet=wallet,
            amount=str(data["amount"]),
            asset_id=data["asset"].lower(),
            destination_address=data["destinationAddress"],
        )

        logger.info(f"Transfer executed successfully.")
        return {
            "status": "success",
            "message": "Transfer executed successfully",
            "result": result,
        }

    except Exception as e:
        logger.error(f"Failed to execute transfer: {str(e)}", exc_info=True)
        logger.error(f"Request data that caused error: {data}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to execute transfer: {str(e)}"},
        )
