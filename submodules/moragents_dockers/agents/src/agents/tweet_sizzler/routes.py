import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.stores import chat_manager_instance, agent_manager_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tweet", tags=["tweet"])


@router.post("/regenerate")
async def regenerate_tweet():
    """Regenerate a tweet"""
    logger.info("Received regenerate tweet request")
    try:
        tweet_agent = agent_manager_instance.get_agent("tweet sizzler")
        if not tweet_agent:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Tweet sizzler agent not found"},
            )

        response = tweet_agent.generate_tweet()
        chat_manager_instance.add_message(response)
        return response
    except Exception as e:
        logger.error(f"Failed to regenerate tweet: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to regenerate tweet: {str(e)}"},
        )


@router.post("/post")
async def post_tweet(request: Request):
    """Post a tweet"""
    logger.info("Received post tweet request")
    try:
        tweet_agent = agent_manager_instance.get_agent("tweet sizzler")
        if not tweet_agent:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Tweet sizzler agent not found"},
            )

        response = await tweet_agent.post_tweet(request)
        chat_manager_instance.add_message(response)
        return response
    except Exception as e:
        logger.error(f"Failed to post tweet: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to post tweet: {str(e)}"},
        )
