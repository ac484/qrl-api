"""Tests for Order entity with value objects integration."""


import pytest

from src.app.domain.models.order import VALUE_OBJECTS_AVAILABLE, Order

if VALUE_OBJECTS_AVAILABLE:
    from src.app.domain.models.order import OrderWithValueObjects
    from src.app.domain.value_objects import (
        OrderSide,
        OrderStatus,
        Price,
        Quantity,
        Symbol,
    )


class TestOrderLegacy:
    """Tests for legacy Order class with primitive types."""

    def test_create_order_with_primitives(self):
        """Test creating order with primitive types."""
        order = Order(
            symbol="QRLUSDT",
            side="BUY",
            quantity=10.0,
            price=100.5,
            order_id="12345",
            status="NEW",
        )

        assert order.symbol == "QRLUSDT"
        assert order.side == "BUY"
        assert order.quantity == 10.0
        assert order.price == 100.5
        assert order.order_id == "12345"
        assert order.status == "NEW"

    def test_create_market_order(self):
        """Test creating market order (no price)."""
        order = Order(
            symbol="QRLUSDT",
            side="SELL",
            quantity=5.0,
            order_id="67890",
        )

        assert order.price is None
        assert order.order_id == "67890"


@pytest.mark.skipif(not VALUE_OBJECTS_AVAILABLE, reason="Value objects not available")
class TestOrderWithValueObjects:
    """Tests for enhanced Order class with value objects."""

    def test_create_order_with_value_objects(self):
        """Test creating order with value objects."""
        order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
            order_id="12345",
            status=OrderStatus.new(),
        )

        assert order.symbol.value == "QRLUSDT"
        assert order.side.is_buy()
        assert float(order.quantity) == 10.0
        assert float(order.price) == 100.5
        assert order.order_id == "12345"
        assert order.status.is_new()

    def test_create_order_from_primitives(self):
        """Test factory method to create order from primitives."""
        order = OrderWithValueObjects.from_primitives(
            symbol="QRLUSDT",
            side="BUY",
            quantity=10.0,
            price=100.5,
            order_id="12345",
            status="NEW",
        )

        assert order.symbol.value == "QRLUSDT"
        assert order.side.is_buy()
        assert float(order.quantity) == 10.0
        assert float(order.price) == 100.5
        assert order.status.is_new()

    def test_order_to_primitives(self):
        """Test converting order to primitive dictionary."""
        order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
            order_id="12345",
            status=OrderStatus.new(),
        )

        primitives = order.to_primitives()

        assert primitives["symbol"] == "QRLUSDT"
        assert primitives["side"] == "BUY"
        assert primitives["quantity"] == 10.0
        assert primitives["price"] == 100.5
        assert primitives["order_id"] == "12345"
        assert primitives["status"] == "NEW"

    def test_market_order_detection(self):
        """Test market order detection."""
        market_order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            order_id="12345",
        )

        limit_order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
            order_id="67890",
        )

        assert market_order.is_market_order()
        assert not market_order.is_limit_order()

        assert not limit_order.is_market_order()
        assert limit_order.is_limit_order()

    def test_order_side_detection(self):
        """Test order side detection methods."""
        buy_order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            order_id="12345",
        )

        sell_order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.sell(),
            quantity=Quantity.from_float(10.0),
            order_id="67890",
        )

        assert buy_order.is_buy()
        assert not buy_order.is_sell()

        assert sell_order.is_sell()
        assert not sell_order.is_buy()

    def test_order_status_detection(self):
        """Test order status detection methods."""
        new_order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            order_id="12345",
            status=OrderStatus.new(),
        )

        filled_order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            order_id="67890",
            status=OrderStatus.filled(),
        )

        assert new_order.is_active()
        assert not new_order.is_final()
        assert new_order.can_cancel()

        assert not filled_order.is_active()
        assert filled_order.is_final()
        assert not filled_order.can_cancel()

    def test_order_validation_via_value_objects(self):
        """Test that value objects enforce validation."""
        # Invalid symbol should raise error
        with pytest.raises(ValueError):
            OrderWithValueObjects(
                symbol=Symbol(""),  # Empty symbol
                side=OrderSide.buy(),
                quantity=Quantity.from_float(10.0),
                order_id="12345",
            )

        # Negative quantity should raise error
        with pytest.raises(ValueError):
            OrderWithValueObjects(
                symbol=Symbol("QRLUSDT"),
                side=OrderSide.buy(),
                quantity=Quantity.from_float(-10.0),  # Negative
                order_id="12345",
            )

        # Negative price should raise error
        with pytest.raises(ValueError):
            OrderWithValueObjects(
                symbol=Symbol("QRLUSDT"),
                side=OrderSide.buy(),
                quantity=Quantity.from_float(10.0),
                price=Price.from_float(-100.5, "USDT"),  # Negative
                order_id="12345",
            )

    def test_order_immutability_of_value_objects(self):
        """Test that value objects within order are immutable."""
        order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
            order_id="12345",
        )

        # Value objects are immutable
        with pytest.raises(Exception):  # FrozenInstanceError
            order.symbol.value = "BTCUSDT"

        with pytest.raises(Exception):
            order.price.value = 200.0

    def test_roundtrip_conversion(self):
        """Test that converting to primitives and back preserves values."""
        original = OrderWithValueObjects.from_primitives(
            symbol="QRLUSDT",
            side="BUY",
            quantity=10.0,
            price=100.5,
            order_id="12345",
            status="NEW",
        )

        # Convert to primitives
        primitives = original.to_primitives()

        # Convert back to value objects
        roundtrip = OrderWithValueObjects.from_primitives(**primitives)

        # Values should match
        assert roundtrip.symbol.value == original.symbol.value
        assert roundtrip.side.value == original.side.value
        assert roundtrip.quantity.value == original.quantity.value
        assert roundtrip.price.value == original.price.value
        assert roundtrip.order_id == original.order_id
        assert roundtrip.status.value == original.status.value


@pytest.mark.skipif(not VALUE_OBJECTS_AVAILABLE, reason="Value objects not available")
class TestOrderMigrationScenarios:
    """Tests for migration scenarios between legacy and value object orders."""

    def test_interoperability_legacy_to_value_objects(self):
        """Test converting legacy order data to value object order."""
        # Legacy order data (from API, database, etc.)
        legacy_data = {
            "symbol": "QRLUSDT",
            "side": "BUY",
            "quantity": 10.0,
            "price": 100.5,
            "order_id": "12345",
            "status": "NEW",
        }

        # Convert to value object order
        vo_order = OrderWithValueObjects.from_primitives(**legacy_data)

        # Verify conversion
        assert vo_order.symbol.value == legacy_data["symbol"]
        assert str(vo_order.side) == legacy_data["side"]
        assert float(vo_order.quantity) == legacy_data["quantity"]
        assert float(vo_order.price) == legacy_data["price"]

    def test_interoperability_value_objects_to_legacy(self):
        """Test converting value object order to legacy format."""
        # Value object order
        vo_order = OrderWithValueObjects(
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
            order_id="12345",
            status=OrderStatus.new(),
        )

        # Convert to primitives for legacy systems
        legacy_data = vo_order.to_primitives()

        # Create legacy order
        legacy_order = Order(**legacy_data)

        # Verify conversion
        assert legacy_order.symbol == "QRLUSDT"
        assert legacy_order.side == "BUY"
        assert legacy_order.quantity == 10.0
        assert legacy_order.price == 100.5
