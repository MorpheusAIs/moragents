import os
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models.config import Config
from src.config import load_agent_routes, setup_logging
from src.stores import workflow_manager_instance

# Configure routes
from src.routes import (
    agent_manager_routes,
    key_manager_routes,
    wallet_manager_routes,
    workflow_manager_routes,
    delegation_routes,
)

# Configure logging
logger = setup_logging()
logger.info("Logging configured successfully")

CONF = Config.get_instance()

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup upload directory
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger.info(f"Upload folder created at {UPLOAD_FOLDER}")

# Include core routers
ROUTERS = [
    delegation_routes.router,
    agent_manager_routes.router,
    key_manager_routes.router,
    wallet_manager_routes.router,
    workflow_manager_routes.router,
]

# Dynamically load and add agent routers
# Load and include all routers
agent_routers = load_agent_routes()
routers = agent_routers + ROUTERS

for router in routers:
    app.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for FastAPI application"""
    # Startup
    logger.info("Starting workflow manager initialization")
    await workflow_manager_instance.initialize()
    logger.info("Workflow manager initialized successfully")
    yield
    # Shutdown
    # Add any cleanup code here if needed


app.router.lifespan_context = lifespan


if __name__ == "__main__":
    logger.info("Starting FastAPI application")
    uvicorn.run(
        "app:app",
        host=CONF.get("host", "default"),
        port=CONF.get_int("port", "default"),
        workers=CONF.get_int("workers", "default"),
        reload=CONF.get_bool("reload", "default"),
    )
