"""
Market data API routes
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """
    Get 24-hour ticker data for a symbol (Direct MEXC API)
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        
    Returns:
        Ticker data with price, volume, and 24h statistics
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Always get fresh data from MEXC API (no caching)
        logger.info(f"Fetching ticker for {symbol} from MEXC API")
        async with mexc_client:
            ticker = await mexc_client.get_ticker_24hr(symbol)
            
            logger.info(f"Ticker data fetched for {symbol}")
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": ticker,
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """
    Get current price for a symbol (Direct MEXC API)
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        
    Returns:
        Current price data
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Always get fresh data from MEXC API (no caching)
        logger.info(f"Fetching price for {symbol} from MEXC API")
        async with mexc_client:
            price_data = await mexc_client.get_ticker_price(symbol)
            price = float(price_data.get("price", 0))
            
            logger.info(f"Price fetched for {symbol}: {price}")
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "price": str(price),
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 100):
    """
    Get order book (depth) for a symbol (Direct MEXC API)
    
    Args:
        symbol: Trading symbol
        limit: Number of orders to return (default: 100)
        
    Returns:
        Order book with bids and asks
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Always get fresh data from MEXC API (no caching)
        logger.info(f"Fetching order book for {symbol} from MEXC API")
        async with mexc_client:
            orderbook = await mexc_client.get_orderbook(symbol, limit)
            
            logger.info(f"Order book fetched for {symbol}")
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": orderbook,
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get order book for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/{symbol}")
async def get_recent_trades(symbol: str, limit: int = 500):
    """
    Get recent trades for a symbol (Direct MEXC API)
    
    Args:
        symbol: Trading symbol
        limit: Number of trades to return (default: 500)
        
    Returns:
        List of recent trades
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Always get fresh data from MEXC API (no caching)
        logger.info(f"Fetching recent trades for {symbol} from MEXC API")
        async with mexc_client:
            trades = await mexc_client.get_recent_trades(symbol, limit)
            
            logger.info(f"Recent trades fetched for {symbol}")
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": trades,
                "count": len(trades),
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get recent trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = "1m",
    limit: int = 500
):
    """
    Get candlestick/kline data for a symbol
    
    Args:
        symbol: Trading symbol
        interval: Time interval (1m, 5m, 15m, 1h, 1d, etc.)
        limit: Number of candles to return (default: 500)
        
    Returns:
        List of candlestick data
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Always get fresh data from MEXC API (no caching)
        logger.info(f"Fetching klines for {symbol}:{interval} from MEXC API")
        async with mexc_client:
            klines = await mexc_client.get_klines(symbol, interval, limit)
            
            logger.info(f"Klines fetched for {symbol}:{interval}")
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "interval": interval,
                "data": klines,
                "count": len(klines),
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get klines for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
