import logging
from decimal import Decimal
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.stores import workflow_manager_instance, wallet_manager_instance
from src.agents.dca_agent.tools import DCAParams, create_dca_workflow

router = APIRouter(prefix="/dca", tags=["dca"])
logger = logging.getLogger(__name__)


@router.post("/create_strategy")
async def create_strategy(data: dict):
    """Create a new DCA trading strategy"""
    try:
        logger.info("DCA Agent: Received create_strategy request")

        # Convert frontend config to DCA params
        dca_params = DCAParams(
            origin_token=data["originToken"].lower(),
            destination_token=data["destinationToken"].lower(),
            step_size=Decimal(str(data["stepSize"])),
            total_investment_amount=(
                Decimal(str(data["totalInvestmentAmount"]))
                if data.get("totalInvestmentAmount")
                else None
            ),
            frequency=data["frequency"],
            max_purchase_amount=(
                Decimal(str(data["maxPurchaseAmount"])) if data.get("maxPurchaseAmount") else None
            ),
            price_threshold=(
                Decimal(str(data["priceThreshold"])) if data.get("priceThreshold") else None
            ),
            pause_on_volatility=data.get("pauseOnVolatility", False),
            wallet_id=wallet_manager_instance.active_wallet_id,
        )

        # Create workflow configuration
        workflow_config = create_dca_workflow(dca_params)

        # Create workflow
        workflow = await workflow_manager_instance.create_workflow(
            name=workflow_config["name"],
            description=workflow_config["description"],
            action=workflow_config["action"],
            params=workflow_config["params"],
            interval=workflow_config["interval"],
        )

        return {
            "status": "success",
            "message": "DCA strategy created successfully",
            "workflow": workflow.to_dict(),
        }

    except Exception as e:
        logger.error(f"Failed to create DCA strategy: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to create DCA strategy: {str(e)}"},
        )


@router.get("/strategies")
async def list_strategies():
    """List all DCA strategies"""
    try:
        workflows = await workflow_manager_instance.list_workflows()
        dca_workflows = [w.to_dict() for w in workflows if w.action == "dca_trade"]

        return {"status": "success", "strategies": dca_workflows}

    except Exception as e:
        logger.error(f"Failed to list DCA strategies: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to list DCA strategies: {str(e)}"},
        )


@router.get("/strategies/{workflow_id}")
async def get_strategy(workflow_id: str):
    """Get a specific DCA strategy"""
    try:
        workflow = await workflow_manager_instance.get_workflow(workflow_id)
        if not workflow:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": f"Strategy {workflow_id} not found"},
            )

        return {"status": "success", "strategy": workflow.to_dict()}

    except Exception as e:
        logger.error(f"Failed to get DCA strategy: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to get DCA strategy: {str(e)}"},
        )


@router.delete("/strategies/{workflow_id}")
async def delete_strategy(workflow_id: str):
    """Delete a DCA strategy"""
    try:
        success = await workflow_manager_instance.delete_workflow(workflow_id)
        if not success:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": f"Strategy {workflow_id} not found"},
            )

        return {"status": "success", "message": f"Strategy {workflow_id} deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete DCA strategy: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to delete DCA strategy: {str(e)}"},
        )
