import requests
import logging
import time
from gasless_agent.src.config import Config
from cdp import Cdp

class InsufficientFundsError(Exception):
    pass

def send_gasless_transaction(address, toAddress, amount):
    cdp = Cdp.configure('')

    time.sleep(2)

    transfer = address.transfer(amount, "usdc", toAddress, gasless=True).wait()

    return {
        "gasless_usdc_transfer": transfer
    }, "gasless_usdc_transfer"

def get_tools():

    """Return a list of tools for the agent."""
    return [
        {
            "type": "function",
            "function": {
                "name": "gasless_usdc_transfer",
                "description": "transfer a small amount of a usdc to another user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "toAddress": {
                            "type": "string",
                            "description": "address of the user to transfer the token to"
                        },
                        "amount": {
                            "type": "string",
                            "description": "amount of the usdc to transfer"
                        },
                    },
                    "required": ["toAddress", "amount"]
                }
            }
        }
    ]