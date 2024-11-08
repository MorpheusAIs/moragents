import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)


# Configuration object
class Config:
    WEB3RPCURL = {
        "1": "https://eth.llamarpc.com/",
    }

    DISTRIBUTION_PROXY_ADDRESS = "0x47176B2Af9885dC6C4575d4eFd63895f7Aaa4790"
    DISTRIBUTION_ABI = [
        {
            "inputs": [
                {"internalType": "uint256", "name": "poolId_", "type": "uint256"},
                {"internalType": "address", "name": "user_", "type": "address"},
            ],
            "name": "getCurrentUserReward",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        }
    ]


test_cases = [
    {
        "pool_id": 1,
        "wallet_address": "0x62aF7c48Cf412162465A8CaFdE44dFb17bA96038",
    },
    {
        "pool_id": 1,
        "wallet_address": "0xC3B82270Db1b77B4bE28a83d0963e02c38A9d13f",
    },
    {
        "pool_id": 1,
        "wallet_address": "0x03aa1e85487a5c3c509bc584ad9490a41d248011",
    },
    {
        "pool_id": 1,
        "wallet_address": "0xEb4E7939C3bCC0635b8531e3C0a6bD42de95cfeF",
    },
    {
        "pool_id": 1,
        "wallet_address": "0x5CD4C60f0e566dCa1Ae8456C36a63bc7A8D803de",
    },
]

reward_check_prompts = [
    "i want to check my mor rewards",
    "check my mor rewards",
    "check my rewards",
    "please check my mor rewards",
    "hi, check my mor rewards",
]
