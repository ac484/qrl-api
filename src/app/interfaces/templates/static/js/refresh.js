import { loadBalances } from './api/account/get_balance.js';
import { loadOrders } from './api/account/list_orders.js';
import { loadTrades } from './api/account/list_trades.js';
import { loadPrice } from './api/market/get_price.js';
import { loadBookTicker } from './api/market/get_book_ticker.js';
import { loadExchangeInfo } from './api/market/get_exchange_info.js';
import { loadDepth } from './api/market/get_orderbook.js';
import { loadAggTrades } from './api/market/get_trades.js';
import { loadKlines } from './api/market/get_klines.js';

export async function refreshAll() {
    await Promise.all([
        loadBalances(),
        loadPrice(),
        loadBookTicker(),
        loadExchangeInfo(),
        loadDepth(),
        loadAggTrades(),
        loadKlines(),
        loadOrders(),
        loadTrades(),
    ]);
}
