#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Dict, List, TypedDict, Optional
import os
from dotenv import load_dotenv
from utils.logger import logger

class CryptoInfo(TypedDict):
    id: str
    symbol: str
    name: str

class MarketAnalysisConfig(TypedDict):
    correlation_sensitivity: float
    volatility_threshold: float
    volume_significance: int
    historical_periods: List[int]

class TweetConstraints(TypedDict):
    MIN_LENGTH: int
    MAX_LENGTH: int
    HARD_STOP_LENGTH: int

class CoinGeckoParams(TypedDict):
    vs_currency: str
    ids: str
    order: str
    per_page: int
    page: int
    sparkline: bool
    price_change_percentage: str

@dataclass
class Config:
    def __init__(self) -> None:
        # Get the absolute path to the .env file
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        logger.logger.info(f"Loading .env from: {env_path}")

        # Load environment variables
        load_dotenv(env_path)
        logger.logger.info("Environment variables loaded")
        
        # Debug loaded variables
        logger.logger.info(f"CHROME_DRIVER_PATH: {os.getenv('CHROME_DRIVER_PATH')}")
        logger.logger.info(f"CLAUDE_API_KEY Present: {bool(os.getenv('CLAUDE_API_KEY'))}")
        
        # Claude API Configuration
        self.CLAUDE_API_KEY: str = os.getenv('CLAUDE_API_KEY', '')
        self.CLAUDE_MODEL: str = 'claude-3-5-sonnet-20241022'  # Updated to Sonnet
        
        # Twitter Configuration
        self.TWITTER_USERNAME: str = os.getenv('TWITTER_USERNAME', '')
        self.TWITTER_PASSWORD: str = os.getenv('TWITTER_PASSWORD', '')
        self.CHROME_DRIVER_PATH: str = os.getenv('CHROME_DRIVER_PATH', '/usr/local/bin/chromedriver')
        
        # Analysis Configuration
        self.CORRELATION_INTERVAL: int = 5  # minutes (for testing)
        self.MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
        
        # ETH/BTC Market Analysis Parameters
        self.MARKET_ANALYSIS_CONFIG: MarketAnalysisConfig = {
            'correlation_sensitivity': 0.7,
            'volatility_threshold': 2.0,
            'volume_significance': 100000,
            'historical_periods': [1, 4, 24]
        }
        
        # Tweet Length Constraints
        self.TWEET_CONSTRAINTS: TweetConstraints = {
            'MIN_LENGTH': 220,
            'MAX_LENGTH': 270,
            'HARD_STOP_LENGTH': 280
        }
        
        # API Endpoints
        self.COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
        
        # CoinGecko API Request Settings
        self.COINGECKO_PARAMS: CoinGeckoParams = {
            "vs_currency": "usd",
            "ids": "bitcoin,ethereum",
            "order": "market_cap_desc",
            "per_page": 2,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "1h,24h,7d"
        }
        
        # Tracked Cryptocurrencies
        self.TRACKED_CRYPTO: Dict[str, CryptoInfo] = {
            'bitcoin': {
                'id': 'bitcoin',
                'symbol': 'btc',
                'name': 'Bitcoin'
            },
            'ethereum': {
                'id': 'ethereum', 
                'symbol': 'eth',
                'name': 'Ethereum'
            }
        }
        
        # Enhanced Claude Analysis Prompt Template for Sonnet
        self.CLAUDE_ANALYSIS_PROMPT: str = """Analyze ETH/BTC Market Dynamics:

Current Market Data:
Bitcoin:
- Price: ${btc_price:,.2f}
- 24h Change: {btc_change:.2f}%
- Volume: ${btc_volume:,.0f}

Ethereum:
- Price: ${eth_price:,.2f}
- 24h Change: {eth_change:.2f}%
- Volume: ${eth_volume:,.0f}

Please provide a concise but detailed market analysis:
1. Short-term Movement: 
   - Price action in last few minutes
   - Volume profile significance
   - Immediate support/resistance levels

2. Market Microstructure:
   - Order flow analysis
   - Volume weighted price trends
   - Market depth indicators

3. Cross-Pair Dynamics:
   - ETH/BTC correlation changes
   - Relative strength shifts
   - Market maker activity signals

Focus on actionable micro-trends and real-time market behavior. Identify minimal but significant price movements.
Keep the analysis technical but concise, emphasizing key shifts in market dynamics."""
        
        # Validation
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate required configuration settings"""
        required_settings: List[tuple[str, str]] = [
            ('TWITTER_USERNAME', self.TWITTER_USERNAME),
            ('TWITTER_PASSWORD', self.TWITTER_PASSWORD),
            ('CHROME_DRIVER_PATH', self.CHROME_DRIVER_PATH),
            ('CLAUDE_API_KEY', self.CLAUDE_API_KEY)
        ]
        
        missing_settings: List[str] = []
        for setting_name, setting_value in required_settings:
            if not setting_value or setting_value.strip() == '':
                missing_settings.append(setting_name)
        
        if missing_settings:
            error_msg = f"Missing required configuration: {', '.join(missing_settings)}"
            logger.log_error("Config", error_msg)
            raise ValueError(error_msg)

    def get_coingecko_markets_url(self) -> str:
        """Get CoinGecko markets API endpoint"""
        return f"{self.COINGECKO_BASE_URL}/coins/markets"

    def get_coingecko_params(self, **kwargs) -> Dict:
        """Get CoinGecko API parameters with optional overrides"""
        params = self.COINGECKO_PARAMS.copy()
        params.update(kwargs)
        return params

    @property
    def twitter_selectors(self) -> Dict[str, str]:
        """CSS Selectors for Twitter elements"""
        return {
            'username_input': 'input[autocomplete="username"]',
            'password_input': 'input[type="password"]',
            'login_button': '[data-testid="LoginForm_Login_Button"]',
            'tweet_input': '[data-testid="tweetTextarea_0"]',
            'tweet_button': '[data-testid="tweetButton"]'
        }

# Create singleton instance
config = Config()
