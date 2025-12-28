"""
Configuration management for QRL Trading API
Supports environment variables and defaults
"""
import os
from typing import Optional


class Config:
    """Application configuration"""
    
    # Flask Configuration (hardcoded for production)
    FLASK_ENV: str = "production"
    DEBUG: bool = False
    PORT: int = int(os.getenv("PORT", "8080"))  # Keep as env var for Cloud Run
    HOST: str = "0.0.0.0"
    
    # Redis Configuration
    # Support REDIS_URL for Redis Cloud (e.g., redis://user:pass@host:port/db)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Fallback to individual parameters if REDIS_URL is not set
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    REDIS_SOCKET_TIMEOUT: int = 5
    
    # MEXC API Configuration
    MEXC_API_KEY: Optional[str] = os.getenv("MEXC_API_KEY")
    MEXC_SECRET_KEY: Optional[str] = os.getenv("MEXC_SECRET_KEY")
    MEXC_BASE_URL: str = os.getenv("MEXC_BASE_URL", "https://api.mexc.com")
    MEXC_WS_URL: str = os.getenv("MEXC_WS_URL", "wss://wbs.mexc.com/ws")
    MEXC_TIMEOUT: int = int(os.getenv("MEXC_TIMEOUT", "10"))
    
    # Sub-Account Configuration
    # MEXC v3 API supports two distinct sub-account systems:
    # 1. SPOT API: For regular users (uses numeric subAccountId)
    # 2. BROKER API: For broker/institutional accounts (uses string subAccount name)
    SUB_ACCOUNT_MODE: str = os.getenv("SUB_ACCOUNT_MODE", "SPOT")  # SPOT or BROKER
    
    # Spot API sub-account (regular users) - uses numeric ID
    SUB_ACCOUNT_ID: Optional[str] = os.getenv("SUB_ACCOUNT_ID")
    
    # Broker API sub-account (broker users) - uses string name
    SUB_ACCOUNT_NAME: Optional[str] = os.getenv("SUB_ACCOUNT_NAME")
    
    @property
    def is_broker_mode(self) -> bool:
        """
        Check if operating in BROKER mode
        
        Returns:
            True if in BROKER mode, False if in SPOT mode
        """
        return self.SUB_ACCOUNT_MODE.upper() == "BROKER"
    
    @property
    def active_sub_account_identifier(self) -> Optional[str]:
        """
        Return the active sub-account identifier based on current mode
        
        Returns:
            SUB_ACCOUNT_NAME for BROKER mode, SUB_ACCOUNT_ID for SPOT mode
        """
        return self.SUB_ACCOUNT_NAME if self.is_broker_mode else self.SUB_ACCOUNT_ID
    
    # Trading Configuration (hardcoded - only QRL/USDT trading)
    TRADING_SYMBOL: str = "QRLUSDT"  # MEXC trading symbol format
    
    # Strategy Parameters
    MA_SHORT_PERIOD: int = int(os.getenv("MA_SHORT_PERIOD", "7"))
    MA_LONG_PERIOD: int = int(os.getenv("MA_LONG_PERIOD", "25"))
    RSI_PERIOD: int = int(os.getenv("RSI_PERIOD", "14"))
    RSI_OVERSOLD: float = float(os.getenv("RSI_OVERSOLD", "30"))
    RSI_OVERBOUGHT: float = float(os.getenv("RSI_OVERBOUGHT", "70"))
    
    # Risk Control
    MAX_DAILY_TRADES: int = int(os.getenv("MAX_DAILY_TRADES", "5"))
    MIN_TRADE_INTERVAL: int = int(os.getenv("MIN_TRADE_INTERVAL", "300"))  # seconds
    STOP_LOSS_PCT: float = float(os.getenv("STOP_LOSS_PCT", "0.03"))  # 3%
    TAKE_PROFIT_PCT: float = float(os.getenv("TAKE_PROFIT_PCT", "0.05"))  # 5%
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "0.3"))  # 30% of available
    
    # Position Management
    CORE_POSITION_PCT: float = float(os.getenv("CORE_POSITION_PCT", "0.70"))  # 70% core
    USDT_RESERVE_PCT: float = float(os.getenv("USDT_RESERVE_PCT", "0.20"))  # 20% USDT reserve
    
    # Redis Cache TTL Configuration (hardcoded in seconds)
    CACHE_TTL_PRICE: int = 30  # 30 seconds for price
    CACHE_TTL_TICKER: int = 60  # 1 minute for ticker
    CACHE_TTL_ORDER_BOOK: int = 10  # 10 seconds for order book
    CACHE_TTL_TRADES: int = 60  # 1 minute for recent trades
    CACHE_TTL_KLINES: int = 300  # 5 minutes for klines
    CACHE_TTL_ACCOUNT: int = 120  # 2 minutes for account data
    CACHE_TTL_ORDERS: int = 30  # 30 seconds for orders
    
    # Logging (hardcoded for production)
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json format for Cloud Logging
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = []
        
        # API keys are optional for testing but recommended for production
        if cls.FLASK_ENV == "production":
            if not cls.MEXC_API_KEY:
                required_fields.append("MEXC_API_KEY")
            if not cls.MEXC_SECRET_KEY:
                required_fields.append("MEXC_SECRET_KEY")
        
        if required_fields:
            raise ValueError(f"Missing required configuration: {', '.join(required_fields)}")
        
        return True
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary (excluding sensitive data)"""
        return {
            "flask_env": cls.FLASK_ENV,
            "debug": cls.DEBUG,
            "port": cls.PORT,
            "redis_host": cls.REDIS_HOST,
            "redis_port": cls.REDIS_PORT,
            "mexc_base_url": cls.MEXC_BASE_URL,
            "trading_symbol": cls.TRADING_SYMBOL,
            "ma_short_period": cls.MA_SHORT_PERIOD,
            "ma_long_period": cls.MA_LONG_PERIOD,
            "rsi_period": cls.RSI_PERIOD,
            "max_daily_trades": cls.MAX_DAILY_TRADES,
            "core_position_pct": cls.CORE_POSITION_PCT,
            "usdt_reserve_pct": cls.USDT_RESERVE_PCT,
            "sub_account_configured": bool(cls.SUB_ACCOUNT_ID or cls.SUB_ACCOUNT_NAME),
            "sub_account_mode": cls.SUB_ACCOUNT_MODE,
        }


# Singleton instance
config = Config()
