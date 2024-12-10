loop_delay = 10  # prevent rate limiting

price_error_tolerance = 0.01  # 1%
mcap_error_tolerance = 0.01  # 1%

coins = [
    {"coingecko_id": "bitcoin", "name_variations": ["Bitcoin", "Bitcoins", "BITcoin", "BTC"]},
    {"coingecko_id": "ethereum", "name_variations": ["Ether", "Ethereum", "Ethers", "ETH"]},
    {"coingecko_id": "tether", "name_variations": ["Tether", "USDT", "USDTether", "TetherUSD"]},
    {
        "coingecko_id": "binancecoin",
        "name_variations": ["BNB", "Binance Smart Chain", "Binancecoin", "Binance coin"],
    },
    {"coingecko_id": "solana", "name_variations": ["Solana", "SOL", "Solanacoin"]},
    {"coingecko_id": "usd-coin", "name_variations": ["USDC", "USDCoin", "USD coin", "CUSD"]},
    {
        "coingecko_id": "staked-ether",
        "name_variations": ["Lido Staked Ether", "Lido Ether", "Lido Eth", "Staked Ether"],
    },
    {"coingecko_id": "ripple", "name_variations": ["XRP", "Ripple", "XRPcoin", "XRP coin"]},
    {
        "coingecko_id": "the-open-network",
        "name_variations": ["Toncoin", "TON", "the open network", "open network coin"],
    },
    {"coingecko_id": "dogecoin", "name_variations": ["Dogecoin", "DOGE", "dogcoin", "doge coin"]},
    {"coingecko_id": "cardano", "name_variations": ["Cardano", "ADA", "cardano coin"]},
    {"coingecko_id": "tron", "name_variations": ["Tron", "TRX", "troncoin", "trxcoin"]},
    {
        "coingecko_id": "avalanche-2",
        "name_variations": ["Avalanche", "AVAX", "Avalancecoin", "Avaxcoin"],
    },
    {
        "coingecko_id": "shiba-inu",
        "name_variations": ["Shiba Inu", "Shiba", "SHIB", "shibacoin", "Shiba inu coin"],
    },
    {
        "coingecko_id": "wrapped-bitcoin",
        "name_variations": ["Wrapped Bitcoin", "WBTC", "wrapped btc", "wrapped BITcoin"],
    },
    {
        "coingecko_id": "polkadot",
        "name_variations": ["Polkadot", "DOT", "polkadotcoin", "polka dot coin", "polka coin"],
    },
    {
        "coingecko_id": "chainlink",
        "name_variations": ["Chainlink", "LINK", "Chainlinkcoin", "Linkcoin"],
    },
    {
        "coingecko_id": "bitcoin-cash",
        "name_variations": ["Bitcoin Cash", "BCH", "BTC cash", "BCHcoin"],
    },
    {"coingecko_id": "uniswap", "name_variations": ["Uniswap", "UNI", "Unicoin", "Uniswap coin"]},
    {"coingecko_id": "leo-token", "name_variations": ["LEO token", "LEO", "leotoken", "leocoin"]},
    {"coingecko_id": "dai", "name_variations": ["Dai", "Daicoin", "DaiUSD"]},
    {"coingecko_id": "near", "name_variations": ["Near Protocol", "NEAR", "Nearcoin"]},
    {"coingecko_id": "litecoin", "name_variations": ["Litecoin", "LTC", "LTCcoin", "lightcoin"]},
    {
        "coingecko_id": "matic-network",
        "name_variations": ["Polygon", "Matic", "MATIC", "Polygoncoin", "Maticcoin"],
    },
    {
        "coingecko_id": "wrapped-eeth",
        "name_variations": ["Wrapped eETH", "eETH", "WEETH", "eETHcoin", "WEETHcoin"],
    },
    {"coingecko_id": "kaspa", "name_variations": ["Kaspa", "KAS", "Kaspacoin", "Kascoin"]},
    {"coingecko_id": "pepe", "name_variations": ["Pepe", "Pepecoin"]},
    {
        "coingecko_id": "ethena-usde",
        "name_variations": ["Ethena", "USDE", "Ethena USD", "Ethenacoin", "USDEcoin"],
    },
    {
        "coingecko_id": "internet-computer",
        "name_variations": ["Internet Computer", "ICP", "ICPcoin", "InternetComputercoin"],
    },
    {
        "coingecko_id": "renzo-restaked-eth",
        "name_variations": [
            "Renzo Restaked ETH",
            "Renzo Restaked Ethereum",
            "Renzocoin",
            "RenzoEth",
        ],
    },
    {
        "coingecko_id": "ethereum-classic",
        "name_variations": ["Ethereum Classic", "Ether Classic", "ETH Classic", "ETC"],
    },
    {
        "coingecko_id": "fetch-ai",
        "name_variations": [
            "Artificial Superintelligence Alliance",
            "FET",
            "FETcoin",
            "Fetch",
            "Ocean Protocol",
            "Oceancoin",
            "Singularity",
            "Singularitycoin",
        ],
    },
    {"coingecko_id": "monero", "name_variations": ["Monero", "XMR", "Monerocoin", "XMRcoin"]},
    {"coingecko_id": "aptos", "name_variations": ["Aptos", "APT", "Aptoscoin", "APTcoin"]},
    {
        "coingecko_id": "render-token",
        "name_variations": ["Render", "RNDR", "Rendercoin", "RNDRcoin", "Render token"],
    },
    {"coingecko_id": "stellar", "name_variations": ["Stellar", "XLM", "Stellarcoin", "XLMcoin"]},
    {
        "coingecko_id": "hedera-hashgraph",
        "name_variations": ["Hedera", "HBAR", "Hederacoin", "HBARcoin", "Hashgraph"],
    },
    {
        "coingecko_id": "cosmos",
        "name_variations": ["Cosmos", "Cosmoshub", "ATOM", "Cosmoscoin", "ATOMCoin"],
    },
    {"coingecko_id": "arbitrum", "name_variations": ["Arbitrum", "ARB", "Arbitrumcoin", "ARBCoin"]},
    {
        "coingecko_id": "crypto-com-chain",
        "name_variations": ["Cronos", "CRO", "Cronoscoin", "CROCoin", "Crypto.com"],
    },
    {"coingecko_id": "mantle", "name_variations": ["Mantle", "MNT", "Mantlecoin", "MNTCoin"]},
    {
        "coingecko_id": "blockstack",
        "name_variations": ["Stacks", "STX", "Stackscoin", "STXCoin", "Blockstack"],
    },
    {"coingecko_id": "filecoin", "name_variations": ["Filecoin", "FIL", "FILCoin", "File coin"]},
    {"coingecko_id": "okb", "name_variations": ["OKB", "OKBCoin"]},
    {
        "coingecko_id": "maker",
        "name_variations": ["Maker", "MKR", "MakerDAO", "Makercoin", "MRKCoin"],
    },
    {"coingecko_id": "vechain", "name_variations": ["VeChain", "VET", "VeChaincoin", "VETCoin"]},
    {
        "coingecko_id": "injective-protocol",
        "name_variations": ["Injective", "INJ", "Injectivecoin", "INJCoin", "Injective Protocol"],
    },
    {
        "coingecko_id": "immutable-x",
        "name_variations": ["Immutable", "IMX", "Immutablecoin", "IMXCoin", "ImmutableX"],
    },
    {
        "coingecko_id": "first-digital-usd",
        "name_variations": ["First Digital USD", "FDUSD", "FirstDigitalUSD", "FDUSDCoin"],
    },
    {"coingecko_id": "optimism", "name_variations": ["Optimism", "OP", "Optimismcoin", "OPCoin"]},
    {"coingecko_id": "morpheusai", "name_variations": ["Morpheus", "MorpheusAI", "MOR", "MORCoin"]},
    {"coingecko_id": "aave", "name_variations": ["Aave", "Aavecoin"]},
    {
        "coingecko_id": "aavegotchi",
        "name_variations": ["Aavegotchi", "Ghost", "Aavegotchicoin", "Ghostcoin", "GHST"],
    },
    {
        "coingecko_id": "thorchain",
        "name_variations": ["Thor", "THORChain", "RUNE", "Thorcoin", "Runecoin"],
    },
    {
        "coingecko_id": "ethereum-name-service",
        "name_variations": ["Ethereum Name Service", "ENS", "ENScoin"],
    },
    {
        "coingecko_id": "axie-infinity",
        "name_variations": ["Axie Infinity", "AXS", "Axiecoin", "Axscoin"],
    },
    {"coingecko_id": "zombiecoin", "name_variations": ["ZombieCoin", "Zombie", "ZMBCoin"]},
    {
        "coingecko_id": "elon-xmas",
        "name_variations": ["Elon Xmas", "XMAS", "ElonXmascoin", "XMASCoin"],
    },
    {"coingecko_id": "neblio", "name_variations": ["Neblio", "NEBL", "Nebliocoin", "NEBLCoin"]},
    {
        "coingecko_id": "shapeshift-fox-token",
        "name_variations": [
            "ShapeShift FOX",
            "ShapeShift",
            "ShapeShiftCoin",
            "FOXCoin",
            "FOXToken",
        ],
    },
]

price_prompts = [
    "What is the price of {}?",
    "How much is one {} worth?",
    "How much does one {} cost?",
]

mcap_prompts = [
    "What is the market cap of {}?",
    "What is the total market cap of {}?",
    "What is the marketcap of {}?",
    "What is the market capitalization of {}?",
    "What is the value of all {}s?",
]

# This is unused at the moment
tvl_prompts = [
    "What is the TVL of {}?",
    "How much value is locked in {}?",
]
