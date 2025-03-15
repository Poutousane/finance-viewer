# assets.py
"""
Définition des actifs financiers par catégories pour l'application Finance Viewer.
"""

# Définition des catégories d'actions par secteur
stock_categories = {
    "Tech": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Google": "GOOGL",
        "Amazon": "AMZN",
        "Tesla": "TSLA",
        "Meta": "META",
        "NVIDIA": "NVDA",
        "Adobe": "ADBE",
        "Intel": "INTC",
        "IBM": "IBM",
        "Cisco": "CSCO",
        "Oracle": "ORCL",
        "Salesforce": "CRM",
        "AMD": "AMD",
        "PayPal": "PYPL",
    },
    "Banques & Finance": {
        "JPMorgan Chase": "JPM",
        "Bank of America": "BAC",
        "Wells Fargo": "WFC",
        "Goldman Sachs": "GS",
        "Morgan Stanley": "MS",
        "Visa": "V",
        "Mastercard": "MA",
        "American Express": "AXP",
    },
    "Consommation": {
        "Walmart": "WMT",
        "Coca-Cola": "KO",
        "PepsiCo": "PEP",
        "McDonald's": "MCD",
        "Nike": "NKE",
        "Disney": "DIS",
        "Home Depot": "HD",
        "Starbucks": "SBUX",
        "Procter & Gamble": "PG",
        "Netflix": "NFLX",
    },
    "Santé & Pharmacie": {
        "Johnson & Johnson": "JNJ",
        "Pfizer": "PFE",
        "Merck": "MRK",
        "UnitedHealth": "UNH",
        "Abbott Labs": "ABT",
        "Eli Lilly": "LLY",
        "Amgen": "AMGN",
        "Bristol-Myers Squibb": "BMY",
    },
    "Énergie": {
        "Exxon Mobil": "XOM",
        "Chevron": "CVX",
        "ConocoPhillips": "COP",
        "Shell": "SHEL",
        "BP": "BP",
    },
    "Automobile": {
        "Ford": "F",
        "General Motors": "GM",
        "Toyota": "TM",
        "Honda": "HMC",
        "Volkswagen": "VWAGY",
    },
    "Télécommunications": {
        "AT&T": "T",
        "Verizon": "VZ",
        "T-Mobile": "TMUS",
        "Comcast": "CMCSA"
    }
}

# Dictionnaire plat des actions
stock_assets = {}
for category, assets in stock_categories.items():
    for name, ticker in assets.items():
        stock_assets[name] = ticker

# Listes des autres types d'actifs
crypto_assets = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Binance Coin": "BNB-USD",
    "Solana": "SOL-USD",
    "XRP": "XRP-USD",
    "Cardano": "ADA-USD",
    "Dogecoin": "DOGE-USD",
    "Polkadot": "DOT-USD"
}

currency_assets = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "USD/CAD": "USDCAD=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CHF": "USDCHF=X",
    "NZD/USD": "NZDUSD=X",
    "EUR/GBP": "EURGBP=X"
}

resource_assets = {
    "Or": "GC=F",
    "Argent": "SI=F",
    "Pétrole brut": "CL=F",
    "Gaz naturel": "NG=F",
    "Cuivre": "HG=F",
    "Blé": "ZW=F",
    "Maïs": "ZC=F"
}

# Indices organisés par pays
index_categories = {
    "États-Unis": {
        "S&P 500": "^GSPC",
        "NASDAQ Composite": "^IXIC",
        "Dow Jones": "^DJI",
        "Russell 2000": "^RUT"
    },
    "France": {
        "CAC 40": "^FCHI"
    },
    "Allemagne": {
        "DAX": "^GDAXI"
    },
    "Royaume-Uni": {
        "FTSE 100": "^FTSE"
    },
    "Japon": {
        "Nikkei 225": "^N225"
    },
    "Hong Kong": {
        "Hang Seng": "^HSI"
    },
    "Australie": {
        "ASX 200": "^AXJO"
    },
    "Espagne": {
        "IBEX 35": "^IBEX"
    },
    "Italie": {
        "FTSE MIB": "FTSEMIB.MI"
    },
    "Corée du Sud": {
        "KOSPI": "^KS11"
    },
    "Canada": {
        "TSX Composite": "^GSPTSE"
    }
}

# Conversion à un dictionnaire plat pour les indices
index_assets = {}
for country, indices in index_categories.items():
    for name, ticker in indices.items():
        index_assets[name] = ticker
