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
