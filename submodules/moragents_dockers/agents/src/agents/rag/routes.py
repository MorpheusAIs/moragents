import logging
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from src.stores import chat_manager_instance, agent_manager_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for RAG processing"""
    logger.info("Received upload request")
    try:
        rag_agent = agent_manager_instance.get_agent("rag")
        if not rag_agent:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "RAG agent not found"},
            )

        response = await rag_agent.upload_file({"file": file})
        chat_manager_instance.add_response(response.dict(), "rag")
        return response
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to upload file: {str(e)}"},
        )
