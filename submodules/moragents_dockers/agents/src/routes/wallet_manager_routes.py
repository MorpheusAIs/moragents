import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.stores import wallet_manager_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.post("/create")
async def create_wallet(request: Request) -> JSONResponse:
    """Create a new wallet"""
    data = await request.json()
    wallet_id = data.get("wallet_id")
    network_id = data.get("network_id")

    try:
        wallet_manager_instance.create_wallet(wallet_id, network_id)
        return JSONResponse(content={"status": "success", "wallet_id": wallet_id})
    except Exception as e:
        logger.error(f"Failed to create wallet: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.post("/restore")
async def restore_wallet(request: Request) -> JSONResponse:
    """Restore a wallet from exported data"""
    data = await request.json()
    wallet_id = data.get("wallet_id")
    wallet_data = data.get("wallet_data")

    if not wallet_id or not wallet_data:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Missing wallet_id or wallet_data"},
        )

    try:
        wallet = wallet_manager_instance.restore_wallet(wallet_id, wallet_data)
        if wallet:
            return JSONResponse(content={"status": "success", "wallet_id": wallet_id})
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to restore wallet {wallet_id}"},
        )
    except Exception as e:
        logger.error(f"Failed to restore wallet: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.get("/list")
async def list_wallets() -> JSONResponse:
    """Get list of all wallet IDs"""
    try:
        wallet_list = wallet_manager_instance.list_wallets()
        return JSONResponse(content={"wallets": wallet_list})
    except Exception as e:
        logger.error(f"Failed to list wallets: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Failed to retrieve wallet list"},
        )


@router.get("/exists/{wallet_id}")
async def has_wallet(wallet_id: str) -> JSONResponse:
    """Check if a wallet exists"""
    exists = wallet_manager_instance.has_wallet(wallet_id)
    return JSONResponse(content={"exists": exists})


@router.post("/save")
async def save_wallet(request: Request) -> JSONResponse:
    """Save a wallet to file"""
    data = await request.json()
    wallet_id = data.get("wallet_id")
    filepath = data.get("filepath")

    success = wallet_manager_instance.save_wallet(wallet_id, filepath)
    return JSONResponse(content={"status": "success" if success else "error"})


@router.post("/load")
async def load_wallet(request: Request) -> JSONResponse:
    """Load a wallet from file"""
    data = await request.json()
    wallet_id = data.get("wallet_id")
    filepath = data.get("filepath")

    wallet = wallet_manager_instance.load_wallet(wallet_id, filepath)
    if wallet:
        return JSONResponse(content={"status": "success", "wallet_id": wallet_id})
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"Failed to load wallet {wallet_id}"},
    )


@router.delete("/{wallet_id}")
async def remove_wallet(wallet_id: str) -> JSONResponse:
    """Remove a wallet"""
    wallet_manager_instance.remove_wallet(wallet_id)
    return JSONResponse(content={"status": "success"})


@router.get("/export/{wallet_id}")
async def export_wallet(wallet_id: str) -> JSONResponse:
    """Export wallet data"""
    wallet_data = wallet_manager_instance.export_wallet(wallet_id)
    if wallet_data:
        return JSONResponse(content={"status": "success", "data": wallet_data})
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"Failed to export wallet {wallet_id}"},
    )
