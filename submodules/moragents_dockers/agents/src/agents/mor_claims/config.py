from src.models.service.agent_config import AgentConfig


class Config:
    """Configuration for MOR Claims Agent."""

    # *************
    # AGENT CONFIG
    # *************

    agent_config = AgentConfig(
        path="src.agents.mor_claims.agent",
        class_name="MORClaimsAgent",
        description="Handles MOR token claims and rewards distribution",
        human_readable_name="MOR Claims Manager",
        command="morclaims",
        upload_required=False,
    )

    # *************
    # TOOLS CONFIG
    # *************

    tools = [
        {
            "name": "claim_rewards",
            "description": "Claim MOR rewards for a pool",
            "parameters": {
                "type": "object",
                "properties": {
                    "pool_id": {"type": "string", "description": "ID of the pool to claim from"},
                    "receiver": {"type": "string", "description": "Address to receive the rewards"},
                },
                "required": ["pool_id", "receiver"],
            },
        },
        {
            "name": "get_claimable_amount",
            "description": "Get claimable MOR reward amount for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "pool_id": {"type": "string", "description": "Pool ID to check rewards for"},
                    "user": {"type": "string", "description": "User address to check rewards for"},
                },
                "required": ["pool_id", "user"],
            },
        },
    ]

    # *************
    # CONTRACT CONFIG
    # *************

    WEB3RPCURL = {"1": "https://eth.llamarpc.com/"}
    MINT_FEE = 0.001  # in ETH

    DISTRIBUTION_PROXY_ADDRESS = "0x47176B2Af9885dC6C4575d4eFd63895f7Aaa4790"
    DISTRIBUTION_ABI = [
        {
            "inputs": [
                {"internalType": "uint256", "name": "poolId_", "type": "uint256"},
                {"internalType": "address", "name": "receiver_", "type": "address"},
            ],
            "name": "claim",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "poolId_", "type": "uint256"},
                {"internalType": "address", "name": "user_", "type": "address"},
            ],
            "name": "getCurrentUserReward",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]
