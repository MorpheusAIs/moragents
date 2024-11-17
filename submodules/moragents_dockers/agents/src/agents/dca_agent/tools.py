import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import asyncio
from src.cdp import CDPWalletManager
from cdp import Wallet
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class DCAAgentError(Exception):
    """Base exception for DCA agent operations"""
    pass

class ValidationError(DCAAgentError):
    """Validation related errors"""
    pass

class InsufficientFundsError(DCAAgentError):
    """Raised when there are insufficient funds"""
    pass

class ConfigurationError(DCAAgentError):
    """Raised when there are configuration issues"""
    pass

@dataclass
class DCAConfig:
    """DCA strategy configuration"""
    token_address: str
    amount: Decimal
    interval_type: str  # daily, weekly, monthly
    total_periods: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    max_slippage: Decimal = Decimal("0.01")
    gasless: bool = False
    
    def validate(self) -> None:
        """Validate configuration parameters"""
        if not self.token_address:
            raise ValidationError("Token address must be provided")
        if self.amount <= Decimal("0"):
            raise ValidationError("Amount must be positive")
        if self.interval_type not in ["daily", "weekly", "monthly"]:
            raise ValidationError("Invalid interval type")
        if self.max_slippage <= Decimal("0") or self.max_slippage >= Decimal("1"):
            raise ValidationError("Max slippage must be between 0 and 1")

@dataclass
class ExecutionResult:
    """DCA execution result"""
    success: bool
    transaction_hash: Optional[str] = None
    amount: Optional[Decimal] = None
    price: Optional[Decimal] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        result = {
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }
        if self.success:
            result.update({
                "transaction_hash": self.transaction_hash,
                "amount": str(self.amount),
                "price": str(self.price)
            })
        else:
            result["error"] = self.error
        return result

class DCAManager:
    """Manager for DCA operations using CDP wallet"""
    
    def __init__(self, wallet_manager: CDPWalletManager):
        self.wallet_manager = wallet_manager
        self.scheduler = AsyncIOScheduler()
        self.active_strategies: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """Initialize DCA manager"""
        try:
            # Ensure wallet is ready
            await self.wallet_manager.load_wallet()
            
            # Start scheduler
            if not self.scheduler.running:
                self.scheduler.start()
                
            logger.info("DCA manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize DCA manager: {e}")
            raise ConfigurationError(f"DCA manager initialization failed: {e}")

    async def create_strategy(self, config: DCAConfig) -> Tuple[Dict[str, Any], str]:
        """Create new DCA strategy"""
        try:
            # Validate configuration
            config.validate()
            
            # Generate strategy ID
            strategy_id = f"dca_{config.token_address}_{int(datetime.now().timestamp())}"
            
            # Verify wallet has sufficient funds
            wallet = await self.wallet_manager.load_wallet()
            balance = await wallet.get_balance()
            if balance < config.amount:
                raise InsufficientFundsError(
                    f"Insufficient balance: {balance}, required: {config.amount}"
                )
            
            # Create strategy data
            strategy = {
                "id": strategy_id,
                "config": {
                    "token_address": config.token_address,
                    "amount": str(config.amount),
                    "interval_type": config.interval_type,
                    "total_periods": config.total_periods,
                    "min_price": str(config.min_price) if config.min_price else None,
                    "max_price": str(config.max_price) if config.max_price else None,
                    "max_slippage": str(config.max_slippage),
                    "gasless": config.gasless
                },
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "last_execution": None,
                "next_execution": None,
                "execution_history": []
            }
            
            # Schedule execution
            await self._schedule_strategy(strategy_id, config)
            
            # Store strategy
            self.active_strategies[strategy_id] = strategy
            
            logger.info(f"Created DCA strategy: {strategy_id}")
            return strategy, "create_strategy"
            
        except Exception as e:
            logger.error(f"Failed to create strategy: {e}")
            if isinstance(e, (ValidationError, InsufficientFundsError)):
                raise
            raise DCAAgentError(f"Strategy creation failed: {e}")
        

    async def pause_strategy(self, strategy_id: str) -> None:
        """Pause a DCA strategy"""
        self.active_strategies[strategy_id]["status"] = "paused"

    async def resume_strategy(self, strategy_id: str) -> None:
        """Resume a paused DCA strategy"""
        self.active_strategies[strategy_id]["status"] = "active"

    async def cancel_strategy(self, strategy_id: str) -> None:
        """Cancel a DCA strategy"""
        self.scheduler.remove_job(f"dca_{strategy_id}")
        del self.active_strategies[strategy_id]

    async def execute_strategy(self, strategy_id: str) -> ExecutionResult:
        """Execute DCA strategy"""
        async with self._lock:
            try:
                strategy = self.active_strategies.get(strategy_id)
                if not strategy:
                    raise ValidationError(f"Strategy not found: {strategy_id}")
                
                if strategy["status"] != "active":
                    return ExecutionResult(
                        success=False,
                        error=f"Strategy is not active: {strategy['status']}"
                    )
                
                # Load wallet
                wallet = await self.wallet_manager.load_wallet()
                if not wallet:
                    raise ConfigurationError("Wallet not initialized")
                
                # Get current price
                price = await wallet.get_token_price(strategy["config"]["token_address"])
                
                # Check price conditions
                if (strategy["config"]["min_price"] and 
                    price < Decimal(strategy["config"]["min_price"])):
                    return ExecutionResult(
                        success=False,
                        error=f"Price {price} below minimum {strategy['config']['min_price']}"
                    )
                
                if (strategy["config"]["max_price"] and 
                    price > Decimal(strategy["config"]["max_price"])):
                    return ExecutionResult(
                        success=False,
                        error=f"Price {price} above maximum {strategy['config']['max_price']}"
                    )
                
                # Execute transaction
                amount = Decimal(strategy["config"]["amount"])
                tx = await self._execute_transaction(
                    wallet=wallet,
                    token_address=strategy["config"]["token_address"],
                    amount=str(amount),
                    max_slippage=Decimal(strategy["config"]["max_slippage"]),
                    gasless=strategy["config"]["gasless"]
                )
                
                # Update strategy data
                result = ExecutionResult(
                    success=True,
                    transaction_hash=tx.hash,
                    amount=amount,
                    price=Decimal(str(price))
                )
                
                strategy["last_execution"] = datetime.now().isoformat()
                strategy["execution_history"].append(result.to_dict())
                
                # Schedule next execution
                await self._schedule_next_execution(strategy_id)
                
                logger.info(f"Successfully executed strategy {strategy_id}: {tx.hash}")
                return result
                
            except Exception as e:
                logger.error(f"Strategy execution failed: {e}")
                return ExecutionResult(
                    success=False,
                    error=str(e)
                )

    async def _execute_transaction(
        self,
        wallet,
        token_address: str,
        amount: str,
        max_slippage: Decimal,
        gasless: bool = False
    ):
        """Execute token purchase transaction"""
        try:
            tx = wallet.trade(
                amount,
                'usdc',
                'eth',
            )
            
            # Wait for confirmation
            confirmed_tx = await tx.wait()
            
            if not confirmed_tx.is_confirmed():
                raise DCAAgentError("Transaction failed to confirm")
                
            return confirmed_tx
            
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise DCAAgentError(f"Transaction failed: {e}")

    async def _schedule_strategy(self, strategy_id: str, config: DCAConfig) -> None:
        """Schedule strategy execution"""
        try:
            # Calculate cron expression based on interval type
            if config.interval_type == "daily":
                trigger = CronTrigger(hour="0", minute="0")
            elif config.interval_type == "weekly":
                trigger = CronTrigger(day_of_week="mon", hour="0", minute="0")
            elif config.interval_type == "monthly":
                trigger = CronTrigger(day="1", hour="0", minute="0")
            else:
                raise ValidationError(f"Invalid interval type: {config.interval_type}")
            
            # Schedule job
            self.scheduler.add_job(
                self.execute_strategy,
                trigger=trigger,
                args=[strategy_id],
                id=f"dca_{strategy_id}",
                replace_existing=True,
                misfire_grace_time=3600
            )
            
            # Calculate and store next execution
            next_run = trigger.get_next_fire_time(None, datetime.now())
            self.active_strategies[strategy_id]["next_execution"] = next_run.isoformat()
            
            logger.info(f"Scheduled strategy {strategy_id} for {next_run}")
            
        except Exception as e:
            logger.error(f"Failed to schedule strategy: {e}")
            raise DCAAgentError(f"Strategy scheduling failed: {e}")

    async def _schedule_next_execution(self, strategy_id: str) -> None:
        """Schedule next execution for strategy"""
        strategy = self.active_strategies.get(strategy_id)
        if not strategy:
            return
            
        await self._schedule_strategy(
            strategy_id,
            DCAConfig(**{
                k: (Decimal(v) if isinstance(v, str) and k in ['amount', 'max_slippage', 'min_price', 'max_price'] else v)
                for k, v in strategy["config"].items()
            })
        )

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tool definitions for LLM function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_dca_strategy",
                    "description": "Create a new dollar cost averaging strategy",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "token_address": {
                                "type": "string",
                                "description": "Token address to DCA into"
                            },
                            "amount": {
                                "type": "string",
                                "description": "Amount to invest per period"
                            },
                            "interval_type": {
                                "type": "string",
                                "enum": ["daily", "weekly", "monthly"],
                                "description": "Interval between purchases"
                            },
                            "total_periods": {
                                "type": "integer",
                                "description": "Optional number of periods to run"
                            },
                            "min_price": {
                                "type": "string",
                                "description": "Optional minimum execution price"
                            },
                            "max_price": {
                                "type": "string",
                                "description": "Optional maximum execution price"
                            },
                            "max_slippage": {
                                "type": "string",
                                "description": "Maximum acceptable slippage (default 0.01)",
                                "default": "0.01"
                            },
                            "gasless": {
                                "type": "boolean",
                                "description": "Whether to use gasless transactions",
                                "default": False
                            }
                        },
                        "required": ["token_address", "amount", "interval_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_dca_strategy",
                    "description": "Execute a DCA strategy manually",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "strategy_id": {
                                "type": "string",
                                "description": "ID of the strategy to execute"
                            }
                        },
                        "required": ["strategy_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pause_dca_strategy",
                    "description": "Pause a DCA strategy",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "strategy_id": {
                                "type": "string",
                                "description": "ID of the strategy to pause"
                            }
                        },
                        "required": ["strategy_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "resume_dca_strategy",
                    "description": "Resume a paused DCA strategy",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "strategy_id": {
                                "type": "string",
                                "description": "ID of the strategy to resume"
                            }
                        },
                        "required": ["strategy_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_dca_strategy",
                    "description": "Cancel a DCA strategy",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "strategy_id": {
                                "type": "string",
                                "description": "ID of the strategy to cancel"
                            }
                        },
                        "required": ["strategy_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_dca_status",
                    "description": "Get status of a DCA strategy",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "strategy_id": {
                                "type": "string",
                                "description": "ID of the strategy"
                            }
                        },
                        "required": ["strategy_id"]
                    }
                }
            }
        ]


    ## Handlers for function calling
    async def handle_create_dca_strategy(
        self,
        token_address: str,
        amount: str,
        interval_type: str,
        total_periods: Optional[int] = None,
        min_price: Optional[str] = None,
        max_price: Optional[str] = None,
        max_slippage: str = "0.01",
        gasless: bool = False
    ) -> Dict[str, Any]:
        """Handler for creating DCA strategy"""
        try:
            config = DCAConfig(
                token_address=token_address,
                amount=Decimal(amount),
                interval_type=interval_type,
                total_periods=total_periods,
                min_price=Decimal(min_price) if min_price else None,
                max_price=Decimal(max_price) if max_price else None,
                max_slippage=Decimal(max_slippage),
                gasless=gasless
            )
            
            strategy, action = await self.create_strategy(config)
            return {
                "success": True,
                "strategy_id": strategy["id"],
                "details": strategy
            }
            
        except Exception as e:
            logger.error(f"Failed to create DCA strategy: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        
    async def handle_pause_dca_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Handler for pausing DCA strategy"""
        try:
            await self.pause_strategy(strategy_id)
            return {"success": True}
        
        except Exception as e:
            logger.error(f"Failed to pause DCA strategy: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        
    async def handle_resume_dca_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Handler for resuming DCA strategy"""
        try:
            await self.resume_strategy(strategy_id)
            return {"success": True}
        
        except Exception as e:
            logger.error(f"Failed to resume DCA strategy: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        
    async def handle_cancel_dca_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Handler for canceling DCA strategy"""
        try:
            await self.cancel_strategy(strategy_id)
            return {"success": True}
        
        except Exception as e:
            logger.error(f"Failed to cancel DCA strategy: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        
    async def handle_execute_dca_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Handler for executing DCA strategy"""
        try:
            result = await self.execute_strategy(strategy_id)
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Failed to execute DCA strategy: {e}")
            return {
                "success": False,
                "error": str(e)
            }