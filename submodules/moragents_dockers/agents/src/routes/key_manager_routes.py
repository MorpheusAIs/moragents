import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.stores import key_manager_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/keys", tags=["keys"])


@router.post("/x")
async def set_x_api_key(request: Request) -> JSONResponse:
    """Set X (Twitter) API keys"""
    logger.info("Received set X API key request")
    data = await request.json()
    key_manager_instance.set_x_keys(
        api_key=data.get("api_key"),
        api_secret=data.get("api_secret"),
        access_token=data.get("access_token"),
        access_token_secret=data.get("access_token_secret"),
        bearer_token=data.get("bearer_token"),
    )
    return JSONResponse(content={"status": "success", "message": "X API keys updated"})


@router.post("/coinbase")
async def set_coinbase_api_key(request: Request) -> JSONResponse:
    """Set Coinbase API keys"""
    logger.info("Received set Coinbase API key request")
    data = await request.json()
    key_manager_instance.set_coinbase_keys(
        cdp_api_key=data.get("cdp_api_key"), cdp_api_secret=data.get("cdp_api_secret")
    )
    return JSONResponse(content={"status": "success", "message": "Coinbase API keys updated"})


@router.post("/1inch")
async def set_oneinch_api_key(request: Request) -> JSONResponse:
    """Set 1inch API key"""
    logger.info("Received set 1inch API key request")
    data = await request.json()
    key_manager_instance.set_oneinch_keys(api_key=data.get("api_key"))
    return JSONResponse(content={"status": "success", "message": "1inch API key updated"})
