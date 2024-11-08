import logging

logging.basicConfig(level=logging.INFO)


class Config:
    # RSS Feed URL
    GOOGLE_NEWS_BASE_URL = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"

    # Time window for news (in hours)
    NEWS_TIME_WINDOW = 24

    # Number of articles to show per token
    ARTICLES_PER_TOKEN = 1

    # LLM configuration
    LLM_MAX_TOKENS = 150
    LLM_TEMPERATURE = 0.3

    # Prompts
    RELEVANCE_PROMPT = (
        "Consider the following news article about {coin}:\n\n"
        "Title: {title}\n\nContent: {content}\n\n"
        "Is this article relevant to potential price impacts on the cryptocurrency? "
        "If yes, provide a concise summary focused on how it might impact trading or prices. "
        "If it's not relevant or only about price movements, respond with 'NOT RELEVANT'."
    )

    # Dictionary of top 100 popular tickers and their crypto names
    CRYPTO_DICT = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "USDT": "Tether",
        "BNB": "BNB",
        "SOL": "Solana",
        "USDC": "USDC",
        "XRP": "XRP",
        "STETH": "Lido Staked Ether",
        "DOGE": "Dogecoin",
        "TON": "Toncoin",
        "ADA": "Cardano",
        "TRX": "TRON",
        "AVAX": "Avalanche",
        "WSTETH": "Wrapped stETH",
        "SHIB": "Shiba Inu",
        "WBTC": "Wrapped Bitcoin",
        "WETH": "Binance-Peg WETH",
        "LINK": "Chainlink",
        "BCH": "Bitcoin Cash",
        "DOT": "Polkadot",
        "NEAR": "NEAR Protocol",
        "UNI": "Uniswap",
        "LEO": "LEO Token",
        "DAI": "Dai",
        "SUI": "Sui",
        "LTC": "Litecoin",
        "PEPE": "Pepe",
        "ICP": "Internet Computer",
        "WEETH": "Wrapped eETH",
        "TAO": "Bittensor",
        "FET": "Artificial Superintelligence Alliance",
        "APT": "Aptos",
        "KAS": "Kaspa",
        "POL": "POL (ex-MATIC)",
        "XLM": "Stellar",
        "ETC": "Ethereum Classic",
        "STX": "Stacks",
        "FDUSD": "First Digital USD",
        "IMX": "Immutable",
        "XMR": "Monero",
        "RENDER": "Render",
        "WIF": "dogwifhat",
        "USDE": "Ethena USDe",
        "OKB": "OKB",
        "AAVE": "Aave",
        "INJ": "Injective",
        "OP": "Optimism",
        "FIL": "Filecoin",
        "CRO": "Cronos",
        "ARB": "Arbitrum",
        "HBAR": "Hedera",
        "FTM": "Fantom",
        "MNT": "Mantle",
        "VET": "VeChain",
        "ATOM": "Cosmos Hub",
        "RUNE": "THORChain",
        "BONK": "Bonk",
        "GRT": "The Graph",
        "SEI": "Sei",
        "WBT": "WhiteBIT Coin",
        "FLOKI": "FLOKI",
        "AR": "Arweave",
        "THETA": "Theta Network",
        "RETH": "Rocket Pool ETH",
        "BGB": "Bitget Token",
        "MKR": "Maker",
        "HNT": "Helium",
        "METH": "Mantle Staked Ether",
        "SOLVBTC": "Solv Protocol SolvBTC",
        "PYTH": "Pyth Network",
        "TIA": "Celestia",
        "JUP": "Jupiter",
        "LDO": "Lido DAO",
        "MATIC": "Polygon",
        "ONDO": "Ondo",
        "ALGO": "Algorand",
        "GT": "Gate",
        "JASMY": "JasmyCoin",
        "QNT": "Quant",
        "OM": "MANTRA",
        "BEAM": "Beam",
        "POPCAT": "Popcat",
        "BSV": "Bitcoin SV",
        "KCS": "KuCoin",
        "EZETH": "Renzo Restaked ETH",
        "CORE": "Core",
        "BRETT": "Brett",
        "WLD": "Worldcoin",
        "GALA": "GALA",
        "BTT": "BitTorrent",
        "FLOW": "Flow",
        "NOT": "Notcoin",
        "STRK": "Starknet",
        "EETH": "ether.fi Staked ETH",
        "MSOL": "Marinade Staked SOL",
        "EIGEN": "Eigenlayer",
        "ORDI": "ORDI",
        "CFX": "Conflux",
        "W": "Wormhole",
        "MOR": "Morpheus AI",
    }
