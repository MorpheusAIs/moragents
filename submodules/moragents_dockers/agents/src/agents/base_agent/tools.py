import logging
import time

import requests
from cdp import Cdp, Transaction, Wallet
from src.agents.base_agent.config import Config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InsufficientFundsError(Exception):
    pass


def send_gasless_usdc_transaction(toAddress, amount):

    client = Cdp.configure("", "")

    logger.info(f"Client successfully configured: {client}")

    wallet1 = Wallet.create()

    logger.info(f"Wallet successfully created: {wallet1}")
    logger.info(f"Wallet address: {wallet1.default_address}")

    eth_faucet_tx = wallet1.faucet()

    usdc_faucet_tx = wallet1.faucet(asset_id="usdc")

    logger.info(f"Faucet transaction successfully sent: {eth_faucet_tx}")
    logger.info(f"Faucet transaction successfully sent: {usdc_faucet_tx}")

    logger.info(f"Faucet transaction successfully completed: {eth_faucet_tx}")
    logger.info(f"Faucet transaction successfully completed: {usdc_faucet_tx}")

    address = wallet1.default_address

    logger.info(f"Address: {address}")

    time.sleep(2)

    transfer = address.transfer(amount, "usdc", toAddress, gasless=True).wait()

    logger.info(f"Transfer transaction: {transfer}")

    return {"success": "Transfer transaction successful"}, "gasless_usdc_transfer"


def send_eth_transaction(toAddress, amount):

    client = Cdp.configure("", "")

    logger.info(f"Client successfully configured: {client}")

    wallet1 = Wallet.create()

    logger.info(f"Wallet successfully created: {wallet1}")
    logger.info(f"Wallet address: {wallet1.default_address}")

    faucet_tx = wallet1.faucet()

    logger.info(f"Faucet transaction successfully sent: {faucet_tx}")

    logger.info(f"Faucet transaction successfully completed: {faucet_tx}")

    address = wallet1.default_address

    logger.info(f"Address: {address}")

    time.sleep(2)

    transfer = wallet1.transfer(amount, "eth", toAddress).wait()

    logger.info(f"Transfer transaction: {transfer}")

    return {"success": "Transfer transaction successful"}, "eth_transfer"


def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "gasless_usdc_transfer",
                "description": "Transfer a small amount of USDC to another user gaslessly.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "toAddress": {"type": "string", "description": "Recipient's address."},
                        "amount": {"type": "string", "description": "Amount of USDC to transfer."},
                    },
                    "required": ["toAddress", "amount"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "eth_transfer",
                "description": "Transfer ETH to another user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "toAddress": {"type": "string", "description": "Recipient's address."},
                        "amount": {"type": "string", "description": "Amount of ETH to transfer."},
                    },
                    "required": ["toAddress", "amount"],
                },
            },
        },
    ]
