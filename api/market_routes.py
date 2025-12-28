"""
Market data API routes
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """
    Get 24-hour ticker data for a symbol
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        
    Returns:
        Ticker data with price, volume, and 24h statistics
    """
    from infrastructure.external import mexc_client
    from infrastructure.external import redis_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Try to get from cache first
        cached_ticker = await redis_client.get_ticker_24hr(symbol)
        if cached_ticker:
            logger.info(f"[Cache HIT] Ticker data for {symbol}")
            return {
                "success": True,
                "source": "cache",
                "symbol": symbol,
                "data": cached_ticker,
                "timestamp": datetime.now().isoformat()
            }
        
        # Cache miss - get from MEXC API
        logger.info(f"[Cache MISS] Fetching ticker for {symbol} from MEXC")
        async with mexc_client:
            ticker = await mexc_client.get_ticker_24hr(symbol)
            
            # Store in cache
            await redis_client.set_ticker_24hr(symbol, ticker)
            
            logger.info(f"Ticker data fetched and cached for {symbol}")
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
    Get current price for a symbol
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        
    Returns:
        Current price data
    """
    from infrastructure.external import mexc_client
    from infrastructure.external import redis_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Try to get from cache first
        cached_price = await redis_client.get_cached_price()
        if cached_price:
            logger.info(f"[Cache HIT] Price for {symbol}")
            return {
                "success": True,
                "source": "cache",
                "symbol": symbol,
                "price": cached_price.get("price"),
                "volume": cached_price.get("volume"),
                "timestamp": datetime.now().isoformat()
            }
        
        # Cache miss - get from MEXC API
        logger.info(f"[Cache MISS] Fetching price for {symbol} from MEXC")
        async with mexc_client:
            price_data = await mexc_client.get_ticker_price(symbol)
            price = float(price_data.get("price", 0))
            
            # Store in cache
            await redis_client.set_cached_price(price, 0)
            
            logger.info(f"Price fetched and cached for {symbol}: {price}")
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
    Get order book (depth) for a symbol
    
    Args:
        symbol: Trading symbol
        limit: Number of orders to return (default: 100)
        
    Returns:
        Order book with bids and asks
    """
    from infrastructure.external import mexc_client
    from infrastructure.external import redis_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Try to get from cache first
        cached_orderbook = await redis_client.get_order_book(symbol)
        if cached_orderbook:
            logger.info(f"[Cache HIT] Order book for {symbol}")
            return {
                "success": True,
                "source": "cache",
                "symbol": symbol,
                "data": cached_orderbook,
                "timestamp": datetime.now().isoformat()
            }
        
        # Cache miss - get from MEXC API
        logger.info(f"[Cache MISS] Fetching order book for {symbol} from MEXC")
        async with mexc_client:
            orderbook = await mexc_client.get_orderbook(symbol, limit)
            
            # Store in cache
            await redis_client.set_order_book(symbol, orderbook)
            
            logger.info(f"Order book fetched and cached for {symbol}")
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
    Get recent trades for a symbol
    
    Args:
        symbol: Trading symbol
        limit: Number of trades to return (default: 500)
        
    Returns:
        List of recent trades
    """
    from infrastructure.external import mexc_client
    from infrastructure.external import redis_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Try to get from cache first
        cached_trades = await redis_client.get_recent_trades(symbol)
        if cached_trades:
            logger.info(f"[Cache HIT] Recent trades for {symbol}")
            return {
                "success": True,
                "source": "cache",
                "symbol": symbol,
                "data": cached_trades,
                "timestamp": datetime.now().isoformat()
            }
        
        # Cache miss - get from MEXC API
        logger.info(f"[Cache MISS] Fetching recent trades for {symbol} from MEXC")
        async with mexc_client:
            trades = await mexc_client.get_recent_trades(symbol, limit)
            
            # Store in cache
            await redis_client.set_recent_trades(symbol, trades)
            
            logger.info(f"Recent trades fetched and cached for {symbol}")
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
    from infrastructure.external import redis_client
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Try to get from cache first
        cache_key = f"{symbol}:{interval}"
        cached_klines = await redis_client.get_klines(cache_key)
        if cached_klines:
            logger.info(f"[Cache HIT] Klines for {cache_key}")
            return {
                "success": True,
                "source": "cache",
                "symbol": symbol,
                "interval": interval,
                "data": cached_klines,
                "timestamp": datetime.now().isoformat()
            }
        
        # Cache miss - get from MEXC API
        logger.info(f"[Cache MISS] Fetching klines for {cache_key} from MEXC")
        async with mexc_client:
            klines = await mexc_client.get_klines(symbol, interval, limit)
            
            # Store in cache
            await redis_client.set_klines(cache_key, klines)
            
            logger.info(f"Klines fetched and cached for {cache_key}")
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
