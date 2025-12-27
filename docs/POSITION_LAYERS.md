# Position Layers Feature

## Overview

The Position Layers feature provides sophisticated position management by dividing QRL holdings into three strategic layers:

1. **Core Position (核心倉位)**: Long-term holdings that are never traded
2. **Swing Position (波段倉位)**: Medium-term trading position for weekly strategies
3. **Active Position (機動倉位)**: Short-term trading position for daily operations

## Architecture

### Backend Implementation

#### Data Model
```python
class PositionLayers:
    core_qrl: float      # Core position (never trade)
    swing_qrl: float     # Swing position (weekly trading)
    active_qrl: float    # Active position (daily trading)
    total_qrl: float     # Total position (sum of all layers)
    core_percent: float  # Core position percentage
    last_adjust: str     # Last adjustment timestamp (ISO format)
```

#### Redis Storage
Position layers are stored in Redis with the following key structure:
- Key: `bot:QRLUSDT:position:layers`
- Data Type: Hash
- Fields: `core_qrl`, `swing_qrl`, `active_qrl`, `total_qrl`, `core_percent`, `last_adjust`

#### API Endpoints

**GET /status**
```json
{
  "bot_status": "running",
  "position": { ... },
  "position_layers": {
    "core_qrl": "7000.0",
    "swing_qrl": "2000.0",
    "active_qrl": "1000.0",
    "total_qrl": "10000.0",
    "core_percent": "0.70",
    "last_adjust": "2024-12-27T19:20:00.000Z"
  },
  "latest_price": { ... },
  "daily_trades": 3,
  "timestamp": "2024-12-27T19:20:00.000Z"
}
```

### Frontend Implementation

The dashboard displays position layers in a dedicated section with real-time updates:

```html
<div class="balance-details">
    <h2>🎯 倉位分層</h2>
    <div class="balance-row">
        <span class="balance-label">核心倉位 (Core)</span>
        <span class="balance-value" id="core-position">7000.0000 QRL</span>
    </div>
    <!-- Additional layers... -->
</div>
```

## Usage

### Setting Position Layers

```python
from redis_client import redis_client

# Set position layers
await redis_client.set_position_layers(
    core_qrl=7000.0,    # 70% core position
    swing_qrl=2000.0,   # 20% swing trading
    active_qrl=1000.0   # 10% active trading
)
```

### Getting Position Layers

```python
# Get current position layers
layers = await redis_client.get_position_layers()

print(f"Core: {layers['core_qrl']} QRL")
print(f"Swing: {layers['swing_qrl']} QRL")
print(f"Active: {layers['active_qrl']} QRL")
print(f"Total: {layers['total_qrl']} QRL")
print(f"Core %: {float(layers['core_percent']) * 100:.2f}%")
```

### Trading Integration

The bot automatically respects position layers when executing SELL orders:

```python
# In bot.py execution phase
layers = await redis_client.get_position_layers()
total_qrl = float(layers.get("total_qrl", qrl_balance))
core_qrl = float(layers.get("core_qrl", total_qrl * 0.70))
tradeable_qrl = total_qrl - core_qrl  # Only trade non-core position

qrl_to_sell = tradeable_qrl * MAX_POSITION_SIZE
```

## Risk Management

### Protection Mechanisms

1. **Core Position Protection**: The core position is never included in sell orders
2. **Tradeable Balance Calculation**: Only non-core positions are considered for trading
3. **Risk Control Validation**: Pre-trade checks ensure adequate tradeable balance

### Configuration

Default position allocation (configurable via environment variables):

```env
CORE_POSITION_PCT=0.70  # 70% core position
MAX_POSITION_SIZE=0.30  # Trade up to 30% of tradeable position per order
```

## Benefits

1. **Capital Preservation**: Core position ensures long-term holding regardless of market conditions
2. **Flexible Trading**: Swing and active layers enable different trading strategies
3. **Risk Management**: Clear separation of long-term and trading capital
4. **Portfolio Visibility**: Real-time dashboard view of position allocation
5. **Strategic Allocation**: Different layers for different time horizons and strategies

## Testing

Run the position layers test suite:

```bash
python test_position_layers.py
```

This will test:
- Setting and getting position layers
- Value validation and consistency
- API endpoint integration
- Redis connection pool functionality

## Future Enhancements

1. **Dynamic Rebalancing**: Automatic adjustment of layers based on market conditions
2. **Performance Tracking**: Layer-specific P&L tracking
3. **Historical Analysis**: Layer allocation history and performance metrics
4. **Alert System**: Notifications when layer allocations deviate from targets
5. **Layer Strategy Configuration**: Different trading strategies per layer

## See Also

- [Redis Client Documentation](../redis_client.py)
- [Trading Bot Documentation](../bot.py)
- [API Documentation](../main.py)
