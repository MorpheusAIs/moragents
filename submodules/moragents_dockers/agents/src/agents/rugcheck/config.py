from typing import Dict, Optional
import re


class TokenRegistry:
    """Registry for mapping between token names and mint addresses."""

    def __init__(self):
        # This mapping should be regularly updated with the most popular tokens
        self._name_to_mint = {
            "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
            "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",  # Raydium
            "MEAN": "MEANeD3XDdUmNMsRGjASkSWdC8prLYsoRJ61pPeHctD",  # Mean Protocol
            "SAMO": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",  # Samoyedcoin
            "PYTH": "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",  # Pyth Network
            "ORCA": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",  # Orca
            "MNGO": "MangoCzJ36AjZyKwVj3VnYU4GTonjfVEnJmvvWaxLac",  # Mango Markets
            "MSOL": "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",  # Marinade Staked SOL
            "STSOL": "7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj",  # Lido Staked SOL
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USD Coin
            "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # Tether USD
            "SLND": "SLNDpmoWTVADgEdndyvWzroNL7zSi1dF9PC3xHGtPwp",  # Solend
            "DUST": "DUSTawucrTsGU8hcqRdHDCbuYhCPADMLM2VcCb8VnFnQ",  # DUST Protocol
            "GENE": "GENEtH5amGSi8kHAtQoezp1XEXwZJ8vcuePYnXdKrMYz",  # Genopets
            "COPE": "8HGyAAB1yoM1ttS7pXjHMa3dukTFGQggnFFH3hJZgzQh",  # Cope
            "ATLAS": "ATLASXmbPQxBUYbxPsV97usA3fPQYEqzQBUHgiFCUsXx",  # Star Atlas
            "POLIS": "poLisWXnNRwC6oBu1vHiuKQzFjGL4XDSu4g9qjz9qVk",  # Star Atlas DAO
            "STEP": "StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT",  # Step Finance
            "FIDA": "EchesyfXePKdLtoiZSL8pBe8Myagyy8ZRqsACNCFGnvp",  # Bonfida
            "AUDIO": "9LzCMqDgTKYz9Drzqnpgee3SGa89up3a247ypMj2xrqM",  # Audius
            "GOFX": "GFX1ZjR2P15tmrSwow6FjyDYcEkoFb4p4gJCpLBjaxHD",  # GooseFX
            "WOOF": "WoofbQN7GgYf7gmHW6KcQKAHZxUPC9kpvFHxbg9bVhk",  # WOOF
            "SHDW": "SHDWyBxihqiCj6YekG2GUr7wqKLeLAMK1gHZck9pL6y",  # GenesysGo Shadow
            "SLIM": "xxxxa1sKNGwFtw2kFn8XauW9xq8hBZ5kVtcSesTT9fW",  # Solanium
            "GRAPE": "8upjSpvjcdpuzhfR1zriwg5NXkwDruejqNE9WNbPRtyA",  # Grape Protocol
            "MNDE": "MNDEFzGvMt87ueuHvVU9VcTqsAP5b3fTGPsHuuPA5ey",  # Marinade
            "LARIX": "Lrxqnh6ZHKbGy3dcrCED43nsoLkM1LTzU2jRfWe8qUC",  # Larix
            "PORT": "PoRTjZMPXb9T7dyU7tpLEZRQj7e6ssfAE62j2oQuc6y",  # Port Finance
            "TULIP": "TuLipcqtGVXP9XR62wM8WWCm6a9vhLs7T1uoWBk6FDs",  # Tulip Protocol
            "SUNNY": "SUNNYWgPQmFxe9wTZzNK7iPnJ3vYDrkgnxJRJm1s3ag",  # Sunny Aggregator
            "JET": "JET6zMJWkCN9tpRT2v2jfAmm5VnQFDpUBCyaKojmGtz",  # Jet Protocol
            "LIKE": "3bRTivrVsitbmCTGtqwp7hxXPsybkjn4XLNtPsHqa3zR",  # Only1
            "MEDIA": "ETAtLmCmsoiEEKfNrHKJ2kYy3MoABhU6NQvpSfij5tDs",  # Media Network
            "NINJA": "FgX1WD9WzMU3yLwXaFSarPfkgzjLb2DZCqmkx9ExpuvJ",  # NINJA
            "SLRS": "SLRSSpSLUTP7okbCUBYStWCo1vUgyt775faPqz8HUMr",  # Solrise Finance
            "SNY": "4dmKkXNHdgYsXqBHCuMikNQWwVomZURhYvkkX5c4pQ7y",  # Synthetify
            "APEX": "APXmJPZH6fBxPWGVj7sGrXtqeWHGkM4pYdWuqk7eXbAx",  # ApeXit Finance
            "AURY": "AURYydfxJib1ZkTir1Jn1J9ECYUtjb6rKQVmtYaixWPP",  # Aurory
            "REAL": "AD27ov5fVU2XzwsbvnFvb1JpCBaCB5dRXrczV9CqSVGb",  # Realy
            "PRISM": "PRSMNsEPqhGVCH1TtWiJqPjJyh2cKrLostPZTNy1o5x",  # Prism
            "WAGMI": "WAGMiLpXJmVJ6YP7JHexwGigqYR4ixZpXxhYHKsEQK1",  # WAGMI
            "SONAR": "sonarX4VtVkQemriJeLm6CKeW3GDMyiBnnAEMw1MRAE",  # Sonar Watch
            "SOLI": "SoLiKzaMnqwf7kKGFC9FNVx9rJqhAHwZPFH9m5KyXkq",  # Solana Ecosystem Index
            "SOLC": "SoLCpYyX2TtZpyJHZDPKaS1j3WNmq2HhKqKiDwjARKf",  # Solcial
            "SOLAPE": "GHvFFSZ9BctWsEc5nujR1MTmmJWY7tgQz2AXE6WVFtGN",  # SolAPE Finance
            "SOLPAD": "SLPDHwdx8q1GLhxhL7QZf4KV4wgBpYM8YQqJvvk6xyo",  # Solpad Finance
            "SOLR": "SoLRaZqNUZtXtguY1iQsEEmX3auDjGg6aBeMKWBZzTv",  # SolRazr
            "SOLX": "SoLXBoWmcYdPQLM8L4Yfb6eD9HSQKVwd5kKDfxvUm3p",  # Soldex
            "SOLY": "SoLYvpNxvA6xG5tS4LVDkGGR9QGXUwNVQhMGoVe8e5q",  # Solyard Finance
        }

        # Create reverse mapping
        self._mint_to_name = {v: k for k, v in self._name_to_mint.items()}

        # Compile regex pattern for Solana mint addresses (base58 encoded public keys)
        self._mint_pattern = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")

    def get_mint_by_name(self, name: str) -> Optional[str]:
        """Get mint address for a token name (case-insensitive)."""
        return self._name_to_mint.get(name.upper())

    def get_name_by_mint(self, mint: str) -> Optional[str]:
        """Get token name for a mint address."""
        return self._mint_to_name.get(mint)

    def is_valid_mint_address(self, address: str) -> bool:
        """Check if a string matches the pattern of a Solana mint address."""
        return bool(self._mint_pattern.match(address))


class Config:
    """Configuration for RugcheckAgent tools."""

    tools = [
        {
            "name": "get_token_report",
            "description": "Generate a report summary for a given token using either its name or mint address",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "description": "Token name (e.g., 'BONK', 'RAY') or mint address"}
                },
                "required": ["identifier"],
            },
        },
        {
            "name": "get_most_viewed",
            "description": "Get most viewed tokens in past 24 hours",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "get_most_voted",
            "description": "Get most voted tokens in past 24 hours",
            "parameters": {"type": "object", "properties": {}},
        },
    ]
