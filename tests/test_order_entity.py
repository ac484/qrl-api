"""Tests for Order entity with pure DDD value objects."""

import pytest
from datetime import datetime
from decimal import Decimal
from src.app.domain.models.order import Order
from src.app.domain.value_objects import (
    Symbol,
    Price,
    Quantity,
    OrderSide,
    OrderStatus,
    OrderStatusEnum,
)


class TestOrderCreation:
    """Tests for creating Order entities."""

    def test_create_order_with_value_objects(self):
        """Test creating order with value objects."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
        )

        assert order.order_id == "12345"
        assert order.symbol.value == "QRLUSDT"
        assert order.side.is_buy()
        assert float(order.quantity) == 10.0
        assert float(order.price) == 100.5
        assert order.status.is_new()

    def test_create_market_order(self):
        """Test creating market order (no price)."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.sell(),
            quantity=Quantity.from_float(5.0),
        )

        assert order.price is None
        assert order.is_market_order()
        assert not order.is_limit_order()

    def test_create_order_requires_order_id(self):
        """Test that order_id is required (entity identity)."""
        with pytest.raises(ValueError, match="Order must have an order_id"):
            Order(
                order_id="",  # Empty order_id
                symbol=Symbol("QRLUSDT"),
                side=OrderSide.buy(),
                quantity=Quantity.from_float(10.0),
            )

    def test_filled_quantity_cannot_exceed_total(self):
        """Test that filled_quantity validation works."""
        with pytest.raises(ValueError, match="Filled quantity.*cannot exceed"):
            Order(
                order_id="12345",
                symbol=Symbol("QRLUSDT"),
                side=OrderSide.buy(),
                quantity=Quantity.from_float(10.0),
                _filled_quantity=Decimal("15.0"),  # Exceeds total
            )


class TestOrderProperties:
    """Tests for Order calculated properties."""

    def test_remaining_quantity(self):
        """Test remaining quantity calculation."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            _filled_quantity=Decimal("3.0"),
        )

        assert float(order.remaining_quantity) == 7.0

    def test_is_fully_filled(self):
        """Test fully filled detection."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            _filled_quantity=Decimal("10.0"),
        )

        assert order.is_fully_filled
        assert not order.is_partially_filled

    def test_is_partially_filled(self):
        """Test partially filled detection."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            _filled_quantity=Decimal("5.0"),
        )

        assert order.is_partially_filled
        assert not order.is_fully_filled

    def test_total_value_limit_order(self):
        """Test total value calculation for limit order."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
        )

        total = order.total_value
        assert total is not None
        assert float(total) == 1005.0  # 10 * 100.5

    def test_total_value_market_order(self):
        """Test total value is None for market order."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
        )

        assert order.total_value is None


class TestOrderQueryMethods:
    """Tests for Order query methods."""

    def test_is_market_and_limit_order(self):
        """Test market and limit order detection."""
        market_order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
        )

        limit_order = Order(
            order_id="67890",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
        )

        assert market_order.is_market_order()
        assert not market_order.is_limit_order()

        assert not limit_order.is_market_order()
        assert limit_order.is_limit_order()

    def test_is_buy_and_sell(self):
        """Test order side detection."""
        buy_order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
        )

        sell_order = Order(
            order_id="67890",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.sell(),
            quantity=Quantity.from_float(10.0),
        )

        assert buy_order.is_buy()
        assert not buy_order.is_sell()

        assert sell_order.is_sell()
        assert not sell_order.is_buy()

    def test_status_detection_methods(self):
        """Test status detection methods."""
        new_order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            status=OrderStatus.new(),
        )

        filled_order = Order(
            order_id="67890",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            status=OrderStatus.filled(),
        )

        assert new_order.is_active()
        assert not new_order.is_filled()
        assert not new_order.is_final()

        assert not filled_order.is_active()
        assert filled_order.is_filled()
        assert filled_order.is_final()


class TestOrderStateTransitions:
    """Tests for Order state transition methods."""

    def test_fill_order_completely(self):
        """Test filling an order completely."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.0, "USDT"),
        )

        order.fill(Quantity.from_float(10.0), Price.from_float(100.0, "USDT"))

        assert order.is_filled()
        assert float(order.filled_quantity) == 10.0
        assert order.is_fully_filled

    def test_fill_order_validates_price_for_buy(self):
        """Test that fill validates execution price for buy orders."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.0, "USDT"),
        )

        # Try to fill at higher price (should fail)
        with pytest.raises(ValueError, match="exceeds limit price"):
            order.fill(Quantity.from_float(10.0), Price.from_float(101.0, "USDT"))

    def test_fill_order_validates_price_for_sell(self):
        """Test that fill validates execution price for sell orders."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.sell(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.0, "USDT"),
        )

        # Try to fill at lower price (should fail)
        with pytest.raises(ValueError, match="below limit price"):
            order.fill(Quantity.from_float(10.0), Price.from_float(99.0, "USDT"))

    def test_cannot_fill_final_order(self):
        """Test that filled orders cannot be filled again."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            status=OrderStatus.filled(),
        )

        with pytest.raises(ValueError, match="Cannot fill order in final state"):
            order.fill(Quantity.from_float(5.0), Price.from_float(100.0, "USDT"))

    def test_partial_fill_order(self):
        """Test partially filling an order."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.0, "USDT"),
        )

        order.partial_fill(Quantity.from_float(3.0), Price.from_float(100.0, "USDT"))

        assert order.is_partially_filled
        assert float(order.filled_quantity) == 3.0
        assert float(order.remaining_quantity) == 7.0
        assert order.status.value == OrderStatusEnum.PARTIALLY_FILLED

    def test_multiple_partial_fills(self):
        """Test multiple partial fills."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.0, "USDT"),
        )

        order.partial_fill(Quantity.from_float(3.0), Price.from_float(100.0, "USDT"))
        order.partial_fill(Quantity.from_float(2.0), Price.from_float(100.0, "USDT"))
        order.partial_fill(Quantity.from_float(5.0), Price.from_float(100.0, "USDT"))

        assert order.is_filled()
        assert float(order.filled_quantity) == 10.0

    def test_partial_fill_cannot_exceed_quantity(self):
        """Test that partial fills cannot exceed total quantity."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.0, "USDT"),
        )

        order.partial_fill(Quantity.from_float(7.0), Price.from_float(100.0, "USDT"))

        with pytest.raises(ValueError, match="would exceed order quantity"):
            order.partial_fill(Quantity.from_float(5.0), Price.from_float(100.0, "USDT"))

    def test_cancel_order(self):
        """Test canceling an order."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
        )

        order.cancel()

        assert order.is_canceled()
        assert order.is_final()

    def test_cannot_cancel_filled_order(self):
        """Test that filled orders cannot be canceled."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            status=OrderStatus.filled(),
        )

        with pytest.raises(ValueError, match="Cannot cancel order"):
            order.cancel()

    def test_reject_order(self):
        """Test rejecting an order."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
        )

        order.reject("Insufficient balance")

        assert order.status.value == OrderStatusEnum.REJECTED
        assert order.is_final()

    def test_expire_order(self):
        """Test expiring an order."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
        )

        order.expire()

        assert order.status.value == OrderStatusEnum.EXPIRED
        assert order.is_final()


class TestOrderSerialization:
    """Tests for Order serialization."""

    def test_to_dict(self):
        """Test converting order to dictionary."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
        )

        order_dict = order.to_dict()

        assert order_dict["order_id"] == "12345"
        assert order_dict["symbol"] == "QRLUSDT"
        assert order_dict["side"] == "BUY"
        assert order_dict["quantity"] == 10.0
        assert order_dict["price"] == 100.5
        assert order_dict["status"] == "NEW"
        assert "created_at" in order_dict
        assert order_dict["filled_quantity"] == 0.0
        assert order_dict["remaining_quantity"] == 10.0
        assert order_dict["total_value"] == 1005.0


class TestOrderDomainInvariants:
    """Tests for Order domain invariants and business rules."""

    def test_order_id_is_identity(self):
        """Test that order_id serves as entity identity."""
        order1 = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
        )

        order2 = Order(
            order_id="12345",
            symbol=Symbol("BTCUSDT"),
            side=OrderSide.sell(),
            quantity=Quantity.from_float(5.0),
        )

        # Same order_id = same entity (even with different attributes)
        assert order1.order_id == order2.order_id

    def test_value_objects_are_immutable(self):
        """Test that value objects within order are immutable."""
        order = Order(
            order_id="12345",
            symbol=Symbol("QRLUSDT"),
            side=OrderSide.buy(),
            quantity=Quantity.from_float(10.0),
            price=Price.from_float(100.5, "USDT"),
        )

        # Value objects are immutable
        with pytest.raises(Exception):  # FrozenInstanceError
            order.symbol.value = "BTCUSDT"

        with pytest.raises(Exception):
            order.price.value = Decimal("200.0")

    def test_order_validation_via_value_objects(self):
        """Test that value objects enforce validation."""
        # Invalid symbol should raise error
        with pytest.raises(ValueError):
            Order(
                order_id="12345",
                symbol=Symbol(""),  # Empty symbol
                side=OrderSide.buy(),
                quantity=Quantity.from_float(10.0),
            )

        # Negative quantity should raise error
        with pytest.raises(ValueError):
            Order(
                order_id="12345",
                symbol=Symbol("QRLUSDT"),
                side=OrderSide.buy(),
                quantity=Quantity.from_float(-10.0),  # Negative
            )

        # Negative price should raise error
        with pytest.raises(ValueError):
            Order(
                order_id="12345",
                symbol=Symbol("QRLUSDT"),
                side=OrderSide.buy(),
                quantity=Quantity.from_float(10.0),
                price=Price.from_float(-100.5, "USDT"),  # Negative
            )
