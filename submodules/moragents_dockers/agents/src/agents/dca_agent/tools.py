from __future__ import annotations
import logging
from typing import Dict, Any, Optional, List, TypeVar, Callable, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import json
import aiofiles
import asyncio
from cdp import Cdp, Wallet
from abc import ABC, abstractmethod
from typing import Protocol
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# Initialize APScheduler
scheduler = AsyncIOScheduler(
    job_defaults={
        "coalesce": True,  # Combine multiple pending executions
        "max_instances": 1,  # Prevent concurrent executions
        "misfire_grace_time": 3600,  # Allow 1 hour grace period for missed executions
    }
)
scheduler.start()


class DCAError(Exception):
    """Base exception for DCA operations"""

    pass


class StrategyError(DCAError):
    """Strategy-related error hierarchy"""

    class NotFound(DCAError):
        """Strategy not found"""

        pass

    class ValidationFailed(DCAError):
        """Strategy validation failed"""

        pass

    class ExecutionFailed(DCAError):
        """Strategy execution failed"""

        pass


class HealthStatus(str, Enum):
    """Health status enum for strategies"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    PENDING = "pending"
    INACTIVE = "inactive"


T = TypeVar("T")

# Configuration constants
CONFIG = {
    "health": {
        "warning_threshold": 1.5,  # 150% of interval
        "critical_threshold": 2.0,  # 200% of interval
        "error_threshold": 3,  # Number of consecutive errors before critical
        "recovery_attempts": 3,  # Number of attempts to recover from errors
    },
    "execution": {
        "liquidity_threshold": Decimal("1000"),
        "gas_buffer": Decimal("1.02"),  # 2% buffer
        "max_retries": 3,
        "retry_delay": [1, 5, 15],  # Exponential backoff delays in seconds
        "min_balance_threshold": Decimal("0.01"),  # Minimum ETH balance required
    },
    "storage": {
        "backup_interval": 3600,  # Backup every hour
        "max_backups": 24,  # Keep last 24 backups
        "retention_days": 30,  # Keep strategy history for 30 days
    },
}


class IntervalType(str, Enum):
    """Interval types for DCA strategies"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class DCAConfig:
    token_address: str
    amount: Decimal
    interval_seconds: int
    total_periods: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    max_slippage: Decimal = Decimal("0.01")
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    time_limit: Optional[int] = None

    def validate(self) -> None:
        """Validate the configuration parameters."""
        if not self.token_address:
            raise StrategyError.ValidationFailed("Token address must be provided.")

        if self.amount <= Decimal("0"):
            raise StrategyError.ValidationFailed("Investment amount must be positive.")

        if self.interval_seconds <= 0:
            raise StrategyError.ValidationFailed("Interval seconds must be positive.")

        if self.total_periods is not None and self.total_periods <= 0:
            raise StrategyError.ValidationFailed("Total periods must be positive if specified.")

        if self.min_price is not None and self.min_price <= Decimal("0"):
            raise StrategyError.ValidationFailed("Minimum price must be positive if specified.")

        if self.max_price is not None and self.max_price <= Decimal("0"):
            raise StrategyError.ValidationFailed("Maximum price must be positive if specified.")

        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise StrategyError.ValidationFailed("Minimum price cannot exceed maximum price.")

        if not (Decimal("0") < self.max_slippage < Decimal("1")):
            raise StrategyError.ValidationFailed(
                "Max slippage must be between 0 and 1 (exclusive)."
            )

        if self.stop_loss is not None and self.stop_loss <= Decimal("0"):
            raise StrategyError.ValidationFailed("Stop loss must be positive if specified.")

        if self.take_profit is not None and self.take_profit <= Decimal("0"):
            raise StrategyError.ValidationFailed("Take profit must be positive if specified.")


@dataclass
class ExecutionResult:
    """Encapsulates strategy execution results"""

    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        result = {
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.error:
            result["error"] = self.error
        else:
            result.update(self.data)
        return result


@dataclass
class StrategyMetrics:
    """Strategy performance metrics"""

    total_periods: int
    successful_txs: int
    failed_txs: int
    total_invested: Decimal
    avg_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    roi: Optional[Decimal] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "total_periods": self.total_periods,
            "successful_transactions": self.successful_txs,
            "failed_transactions": self.failed_txs,
            "total_invested": str(self.total_invested),
            **({"average_price": str(self.avg_price)} if self.avg_price else {}),
            **({"minimum_price": str(self.min_price)} if self.min_price else {}),
            **({"maximum_price": str(self.max_price)} if self.max_price else {}),
            **({"return_on_investment": str(self.roi)} if self.roi else {}),
        }


class StrategyStatus(str, Enum):
    """Strategy execution status with transition rules"""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

    @property
    def is_terminal(self) -> bool:
        return self in {self.COMPLETED, self.CANCELLED, self.ERROR}

    @property
    def allowed_transitions(self) -> set:
        """Define valid status transitions"""
        transitions = {
            self.ACTIVE: {self.PAUSED, self.CANCELLED, self.COMPLETED, self.ERROR},
            self.PAUSED: {self.ACTIVE, self.CANCELLED},
            self.COMPLETED: set(),
            self.CANCELLED: set(),
            self.ERROR: {self.ACTIVE, self.CANCELLED},
        }
        return transitions[self]


class CDPClient:
    """CDP Client with error handling and retry logic"""

    _instance = None
    _lock = asyncio.Lock()
    _init_lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CDPClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    async def initialize(self, api_key: str, api_secret: str) -> None:
        """Initialize CDP client with health monitoring"""
        async with self._init_lock:
            if self._initialized:
                return
            try:
                # Configure CDP SDK
                Cdp.configure(api_key, api_secret)

                # Create wallet and verify connection
                self._wallet = await Wallet.create()
                await self._verify_connection()

                # Start health monitoring
                asyncio.create_task(self._monitor_health())

                self._initialized = True
                self._ready.set()

                logger.info(f"CDP client initialized successfully: {self._wallet.default_address}")

            except Exception as e:
                logger.error(f"CDP initialization failed: {e}")
                self._ready.clear()
                raise StrategyError.ExecutionFailed(f"CDP initialization failed: {e}")

    async def _verify_connection(self) -> None:
        """Verify CDP connection and wallet setup"""
        try:
            # Check wallet balance
            balance = await self._wallet.get_balance()
            if balance < CONFIG["execution"]["min_balance_threshold"]:
                raise StrategyError.ValidationFailed(f"Insufficient wallet balance: {balance} ETH")

            # Verify price feed access
            await self._wallet.get_token_price("eth")

            self._last_health_check = datetime.now()
            self._error_count = 0

        except Exception as e:
            logger.error(f"Connection verification failed: {e}")
            raise StrategyError.ExecutionFailed(f"Connection verification failed: {e}")

    async def get_current_price(self, token_address: str) -> Decimal:
        """Get current token price from CDP"""
        try:
            price = await self._wallet.get_token_price(token_address)
            return Decimal(str(price))
        except Exception as e:
            logger.error(f"Failed to get token price: {e}")
            raise StrategyError.ExecutionFailed(f"Price fetch failed: {e}")

    async def swap(
        self,
        amount: str,
        token_address: str,
        min_tokens: str,
        slippage_tolerance: float,
        gas_buffer: float,
        source_asset: str = "eth",
    ) -> Any:
        """Execute swap with enhanced validation and monitoring"""
        await self._ready.wait()

        try:
            # Pre-trade validation
            balance = await self._wallet.get_balance()
            amount_decimal = Decimal(amount)

            if balance < amount_decimal:
                raise StrategyError.ValidationFailed(
                    f"Insufficient balance: {balance} {source_asset}"
                )

            # Execute trade with retry logic
            last_error = None
            for attempt, delay in enumerate(CONFIG["execution"]["retry_delay"]):
                try:
                    trade = self._wallet.trade(
                        float(amount),
                        source_asset,
                        token_address,
                        slippage_tolerance=slippage_tolerance,
                    )

                    # Wait for transaction confirmation
                    result = await trade.wait()

                    # Verify transaction success
                    if not self._verify_transaction(result):
                        raise StrategyError.ExecutionFailed("Transaction verification failed")

                    return result

                except Exception as e:
                    logger.warning(f"Trade attempt {attempt + 1} failed: {e}")
                    last_error = e

                    if attempt < len(CONFIG["execution"]["retry_delay"]) - 1:
                        await asyncio.sleep(delay)

            raise StrategyError.ExecutionFailed(f"All trade attempts failed: {last_error}")

        except Exception as e:
            logger.error(f"Swap failed: {e}")
            raise StrategyError.ExecutionFailed(f"Swap failed: {e}")


@dataclass
class Strategy:
    """Enhanced DCA strategy implementation"""

    id: str
    config: DCAConfig
    status: StrategyStatus = field(default=StrategyStatus.ACTIVE)
    current_period: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    def __post_init__(self):
        """Initialize strategy metadata"""
        self.metadata.setdefault("status_history", [])
        self.metadata.setdefault("creation_time", datetime.now().isoformat())
        self.metadata.setdefault("current_prices", {})
        self.metadata.setdefault("error_count", 0)

    async def execute(self, client: CDPClient) -> ExecutionResult:
        """Execute strategy purchase"""
        async with self._lock:
            if self.status != StrategyStatus.ACTIVE:
                return ExecutionResult(
                    success=False,
                    error=f"Strategy {self.id} is not active (current status: {self.status})",
                )

        try:
            # Get current price
            price = await self._get_token_price(client)

            # Check execution conditions
            if not self._should_execute(price):
                return ExecutionResult(
                    success=True,
                    data={
                        "status": "skipped",
                        "reason": "Execution conditions not met",
                        "price": str(price),
                    },
                )

            # Execute transaction
            result = await self._execute_transaction(client, price)
            if result:
                self._update_execution_state(price, result.transaction_hash)

            # Schedule next execution
            if self.status == StrategyStatus.ACTIVE:
                self._schedule_next_execution(client)

            return ExecutionResult(
                success=True,
                data={
                    "status": "success",
                    "transaction_hash": result.transaction_hash if result else None,
                    "price": str(price),
                    "amount": str(self.config.amount),
                    "next_execution": (
                        self.next_execution.isoformat() if self.next_execution else None
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Strategy execution failed: {str(e)}", exc_info=True)
            self._handle_execution_error(e)
            return ExecutionResult(success=False, error=str(e))

    def pause(self) -> ExecutionResult:
        """Pause strategy execution"""
        try:
            if self.status != StrategyStatus.ACTIVE:
                return ExecutionResult(
                    success=False, error=f"Cannot pause strategy in {self.status} status"
                )

            self._transition_to(StrategyStatus.PAUSED, "User requested pause")
            self.metadata["paused_at"] = datetime.now().isoformat()

            return ExecutionResult(
                success=True,
                data={
                    "status": "paused",
                    "paused_at": self.metadata["paused_at"],
                    "current_period": self.current_period,
                },
            )
        except Exception as e:
            logger.error(f"Failed to pause strategy: {str(e)}")
            return ExecutionResult(success=False, error=str(e))

    def resume(self) -> ExecutionResult:
        """Resume paused strategy"""
        try:
            if self.status != StrategyStatus.PAUSED:
                return ExecutionResult(
                    success=False, error=f"Cannot resume strategy in {self.status} status"
                )

            self._transition_to(StrategyStatus.ACTIVE, "User requested resume")
            self._calculate_next_execution()
            self.metadata["resumed_at"] = datetime.now().isoformat()

            # Schedule next execution
            self._schedule_next_execution()

            return ExecutionResult(
                success=True,
                data={
                    "status": "active",
                    "resumed_at": self.metadata["resumed_at"],
                    "next_execution": (
                        self.next_execution.isoformat() if self.next_execution else None
                    ),
                },
            )
        except Exception as e:
            logger.error(f"Failed to resume strategy: {str(e)}")
            return ExecutionResult(success=False, error=str(e))

    def cancel(self) -> ExecutionResult:
        """Cancel strategy execution"""
        try:
            if self.status.is_terminal:
                return ExecutionResult(
                    success=False, error=f"Cannot cancel strategy in {self.status} status"
                )

            previous_status = self.status
            self._transition_to(StrategyStatus.CANCELLED, "User requested cancellation")

            metrics = self.calculate_metrics()
            self.metadata.update(
                {
                    "cancelled_at": datetime.now().isoformat(),
                    "final_metrics": metrics.to_dict(),
                    "previous_status": previous_status.value,
                }
            )

            return ExecutionResult(
                success=True,
                data={
                    "status": "cancelled",
                    "cancelled_at": self.metadata["cancelled_at"],
                    "metrics": metrics.to_dict(),
                },
            )
        except Exception as e:
            logger.error(f"Failed to cancel strategy: {str(e)}")
            return ExecutionResult(success=False, error=str(e))

    def calculate_metrics(self) -> StrategyMetrics:
        """Calculate current strategy metrics"""
        successful_txs = [tx for tx in self.history if tx.get("status") == "success"]
        failed_txs = [tx for tx in self.history if tx.get("status") == "failed"]

        total_invested = sum(Decimal(tx["amount"]) for tx in successful_txs)

        metrics = StrategyMetrics(
            total_periods=self.current_period,
            successful_txs=len(successful_txs),
            failed_txs=len(failed_txs),
            total_invested=total_invested,
        )

        if successful_txs:
            prices = [Decimal(tx["price"]) for tx in successful_txs]
            metrics.avg_price = sum(prices) / len(prices)
            metrics.min_price = min(prices)
            metrics.max_price = max(prices)

            # Calculate ROI if possible
            current_prices = self.metadata.get("current_prices", {})
            if self.config.token_address in current_prices:
                current_value = total_invested * Decimal(
                    str(current_prices[self.config.token_address])
                )
                metrics.roi = ((current_value - total_invested) / total_invested * 100).quantize(
                    Decimal("0.01")
                )

        return metrics

    def _transition_to(self, new_status: StrategyStatus, reason: str) -> None:
        """Handle status transitions with validation"""
        if new_status not in self.status.allowed_transitions:
            raise StrategyError.ValidationFailed(
                f"Invalid transition from {self.status} to {new_status}"
            )

        old_status = self.status
        self.status = new_status

        # Record transition in history
        self.metadata["status_history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "old_status": old_status.value,
                "new_status": new_status.value,
                "reason": reason,
            }
        )

    def _calculate_next_execution(self) -> None:
        """Calculate next execution time"""
        if self.last_execution:
            self.next_execution = self.last_execution + timedelta(
                seconds=self.config.interval_seconds
            )
        else:
            self.next_execution = datetime.now() + timedelta(seconds=self.config.interval_seconds)

    def _should_execute(self, price: Decimal) -> bool:
        """Check if execution conditions are met"""
        price_in_range = (self.config.min_price is None or price >= self.config.min_price) and (
            self.config.max_price is None or price <= self.config.max_price
        )

        if not price_in_range:
            logger.info(f"Price {price} outside bounds for strategy {self.id}")
            return False

        if self.config.total_periods and self.current_period >= self.config.total_periods:
            logger.info(f"Strategy {self.id} reached total periods limit")
            self._transition_to(StrategyStatus.COMPLETED, "Total periods reached")
            return False

        return True

    async def _execute_transaction(self, client: CDPClient, price: Decimal) -> Any:
        """Execute token swap transaction"""
        # Calculate minimum tokens with slippage protection
        min_tokens = (self.config.amount / price * (1 - self.config.max_slippage)).quantize(
            Decimal("0.00000001")
        )

        # Check stop loss and take profit
        if self.config.stop_loss and price <= self.config.stop_loss:
            self._transition_to(StrategyStatus.COMPLETED, f"Stop loss triggered at price {price}")
            return None

        if self.config.take_profit and price >= self.config.take_profit:
            self._transition_to(StrategyStatus.COMPLETED, f"Take profit triggered at price {price}")
            return None

        for attempt in range(CONFIG["execution"]["max_retries"]):
            try:
                trade = await client.swap(
                    amount=str(self.config.amount),
                    token_address=self.config.token_address,
                    min_tokens=str(min_tokens),
                    slippage_tolerance=float(self.config.max_slippage),
                    gas_buffer=float(CONFIG["execution"]["gas_buffer"]),
                    source_asset="eth",  # This could also be parameterized or derived from strategy
                )
                return await trade.wait()
            except Exception as e:
                if attempt == CONFIG["execution"]["max_retries"] - 1:
                    raise StrategyError.ExecutionFailed(f"Transaction failed: {e}")
                logger.warning(
                    f"Transaction attempt {attempt + 1} failed: {e}. Retrying in {CONFIG['execution']['retry_delay']} seconds."
                )
                await asyncio.sleep(CONFIG["execution"]["retry_delay"])

    def _update_execution_state(self, price: Decimal, transaction_hash: str) -> None:
        """Update strategy state after successful execution"""
        self.current_period += 1
        self.last_execution = datetime.now()
        self.history.append(
            {
                "timestamp": self.last_execution.isoformat(),
                "status": "success",
                "price": str(price),
                "amount": str(self.config.amount),
                "transaction_hash": transaction_hash,
            }
        )
        self._calculate_next_execution()

    def _handle_execution_error(self, error: Exception) -> None:
        """Handle errors during execution"""
        self.status = StrategyStatus.ERROR
        self.metadata["error_count"] = self.metadata.get("error_count", 0) + 1
        self.history.append(
            {"timestamp": datetime.now().isoformat(), "status": "failed", "error": str(error)}
        )

    async def _get_token_price(self, client: CDPClient) -> Decimal:
        """Fetch the current price of the token."""
        try:
            price = await client.get_current_price(self.config.token_address)
            if price <= Decimal("0"):
                raise StrategyError.ValidationFailed(f"Fetched invalid price: {price}")
            # Optionally store the current price in metadata
            self.metadata["current_prices"][self.config.token_address] = str(price)
            return price
        except Exception as e:
            logger.error(f"Failed to fetch token price: {e}")
            raise StrategyError.ExecutionFailed(f"Failed to fetch token price: {e}")

    def _schedule_next_execution(
        self, client: Optional[CDPClient] = None, scheduler: Optional[AsyncIOScheduler] = None
    ) -> None:
        """Schedule next execution with enhanced reliability"""
        if not client:
            client = CDPClient()
        if not scheduler:
            scheduler = AsyncIOScheduler()
            scheduler.start()

        if self.next_execution:
            # Calculate optimal execution window
            grace_period = timedelta(minutes=5)  # 5-minute grace period
            execution_window = (
                self.next_execution - grace_period,
                self.next_execution + grace_period,
            )

            # Create cron trigger for more reliable scheduling
            trigger = CronTrigger(
                year=self.next_execution.year,
                month=self.next_execution.month,
                day=self.next_execution.day,
                hour=self.next_execution.hour,
                minute=self.next_execution.minute,
            )

            # Add job with enhanced parameters
            scheduler.add_job(
                lambda: asyncio.create_task(self.execute(client)),
                trigger=trigger,
                id=self.id,
                replace_existing=True,
                misfire_grace_time=3600,  # 1-hour grace period
                coalesce=True,
                max_instances=1,
                next_run_time=self.next_execution,
            )

            logger.info(
                f"Scheduled next execution for strategy {self.id} at {self.next_execution} "
                f"(window: {execution_window[0]} - {execution_window[1]})"
            )

    @classmethod
    def create_new(cls, **kwargs) -> "Strategy":
        """Create new strategy with validation"""
        config = DCAConfig(**kwargs)
        config.validate()

        # Generate unique strategy ID
        timestamp = int(datetime.now().timestamp())
        strategy_id = f"dca_{kwargs['token_address']}_{timestamp}"

        # Calculate interval_seconds based on interval type
        interval = kwargs.get("interval", "daily").lower()
        if interval == IntervalType.DAILY.value:
            interval_seconds = 86400  # 24 * 60 * 60
        elif interval == IntervalType.WEEKLY.value:
            interval_seconds = 604800  # 7 * 24 * 60 * 60
        elif interval == IntervalType.MONTHLY.value:
            interval_seconds = 2592000  # 30 * 24 * 60 * 60 (approx)
        else:
            raise StrategyError.ValidationFailed(f"Invalid interval type: {interval}")

        config.interval_seconds = interval_seconds

        strategy = cls(
            id=str(strategy_id),
            config=config,
            status=StrategyStatus.ACTIVE,
            start_time=datetime.now(),
            metadata={
                "creation_time": datetime.now().isoformat(),
                "status_history": [],
                "current_prices": {},
                "error_count": 0,
            },
        )

        # Schedule the first execution
        client = CDPClient()
        strategy._schedule_next_execution(client)

        return strategy

    def to_dict(self) -> Dict[str, Any]:
        """Convert strategy to dictionary"""
        return {
            "id": self.id,
            "config": {
                "token_address": self.config.token_address,
                "amount": str(self.config.amount),
                "interval_seconds": self.config.interval_seconds,
                "total_periods": self.config.total_periods,
                "min_price": str(self.config.min_price) if self.config.min_price else None,
                "max_price": str(self.config.max_price) if self.config.max_price else None,
                "max_slippage": str(self.config.max_slippage),
                "stop_loss": str(self.config.stop_loss) if self.config.stop_loss else None,
                "take_profit": str(self.config.take_profit) if self.config.take_profit else None,
                "time_limit": self.config.time_limit,
            },
            "status": self.status.value,
            "current_period": self.current_period,
            "start_time": self.start_time.isoformat(),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "next_execution": self.next_execution.isoformat() if self.next_execution else None,
            "history": self.history,
            "metadata": self.metadata,
            "metrics": self.calculate_metrics().to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Strategy":
        """Deserialize a Strategy instance from a dictionary."""
        config_data = data.get("config", {})
        config = DCAConfig(
            token_address=config_data["token_address"],
            amount=Decimal(config_data["amount"]),
            interval_seconds=config_data["interval_seconds"],
            total_periods=config_data.get("total_periods"),
            min_price=Decimal(config_data["min_price"]) if config_data.get("min_price") else None,
            max_price=Decimal(config_data["max_price"]) if config_data.get("max_price") else None,
            max_slippage=Decimal(config_data.get("max_slippage", "0.01")),
            stop_loss=Decimal(config_data["stop_loss"]) if config_data.get("stop_loss") else None,
            take_profit=(
                Decimal(config_data["take_profit"]) if config_data.get("take_profit") else None
            ),
            time_limit=config_data.get("time_limit"),
        )
        config.validate()

        strategy = cls(
            id=data["id"],
            config=config,
            status=StrategyStatus(data["status"]),
            current_period=data.get("current_period", 0),
            start_time=datetime.fromisoformat(data["start_time"]),
            last_execution=(
                datetime.fromisoformat(data["last_execution"])
                if data.get("last_execution")
                else None
            ),
            next_execution=(
                datetime.fromisoformat(data["next_execution"])
                if data.get("next_execution")
                else None
            ),
            history=data.get("history", []),
            metadata=data.get("metadata", {}),
        )
        return strategy


class StrategyStore(Protocol):
    """Strategy persistence protocol"""

    @abstractmethod
    async def save(self, strategy: Strategy) -> None:
        pass

    @abstractmethod
    async def load(self, strategy_id: str) -> Optional[Strategy]:
        pass

    @abstractmethod
    async def delete(self, strategy_id: str) -> None:
        pass

    @abstractmethod
    async def list_all(self) -> List[Strategy]:
        pass


class JsonFileStrategyStore(StrategyStore):
    """Asynchronous JSON file-based strategy storage"""

    def __init__(self, filepath: str = "dca_strategies.json"):
        self.filepath = Path(filepath)
        self._lock = asyncio.Lock()
        self._backup_dir = Path("backups")
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        asyncio.create_task(self._initialize())

    async def _initialize(self) -> None:
        """Initialize the storage by ensuring file existence and setting up backups."""
        await self._ensure_file_exists()
        await self._setup_backup_schedule()

    async def _setup_backup_schedule(self) -> None:
        """Setup automated backups using asynchronous backups."""
        self._backup_dir.mkdir(exist_ok=True)

        self.scheduler.add_job(
            self._create_backup,
            IntervalTrigger(seconds=CONFIG["storage"]["backup_interval"]),
            id="strategy_backup",
            replace_existing=True,
        )
        logger.info("Backup schedule initialized.")

    async def _create_backup(self) -> None:
        """Create a timestamped backup of strategies asynchronously."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self._backup_dir / f"strategies_backup_{timestamp}.json"

            data = await self._load_file()
            async with aiofiles.open(backup_path, "w") as f:
                await f.write(json.dumps(data, indent=4))

            await self._cleanup_old_backups()
            logger.info(f"Backup created at {backup_path}")

        except Exception as e:
            logger.error(f"Backup creation failed: {e}")

    async def _cleanup_old_backups(self) -> None:
        """Remove old backup files asynchronously."""
        try:
            backups = sorted(
                self._backup_dir.glob("strategies_backup_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

            for backup in backups[CONFIG["storage"]["max_backups"] :]:
                await asyncio.to_thread(backup.unlink)
                logger.info(f"Old backup removed: {backup}")

        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")

    async def _ensure_file_exists(self) -> None:
        """Create storage file if it doesn't exist asynchronously."""
        if not self.filepath.exists():
            async with aiofiles.open(self.filepath, "w") as f:
                await f.write("{}")
            logger.info(f"Storage file created at {self.filepath}")

    async def _with_file_lock(self, operation: Callable[[], T]) -> T:
        """Execute operation with asynchronous file lock."""
        async with self._lock:
            return await operation()

    async def save(self, strategy: Strategy) -> None:
        """Save strategy with atomic asynchronous file write."""

        async def _save():
            strategies = await self._load_file()
            strategies[strategy.id] = strategy.to_dict()
            await self._save_file(strategies)

        await self._with_file_lock(_save)
        logger.info(f"Strategy {strategy.id} saved.")

    async def load(self, strategy_id: str) -> Optional[Strategy]:
        """Load strategy by ID asynchronously."""
        strategies = await self._with_file_lock(self._load_file)
        strategy_data = strategies.get(strategy_id)
        if strategy_data:
            logger.info(f"Strategy {strategy_id} loaded.")
            return Strategy.from_dict(strategy_data)
        logger.warning(f"Strategy {strategy_id} not found.")
        return None

    async def delete(self, strategy_id: str) -> None:
        """Delete strategy by ID asynchronously."""

        async def _delete():
            strategies = await self._load_file()
            if strategy_id in strategies:
                del strategies[strategy_id]
                await self._save_file(strategies)
                logger.info(f"Strategy {strategy_id} deleted.")
            else:
                logger.warning(f"Strategy {strategy_id} not found for deletion.")

        await self._with_file_lock(_delete)

    async def list_all(self) -> List[Strategy]:
        """List all stored strategies asynchronously."""
        strategies = await self._with_file_lock(self._load_file)
        logger.info("Listing all strategies.")
        return [Strategy.from_dict(data) for data in strategies.values()]

    async def _load_file(self) -> Dict[str, Any]:
        """Load JSON file contents asynchronously."""
        try:
            async with aiofiles.open(self.filepath, "r") as f:
                content = await f.read()
                return json.loads(content)
        except json.JSONDecodeError:
            logger.error(f"JSON decode error in {self.filepath}. Resetting file.")
            return {}
        except Exception as e:
            logger.error(f"Error loading strategies: {e}")
            raise StrategyError.ExecutionFailed(f"Failed to load strategies: {e}")

    async def _save_file(self, data: Dict[str, Any]) -> None:
        """Save data to JSON file asynchronously."""
        try:
            async with aiofiles.open(self.filepath, "w") as f:
                await f.write(json.dumps(data, indent=4))
        except Exception as e:
            logger.error(f"Error saving strategies: {e}")
            raise StrategyError.ExecutionFailed(f"Failed to save strategies: {e}")


def get_tools() -> List[Dict[str, Any]]:
    """Get tool definitions for LLM function calling"""
    return [
        {
            "type": "function",
            "function": {
                "name": "set_cdp_credentials",
                "description": "Set Coinbase Developer Platform API credentials",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cdpApiKey": {"type": "string", "description": "CDP API Key"},
                        "cdpApiSecret": {"type": "string", "description": "CDP API Secret"},
                    },
                    "required": ["cdpApiKey", "cdpApiSecret"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "handle_dollar_cost_average",
                "description": "Create a new dollar cost averaging strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "token_address": {
                            "type": "string",
                            "description": "Address of token to DCA into",
                        },
                        "amount": {"type": "string", "description": "Amount to invest per period"},
                        "interval": {
                            "type": "string",
                            "enum": [e.value for e in IntervalType],
                            "description": "Time between purchases",
                        },
                        "total_periods": {
                            "type": "integer",
                            "description": "Optional number of periods to run",
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Optional minimum price to execute purchase",
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Optional maximum price to execute purchase",
                        },
                        "max_slippage": {
                            "type": "number",
                            "description": "Maximum acceptable slippage percentage (default 1%)",
                            "default": 1.0,
                        },
                        "stop_loss": {"type": "number", "description": "Optional stop loss price"},
                        "take_profit": {
                            "type": "number",
                            "description": "Optional take profit price",
                        },
                    },
                    "required": ["token_address", "amount", "interval"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "handle_pause_dca",
                "description": "Pause an active DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {
                            "type": "string",
                            "description": "ID of the DCA strategy to pause",
                        }
                    },
                    "required": ["strategy_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "handle_resume_dca",
                "description": "Resume a paused DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {
                            "type": "string",
                            "description": "ID of the DCA strategy to resume",
                        }
                    },
                    "required": ["strategy_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "handle_cancel_dca",
                "description": "Cancel a DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {
                            "type": "string",
                            "description": "ID of the DCA strategy to cancel",
                        }
                    },
                    "required": ["strategy_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "handle_get_status",
                "description": "Get current status and metrics of a DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {"type": "string", "description": "ID of the DCA strategy"},
                        "include_history": {
                            "type": "boolean",
                            "description": "Include execution history in response",
                            "default": False,
                        },
                    },
                    "required": ["strategy_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "handle_check_health",
                "description": "Check health status of a DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {
                            "type": "string",
                            "description": "ID of the DCA strategy to check",
                        }
                    },
                    "required": ["strategy_id"],
                },
            },
        },
    ]


async def handle_get_status(strategy_id: str, include_history: bool = False) -> Dict[str, Any]:
    """Handler for getting strategy status"""
    try:
        store = JsonFileStrategyStore()
        strategy = await store.load(strategy_id)

        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")

        response = {
            "id": strategy.id,
            "status": strategy.status.value,
            "current_period": strategy.current_period,
            "last_execution": (
                strategy.last_execution.isoformat() if strategy.last_execution else None
            ),
            "next_execution": (
                strategy.next_execution.isoformat() if strategy.next_execution else None
            ),
            "metrics": strategy.calculate_metrics().to_dict(),
            "config": strategy.config.to_dict(),
        }

        if include_history:
            response["history"] = strategy.history
            response["status_history"] = strategy.metadata.get("status_history", [])

        return response

    except StrategyError.NotFound as e:
        logger.error(f"Strategy not found: {e}")
        return {"status": "error", "error": str(e)}
    except StrategyError.ExecutionFailed as e:
        logger.error(f"Execution error: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "error": "An unexpected error occurred."}


async def handle_pause_dca(strategy_id: str) -> Dict[str, Any]:
    """Handler for pausing DCA strategy"""
    try:
        store = JsonFileStrategyStore()
        strategy = await store.load(strategy_id)

        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")

        result = strategy.pause()
        if result.success:
            store.save(strategy)
            # Remove scheduled job
            scheduler.remove_job(strategy.id)

        return result.to_dict()

    except StrategyError.NotFound as e:
        logger.error(f"Strategy not found: {e}")
        return {"status": "error", "error": str(e)}
    except StrategyError.ExecutionFailed as e:
        logger.error(f"Execution error: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "error": "An unexpected error occurred."}


async def handle_resume_dca(strategy_id: str) -> Dict[str, Any]:
    """Handler for resuming DCA strategy"""
    try:
        store = JsonFileStrategyStore()
        strategy = await store.load(strategy_id)

        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")

        result = strategy.resume()
        if result.success:
            store.save(strategy)
            # Schedule next execution
            client = CDPClient()
            strategy._schedule_next_execution(client)

        return result.to_dict()

    except StrategyError.NotFound as e:
        logger.error(f"Strategy not found: {e}")
        return {"status": "error", "error": str(e)}
    except StrategyError.ExecutionFailed as e:
        logger.error(f"Execution error: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "error": "An unexpected error occurred."}


async def handle_cancel_dca(strategy_id: str) -> Dict[str, Any]:
    """Handler for cancelling DCA strategy"""
    try:
        store = JsonFileStrategyStore()
        strategy = await store.load(strategy_id)

        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")

        result = strategy.cancel()
        if result.success:
            store.save(strategy)
            # Remove scheduled job
            scheduler.remove_job(strategy.id)

        return result.to_dict()

    except StrategyError.NotFound as e:
        logger.error(f"Strategy not found: {e}")
        return {"status": "error", "error": str(e)}
    except StrategyError.ExecutionFailed as e:
        logger.error(f"Execution error: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "error": "An unexpected error occurred."}


async def handle_check_health(strategy_id: str) -> Dict[str, Any]:
    """Handler for checking strategy health"""
    try:
        store = JsonFileStrategyStore()
        strategy = await store.load(strategy_id)

        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")

        health_status = strategy.check_health()
        metrics = strategy.calculate_metrics()

        response = {
            "status": health_status.value,
            "strategy_id": strategy_id,
            "current_status": strategy.status.value,
            "last_execution": (
                strategy.last_execution.isoformat() if strategy.last_execution else None
            ),
            "next_execution": (
                strategy.next_execution.isoformat() if strategy.next_execution else None
            ),
            "error_count": strategy.metadata.get("error_count", 0),
            "metrics": metrics.to_dict(),
            "warnings": [],
        }

        # Add relevant warnings
        if health_status == HealthStatus.WARNING:
            response["warnings"].append("Strategy execution is delayed")
        elif health_status == HealthStatus.CRITICAL:
            response["warnings"].append("Strategy execution is critically delayed")

        if metrics.failed_txs > 0:
            response["warnings"].append(f"Strategy has {metrics.failed_txs} failed transactions")

        return response

    except StrategyError.NotFound as e:
        logger.error(f"Strategy not found: {e}")
        return {"status": "error", "error": str(e)}
    except StrategyError.ExecutionFailed as e:
        logger.error(f"Execution error: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "error": "An unexpected error occurred."}
