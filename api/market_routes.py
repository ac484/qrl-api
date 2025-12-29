"""
Market data API routes (aggregated).
Delegates to api.market.* modules to match README structure.
"""
from fastapi import APIRouter

from api.market.ticker import router as ticker_router, get_ticker
from api.market.price import router as price_router, get_price
from api.market.exchange_info import router as exchange_info_router, get_exchange_info
from api.market.orderbook import router as orderbook_router, get_orderbook
from api.market.book_ticker import router as book_ticker_router, get_book_ticker
from api.market.trades import router as trades_router, get_recent_trades
from api.market.agg_trades import router as agg_trades_router, get_agg_trades
from api.market.klines import router as klines_router, get_klines

router = APIRouter()
router.include_router(ticker_router)
router.include_router(price_router)
router.include_router(exchange_info_router)
router.include_router(orderbook_router)
router.include_router(book_ticker_router)
router.include_router(trades_router)
router.include_router(agg_trades_router)
router.include_router(klines_router)

__all__ = [
    "router",
    "get_ticker",
    "get_price",
    "get_exchange_info",
    "get_orderbook",
    "get_book_ticker",
    "get_recent_trades",
    "get_agg_trades",
    "get_klines",
]
