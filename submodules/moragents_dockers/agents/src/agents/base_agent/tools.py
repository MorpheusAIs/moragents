import logging
from typing import Dict, Any
from cdp import Wallet

logger = logging.getLogger(__name__)


def swap_assets(
    agent_wallet: Wallet, amount: str, from_asset_id: str, to_asset_id: str
) -> Dict[str, Any]:
    """Swap one asset for another (Base Mainnet only)"""
    try:
        if agent_wallet.network_id != "base-mainnet":
            raise Exception("Asset swaps only available on Base Mainnet")

        from_asset_id = from_asset_id.lower()
        to_asset_id = to_asset_id.lower()
        logger.info(f"Attempting swap on Base Mainnet:")
        logger.info(f"From asset: {from_asset_id}")
        logger.info(f"To asset: {to_asset_id}")
        logger.info(f"Amount: {amount}")

        # Check wallet balance
        balance = agent_wallet.balance(from_asset_id)
        logger.info(f"Wallet balance of {from_asset_id}: {balance}")

        if float(balance) < float(amount):
            raise Exception(f"Insufficient balance. Have {balance}, need {amount}")

        try:
            trade = agent_wallet.trade(amount, from_asset_id, to_asset_id)
            logger.info(f"Trade constructed: {trade}")
        except Exception as e:
            if "internal" in str(e).lower():
                raise Exception(
                    "Not enough ETH. Please ensure you have sufficient ETH for gas fees."
                )
            raise e

        trade.wait()
        logger.info(f"Trade completed")

        return {
            "success": True,
            "from_asset": from_asset_id,
            "to_asset": to_asset_id,
            "amount": amount,
        }
    except Exception as e:
        logger.error(f"Swap failed: {str(e)}", exc_info=True)
        raise Exception(f"Failed to swap assets: {str(e)}")


def transfer_asset(
    agent_wallet: Wallet, amount: str, asset_id: str, destination_address: str
) -> Dict[str, Any]:
    """Transfer an asset to another address"""
    try:
        # Create the transfer
        gasless = agent_wallet.network_id == "base-mainnet" and asset_id.lower() == "usdc"
        transfer = agent_wallet.default_address.transfer(
            amount=amount, asset_id=asset_id, destination=destination_address, gasless=gasless
        )

        # Wait for transfer to settle and return status
        transfer.wait()

        return {
            "success": transfer.status,
            "from": agent_wallet.default_address.address_id,
            "to": destination_address,
            "amount": amount,
            "asset": asset_id,
            "transaction_link": transfer.transaction_link,
        }

    except Exception as e:
        raise Exception(f"Failed to transfer asset: {str(e)}")


def get_balance(agent_wallet: Wallet, asset_id: str) -> Dict[str, Any]:
    """Get balance of a specific asset"""
    try:
        balance = agent_wallet.balance(asset_id)
        return {
            "success": True,
            "asset": asset_id,
            "balance": str(balance),
            "address": agent_wallet.default_address.address_id,
        }
    except Exception as e:
        raise Exception(f"Failed to get balance: {str(e)}")


# -----------------------------------------------------
# The following functions need to be fleshed out later:
# -----------------------------------------------------


def create_token(
    agent_wallet: Wallet, name: str, symbol: str, initial_supply: int
) -> Dict[str, Any]:
    """Create a new ERC-20 token"""
    try:
        deployed_contract = agent_wallet.deploy_token(name, symbol, initial_supply)
        deployed_contract.wait()

        return {
            "success": True,
            "contract_address": deployed_contract.contract_address,
            "name": name,
            "symbol": symbol,
            "supply": initial_supply,
        }
    except Exception as e:
        raise Exception(f"Failed to create token: {str(e)}")


def request_eth_from_faucet(agent_wallet: Wallet) -> Dict[str, Any]:
    """Request ETH from testnet faucet"""
    try:
        if agent_wallet.network_id == "base-mainnet":
            raise Exception("Faucet only available on testnet")

        faucet_tx = agent_wallet.faucet()
        return {
            "success": True,
            "address": agent_wallet.default_address.address_id,
        }
    except Exception as e:
        raise Exception(f"Failed to request from faucet: {str(e)}")


def deploy_nft(agent_wallet: Wallet, name: str, symbol: str, base_uri: str) -> Dict[str, Any]:
    """Deploy an ERC-721 NFT contract"""
    try:
        deployed_nft = agent_wallet.deploy_nft(name, symbol, base_uri)
        deployed_nft.wait()

        return {
            "success": True,
            "contract_address": deployed_nft.contract_address,
            "name": name,
            "symbol": symbol,
            "base_uri": base_uri,
        }
    except Exception as e:
        raise Exception(f"Failed to deploy NFT: {str(e)}")


def mint_nft(agent_wallet: Wallet, contract_address: str, mint_to: str) -> Dict[str, Any]:
    """Mint an NFT to an address"""
    try:
        mint_args = {"to": mint_to, "quantity": "1"}
        mint_tx = agent_wallet.invoke_contract(
            contract_address=contract_address, method="mint", args=mint_args
        )
        mint_tx.wait()

        return {
            "success": True,
            "tx_hash": mint_tx.hash,
            "contract": contract_address,
            "recipient": mint_to,
        }
    except Exception as e:
        raise Exception(f"Failed to mint NFT: {str(e)}")


def register_basename(agent_wallet: Wallet, basename: str, amount: float = 0.002) -> Dict[str, Any]:
    """Register a basename for the agent's wallet"""
    try:
        address_id = agent_wallet.default_address.address_id
        is_mainnet = agent_wallet.network_id == "base-mainnet"

        suffix = ".base.eth" if is_mainnet else ".basetest.eth"
        if not basename.endswith(suffix):
            basename += suffix

        contract_address = (
            "0x4cCb0BB02FCABA27e82a56646E81d8c5bC4119a5"
            if is_mainnet
            else "0x49aE3cC2e3AA768B1e5654f5D3C6002144A59581"
        )

        register_tx = agent_wallet.invoke_contract(
            contract_address=contract_address,
            method="register",
            args={"name": basename},
            amount=amount,
            asset_id="eth",
        )
        register_tx.wait()

        return {
            "success": True,
            "tx_hash": register_tx.hash,
            "basename": basename,
            "owner": address_id,
        }
    except Exception as e:
        raise Exception(f"Failed to register basename: {str(e)}")
