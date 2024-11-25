import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple

from cdp import Cdp, Wallet
from src.models.messages import ChatRequest

from .tools import (
    Strategy,
    StrategyStatus,
    StrategyStore,
    JsonFileStrategyStore,
    ValidationError,
    ExecutionError,
    StrategyNotFoundError,
    get_tools,
    cleanup_completed_strategies,
    handle_create_dca,
    handle_pause_dca,
    handle_resume_dca,
    handle_cancel_dca,
    handle_get_status,
    handle_check_health,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DCAAgent:
    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        """
        Initialize the DCAAgent for managing DCA strategies.
        """
        self.config = config
        self.llm = llm
        self.embeddings = embeddings
        self.store = JsonFileStrategyStore()
        self.client: Optional[Cdp] = None
        self.tools_provided = get_tools()
        self.wallets: Dict[str, Wallet] = {}

        # Mapping of function names to handler methods
        self.function_handlers = {
            "handle_dollar_cost_average": self.handle_dollar_cost_average,
            "handle_pause_dca": self.handle_pause_dca,
            "handle_resume_dca": self.handle_resume_dca,
            "handle_cancel_dca": self.handle_cancel_dca,
            "handle_get_status": self.handle_get_status,
            "handle_check_health": self.handle_check_health,
        }

        self.initialize_cdp_client()

    def chat(self, request: ChatRequest):
        """Handle incoming chat requests"""
        try:
            data = request.dict()
            if not data:
                return {"error": "Invalid request data"}, 400

            # Check CDP client initialization
            if not self.client and not self.initialize_cdp_client():
                return {
                    "error": "CDP client not initialized. Please set API credentials.",
                    "needs_credentials": True,
                }, 400

            # Handle strategy status request
            if "strategy_id" in data:
                response, role = self.handle_get_status({"strategy_id": data["strategy_id"]})
                return {"role": role, "content": response}

            # Handle chat prompt
            if "prompt" in data:
                prompt = data["prompt"]
                response, role, next_turn_agent = self.handle_request(prompt)
                return {"role": role, "content": response, "next_turn_agent": next_turn_agent}

            return {"error": "Missing required parameters"}, 400

        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}")
            return {"error": str(e)}, 500

    def handle_request(self, message: str) -> Tuple[str, str, Optional[str]]:
        """Process request and route to appropriate handler"""
        logger.info(f"Processing message: {message}")

        # System prompt that includes descriptions of available functions
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a DCA (Dollar Cost Averaging) agent that helps users create and manage "
                    "cryptocurrency trading strategies. Available actions:\n"
                    "1. Create new DCA strategies with specific intervals and amounts\n"
                    "2. Pause active strategies\n"
                    "3. Resume paused strategies\n"
                    "4. Cancel existing strategies\n"
                    "5. Check strategy status and health"
                ),
            }
        ]

        if isinstance(message, dict):
            user_content = message.get("content", "")
        else:
            user_content = message

        prompt.append({"role": "user", "content": user_content})

        result = self.llm.create_chat_completion(
            messages=prompt, tools=self.tools_provided, tool_choice="auto", temperature=0.01
        )

        try:
            choice = result["choices"][0]["message"]
            if "tool_calls" in choice:
                func = choice["tool_calls"][0]["function"]
                func_name = func["name"].strip().split()[-1]
                logger.info(f"Function name: {func_name}")
                args = json.loads(func["arguments"])
                return self.handle_function_call(func_name, args)
            return choice.get("content", ""), "assistant", None
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            return f"Error processing request: {str(e)}", "assistant", None

    def initialize_cdp_client(self) -> bool:
        """Initialize CDP client with stored credentials"""
        try:
            api_key = self.config.get("cdpApiKey")
            api_secret = self.config.get("cdpApiSecret")

            if not all([api_key, api_secret]):
                logger.warning("CDP credentials not found")
                return False

            self.client = Cdp.configure(api_key, api_secret)
            return True
        except Exception as e:
            logger.error(f"CDP client initialization failed: {e}")
            return False

    def handle_function_call(
        self,
        func_name: str,
        args: Dict[str, Any],
        chain_id: Optional[str] = None,
        wallet_address: Optional[str] = None,
    ) -> Tuple[str, str, Optional[str]]:
        handler = self.function_handlers.get(func_name)
        if handler:
            return handler(args, chain_id, wallet_address)
        else:
            logger.error(f"Function '{func_name}' not supported.")
            return f"Error: Function '{func_name}' not supported.", "assistant", None

    def handle_dollar_cost_average(
        self, args: Dict[str, Any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        """Handle dollar cost averaging strategy creation"""
        try:
            res, role = handle_create_dca(
                token_address=args["token_address"],
                amount=args["amount"],
                interval=args["interval"],
                total_periods=args.get("total_periods"),
                min_price=args.get("min_price"),
                max_price=args.get("max_price"),
                max_slippage=args.get("max_slippage", 0.01),
                stop_loss=args.get("stop_loss"),
                take_profit=args.get("take_profit"),
            )
            logger.info(f"DCA Strategy creation result: {res}")
            return f"Successfully created DCA strategy with ID: {res['strategy_id']}", role, None
        except ValidationError as e:
            logger.error(f"Validation error in DCA creation: {str(e)}")
            return str(e), "assistant", None
        except ExecutionError as e:
            logger.error(f"Execution error in DCA creation: {str(e)}")
            return str(e), "assistant", None

    def handle_pause_dca(
        self, args: Dict[str, Any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        """Handle pausing a DCA strategy"""
        try:
            res, role = handle_pause_dca(args["strategy_id"])
            logger.info(f"Strategy pause result: {res}")
            return f"Successfully paused strategy {args['strategy_id']}", role, None
        except StrategyNotFoundError as e:
            logger.error(f"Strategy not found: {str(e)}")
            return str(e), "assistant", None
        except ExecutionError as e:
            logger.error(f"Error pausing strategy: {str(e)}")
            return str(e), "assistant", None

    def handle_resume_dca(
        self, args: Dict[str, Any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        """Handle resuming a DCA strategy"""
        try:
            res, role = handle_resume_dca(args["strategy_id"])
            logger.info(f"Strategy resume result: {res}")
            return f"Successfully resumed strategy {args['strategy_id']}", role, None
        except StrategyNotFoundError as e:
            logger.error(f"Strategy not found: {str(e)}")
            return str(e), "assistant", None
        except ExecutionError as e:
            logger.error(f"Error resuming strategy: {str(e)}")
            return str(e), "assistant", None

    def handle_cancel_dca(
        self, args: Dict[str, Any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        """Handle cancelling a DCA strategy"""
        try:
            res, role = handle_cancel_dca(args["strategy_id"])
            logger.info(f"Strategy cancellation result: {res}")
            return f"Successfully cancelled strategy {args['strategy_id']}", role, None
        except StrategyNotFoundError as e:
            logger.error(f"Strategy not found: {str(e)}")
            return str(e), "assistant", None
        except ExecutionError as e:
            logger.error(f"Error cancelling strategy: {str(e)}")
            return str(e), "assistant", None

    def handle_get_status(
        self, args: Dict[str, Any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        """Handle getting strategy status"""
        try:
            res, role = handle_get_status(
                args["strategy_id"], include_history=args.get("include_history", False)
            )
            logger.info(f"Strategy status result: {res}")
            return json.dumps(res, indent=2), role, None
        except StrategyNotFoundError as e:
            logger.error(f"Strategy not found: {str(e)}")
            return str(e), "assistant", None
        except ExecutionError as e:
            logger.error(f"Error getting strategy status: {str(e)}")
            return str(e), "assistant", None

    def handle_check_health(
        self, args: Dict[str, Any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        """Handle checking strategy health"""
        try:
            res, role = handle_check_health(args["strategy_id"])
            logger.info(f"Strategy health check result: {res}")
            return json.dumps(res, indent=2), role, None
        except StrategyNotFoundError as e:
            logger.error(f"Strategy not found: {str(e)}")
            return str(e), "assistant", None
        except ExecutionError as e:
            logger.error(f"Error checking strategy health: {str(e)}")
            return str(e), "assistant", None
