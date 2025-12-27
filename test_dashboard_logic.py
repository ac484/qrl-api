#!/usr/bin/env python3
"""
Test dashboard data source priority logic
Simulates the JavaScript logic to verify correct behavior
"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simulate_refresh_data(api_balances=None, redis_position=None, price=None):
    """
    Simulates the refreshData() JavaScript function
    
    Args:
        api_balances: Dict with 'qrlTotal' and 'usdtTotal' (from MEXC API)
        redis_position: Dict with 'qrl_balance' and 'usdt_balance' (from Redis)
        price: Current QRL price
    
    Returns:
        Dict with the balance that should be used for total value calculation
    """
    # PRIMARY: Use real-time API balance
    if api_balances and price:
        logger.info("✅ Using API balance (primary source)")
        return {
            'source': 'api',
            'qrl': api_balances['qrlTotal'],
            'usdt': api_balances['usdtTotal'],
            'total_value': (api_balances['qrlTotal'] * price) + api_balances['usdtTotal']
        }
    
    # FALLBACK: Use Redis position data if API fails
    elif redis_position and price and (redis_position.get('qrl_balance') or redis_position.get('usdt_balance')):
        logger.info("⚠️  Using Redis position (fallback - API failed)")
        qrl_bal = float(redis_position.get('qrl_balance', 0))
        usdt_bal = float(redis_position.get('usdt_balance', 0))
        return {
            'source': 'redis',
            'qrl': qrl_bal,
            'usdt': usdt_bal,
            'total_value': (qrl_bal * price) + usdt_bal
        }
    
    else:
        logger.error("❌ No data available")
        return None


def test_scenario(name, api_balances, redis_position, price, expected_source):
    """Test a specific scenario"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Scenario: {name}")
    logger.info(f"API balance: {api_balances}")
    logger.info(f"Redis position: {redis_position}")
    logger.info(f"Price: {price}")
    
    result = simulate_refresh_data(api_balances, redis_position, price)
    
    if result:
        logger.info(f"Result: {result}")
        if result['source'] == expected_source:
            logger.info(f"✅ PASS - Used {expected_source} as expected")
            return True
        else:
            logger.error(f"❌ FAIL - Expected {expected_source}, got {result['source']}")
            return False
    else:
        logger.error(f"❌ FAIL - No result returned")
        return False


def main():
    """Run all test scenarios"""
    logger.info("Testing Dashboard Data Source Priority Logic")
    logger.info("="*60)
    
    results = []
    
    # Test 1: Normal case - API works, Redis has stale data
    results.append(test_scenario(
        "User deposited 1000 QRL, but bot hasn't run",
        api_balances={'qrlTotal': 1000, 'usdtTotal': 500},
        redis_position={'qrl_balance': '0', 'usdt_balance': '500'},
        price=0.055,
        expected_source='api'
    ))
    
    # Test 2: API fails, use Redis fallback
    results.append(test_scenario(
        "API fails, Redis has data",
        api_balances=None,
        redis_position={'qrl_balance': '500', 'usdt_balance': '250'},
        price=0.055,
        expected_source='redis'
    ))
    
    # Test 3: Both API and Redis have data, API should win
    results.append(test_scenario(
        "Both sources available, API should be primary",
        api_balances={'qrlTotal': 1500, 'usdtTotal': 750},
        redis_position={'qrl_balance': '500', 'usdt_balance': '250'},
        price=0.055,
        expected_source='api'
    ))
    
    # Test 4: User withdrew USDT manually
    results.append(test_scenario(
        "User withdrew 200 USDT manually (not tracked by bot)",
        api_balances={'qrlTotal': 1000, 'usdtTotal': 300},
        redis_position={'qrl_balance': '1000', 'usdt_balance': '500'},
        price=0.055,
        expected_source='api'
    ))
    
    # Test 5: Bot bought QRL, API reflects real balance
    results.append(test_scenario(
        "Bot bought 500 QRL, user has total 1500 QRL",
        api_balances={'qrlTotal': 1500, 'usdtTotal': 250},
        redis_position={'qrl_balance': '500', 'usdt_balance': '250'},
        price=0.055,
        expected_source='api'
    ))
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("Test Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Total tests: {len(results)}")
    logger.info(f"Passed: {sum(results)}")
    logger.info(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        logger.info("\n✅ ALL TESTS PASSED")
        return 0
    else:
        logger.error("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
