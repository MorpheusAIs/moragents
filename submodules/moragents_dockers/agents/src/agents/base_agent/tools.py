from typing import Dict, Any, Tuple
from cdp import Wallet


def create_token(
    agent_wallet: Wallet, name: str, symbol: str, initial_supply: int
) -> Tuple[Dict[str, Any], str]:
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
        }, "create_token"
    except Exception as e:
        raise Exception(f"Failed to create token: {str(e)}")


def transfer_asset(
    agent_wallet: Wallet, amount: str, asset_id: str, destination_address: str
) -> Tuple[Dict[str, Any], str]:
    """Transfer an asset to another address"""
    try:
        is_mainnet = agent_wallet.network_id == "base-mainnet"
        is_usdc = asset_id.lower() == "usdc"
        gasless = is_mainnet and is_usdc

        transfer = agent_wallet.transfer(
            amount=amount, asset_id=asset_id, to_address=destination_address, gasless=gasless
        )
        transfer.wait()

        return {
            "success": True,
            "tx_hash": transfer.hash,
            "from": agent_wallet.default_address.address_id,
            "to": destination_address,
            "amount": amount,
            "asset": asset_id,
        }, "transfer_asset"
    except Exception as e:
        raise Exception(f"Failed to transfer asset: {str(e)}")


def get_balance(agent_wallet: Wallet, asset_id: str) -> Tuple[Dict[str, Any], str]:
    """Get balance of a specific asset"""
    try:
        balance = agent_wallet.balance(asset_id)
        return {
            "success": True,
            "asset": asset_id,
            "balance": str(balance),
            "address": agent_wallet.default_address.address_id,
        }, "get_balance"
    except Exception as e:
        raise Exception(f"Failed to get balance: {str(e)}")


def request_eth_from_faucet(agent_wallet: Wallet) -> Tuple[Dict[str, Any], str]:
    """Request ETH from testnet faucet"""
    try:
        if agent_wallet.network_id == "base-mainnet":
            raise Exception("Faucet only available on testnet")

        faucet_tx = agent_wallet.faucet()
        return {
            "success": True,
            "address": agent_wallet.default_address.address_id,
        }, "request_eth_from_faucet"
    except Exception as e:
        raise Exception(f"Failed to request from faucet: {str(e)}")


def deploy_nft(
    agent_wallet: Wallet, name: str, symbol: str, base_uri: str
) -> Tuple[Dict[str, Any], str]:
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
        }, "deploy_nft"
    except Exception as e:
        raise Exception(f"Failed to deploy NFT: {str(e)}")


def mint_nft(
    agent_wallet: Wallet, contract_address: str, mint_to: str
) -> Tuple[Dict[str, Any], str]:
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
        }, "mint_nft"
    except Exception as e:
        raise Exception(f"Failed to mint NFT: {str(e)}")


def swap_assets(
    agent_wallet: Wallet, amount: str, from_asset_id: str, to_asset_id: str
) -> Tuple[Dict[str, Any], str]:
    """Swap one asset for another (Base Mainnet only)"""
    try:
        if agent_wallet.network_id != "base-mainnet":
            raise Exception("Asset swaps only available on Base Mainnet")

        trade = agent_wallet.trade(amount, from_asset_id, to_asset_id)
        trade.wait()

        return {
            "success": True,
            "tx_hash": trade.hash,
            "from_asset": from_asset_id,
            "to_asset": to_asset_id,
            "amount": amount,
        }, "swap_assets"
    except Exception as e:
        raise Exception(f"Failed to swap assets: {str(e)}")


def register_basename(
    agent_wallet: Wallet, basename: str, amount: float = 0.002
) -> Tuple[Dict[str, Any], str]:
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
        }, "register_basename"
    except Exception as e:
        raise Exception(f"Failed to register basename: {str(e)}")
