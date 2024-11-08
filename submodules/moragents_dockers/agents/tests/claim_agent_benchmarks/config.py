class Config:
    URL = "http://127.0.0.1:5000/"
    HEADERS = {"Content-Type": "application/json"}

    # Test wallet addresses
    WALLET_ADDRESSES = [{"wallet": "0x48d0EAc727A7e478f792F16527012452a000f2bd"}]

    PROMPTS = {"claim_request": "I want to claim my MOR", "proceed": "yes"}
