"""
Configuration module for QRL Trading Bot
Manages environment variables and application settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # Application settings
    PORT = int(os.getenv('PORT', '8080'))  # Cloud Run provides this automatically
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Redis settings (Cloud Redis - single URL format)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Trading settings
    TRADING_PAIR = os.getenv('TRADING_PAIR', 'QRL-USDT')
    MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '8'))
    
    # MEXC API settings (stored in Secret Manager in production)
    MEXC_API_KEY = os.getenv('MEXC_API_KEY', '')
    MEXC_API_SECRET = os.getenv('MEXC_API_SECRET', '')
    MEXC_SUBACCOUNT = os.getenv('MEXC_SUBACCOUNT', '')
    MEXC_BASE_URL = os.getenv('MEXC_BASE_URL', 'https://api.mexc.com')
    
    # Accumulation Strategy Settings (DCA - Dollar Cost Averaging)
    CORE_POSITION_PERCENT = float(os.getenv('CORE_POSITION_PERCENT', '70.0'))  # 核心倉位 70%
    SWING_POSITION_PERCENT = float(os.getenv('SWING_POSITION_PERCENT', '20.0'))  # 波段倉位 20%
    ACTIVE_POSITION_PERCENT = float(os.getenv('ACTIVE_POSITION_PERCENT', '10.0'))  # 機動倉位 10%
    
    # USDT Reserve Management
    MIN_USDT_RESERVE_PERCENT = float(os.getenv('MIN_USDT_RESERVE_PERCENT', '15.0'))  # 最低 15% USDT 儲備
    MAX_USDT_RESERVE_PERCENT = float(os.getenv('MAX_USDT_RESERVE_PERCENT', '25.0'))  # 最高 25% USDT 儲備
    USDT_USAGE_PERCENT = float(os.getenv('USDT_USAGE_PERCENT', '60.0'))  # 每次交易使用 60% 可用 USDT
    
    # Price and Strategy Parameters
    LONG_MA_PERIOD = int(os.getenv('LONG_MA_PERIOD', '20'))  # For price dip detection
    DCA_DIP_THRESHOLD = float(os.getenv('DCA_DIP_THRESHOLD', '0.98'))  # Buy when price < MA * 0.98
    DCA_INTERVAL_HOURS = int(os.getenv('DCA_INTERVAL_HOURS', '24'))  # Periodic buy interval
    
    # Selling thresholds (only sell active/swing positions, never core)
    ACTIVE_SELL_THRESHOLD = float(os.getenv('ACTIVE_SELL_THRESHOLD', '1.05'))  # 機動倉位: +5% 賣出
    SWING_SELL_THRESHOLD = float(os.getenv('SWING_SELL_THRESHOLD', '1.15'))  # 波段倉位: +15% 賣出
    ACTIVE_SELL_PERCENT = float(os.getenv('ACTIVE_SELL_PERCENT', '50.0'))  # 機動倉位賣出比例 50%
    SWING_SELL_PERCENT = float(os.getenv('SWING_SELL_PERCENT', '30.0'))  # 波段倉位賣出比例 30%
    
    # Buy back thresholds
    BUYBACK_DROP_PERCENT = float(os.getenv('BUYBACK_DROP_PERCENT', '5.0'))  # 回調 5% 買回
    
    # Risk management
    MAX_DAILY_LOSS_PERCENT = float(os.getenv('MAX_DAILY_LOSS_PERCENT', '3.0'))
    MIN_USDT_FOR_TRADE = float(os.getenv('MIN_USDT_FOR_TRADE', '10.0'))
    
    # Cost protection
    ALLOW_BUY_ABOVE_COST = os.getenv('ALLOW_BUY_ABOVE_COST', 'False').lower() == 'true'  # 禁止高於成本買入
    MIN_SELL_PROFIT_PERCENT = float(os.getenv('MIN_SELL_PROFIT_PERCENT', '3.0'))  # 最低賣出利潤 3%


# Create a singleton config instance
config = Config()
