class Config:
    tools = [
        {
            "name": "swap_assets",
            "description": "Swap one asset for another (Base Mainnet only)",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "string", "description": "Amount to swap"},
                    "from_asset_id": {"type": "string", "description": "Asset ID to swap from"},
                    "to_asset_id": {"type": "string", "description": "Asset ID to swap to"},
                },
                "required": ["amount", "from_asset_id", "to_asset_id"],
            },
        },
        {
            "name": "transfer_asset",
            "description": "Transfer an asset to another address",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "string", "description": "Amount to transfer"},
                    "asset_id": {"type": "string", "description": "Asset ID to transfer"},
                },
                "required": ["amount", "asset_id"],
            },
        },
        {
            "name": "get_balance",
            "description": "Get balance of a specific asset",
            "parameters": {
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string", "description": "Asset ID to check balance for"}
                },
                "required": ["asset_id"],
            },
        },
        # TODO: Add more base tools / functionality
        # {
        #     "name": "create_token",
        #     "description": "Create a new ERC-20 token",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "name": {"type": "string", "description": "Name of the token"},
        #             "symbol": {"type": "string", "description": "Symbol of the token"},
        #             "initial_supply": {
        #                 "type": "integer",
        #                 "description": "Initial supply of tokens",
        #             },
        #         },
        #         "required": ["name", "symbol", "initial_supply"],
        #     },
        # },
        # {
        #     "name": "request_eth_from_faucet",
        #     "description": "Request ETH from testnet faucet",
        #     "parameters": {"type": "object", "properties": {}},
        # },
        # {
        #     "name": "mint_nft",
        #     "description": "Mint an NFT to an address",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "contract_address": {"type": "string", "description": "NFT contract address"},
        #             "mint_to": {"type": "string", "description": "Address to mint NFT to"},
        #         },
        #         "required": ["contract_address", "mint_to"],
        #     },
        # },
        # {
        #     "name": "register_basename",
        #     "description": "Register a basename for the agent's wallet",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "basename": {"type": "string", "description": "Basename to register"},
        #             "amount": {
        #                 "type": "number",
        #                 "description": "Amount of ETH to pay for registration",
        #                 "default": 0.002,
        #             },
        #         },
        #         "required": ["basename"],
        #     },
        # },
    ]
