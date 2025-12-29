"""
Account balance route.
"""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


@router.get("/balance")
async def get_account_balance():
    """
    Get account balance (real-time from MEXC API)
    """
    from infrastructure.external.mexc_client import mexc_client

    try:
        async with mexc_client:
            account_info = await mexc_client.get_account_info()
            price_data = (await mexc_client.get_ticker_price("QRLUSDT")) or {}
            qrl_price = float(price_data.get("price", 0))

            balances = account_info.get("balances", [])
            qrl_balance = {"asset": "QRL", "free": "0", "locked": "0"}
            usdt_balance = {"asset": "USDT", "free": "0", "locked": "0"}

            for balance in balances:
                if balance.get("asset") == "QRL":
                    qrl_balance = balance
                elif balance.get("asset") == "USDT":
                    usdt_balance = balance

            qrl_total = float(qrl_balance.get("free", 0)) + float(qrl_balance.get("locked", 0))
            usdt_total = float(usdt_balance.get("free", 0)) + float(usdt_balance.get("locked", 0))

            qrl_value_usdt = qrl_total * qrl_price
            qrl_free_value_usdt = float(qrl_balance.get("free", 0)) * qrl_price

            logger.info(
                f"Account balance fetched - QRL: {qrl_total:.2f}, USDT: {usdt_total:.2f}"
            )

            return {
                "success": True,
                "source": "api",
                "balances": {
                    "QRL": {
                        "free": qrl_balance.get("free"),
                        "locked": qrl_balance.get("locked"),
                        "total": qrl_total,
                        "price": qrl_price,
                        "value_usdt": qrl_value_usdt,
                        "value_usdt_free": qrl_free_value_usdt,
                    },
                    "USDT": {
                        "free": usdt_balance.get("free"),
                        "locked": usdt_balance.get("locked"),
                        "total": usdt_total,
                    },
                },
                "account_type": account_info.get("accountType"),
                "can_trade": account_info.get("canTrade"),
                "prices": {"QRLUSDT": qrl_price},
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"Failed to get account balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
