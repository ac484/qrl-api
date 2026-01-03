"""Tests for domain value objects.

Tests verify that value objects follow DDD patterns:
- Immutability (frozen dataclasses)
- Validation on creation
- Equality by value
- Hash consistency
"""

from decimal import Decimal

import pytest

from src.app.domain.value_objects import (
    OrderSide,
    OrderSideEnum,
    OrderStatus,
    OrderStatusEnum,
    Price,
    Quantity,
    Symbol,
)


class TestSymbol:
    """Tests for Symbol value object."""

    def test_create_valid_symbol(self):
        """Test creating a valid symbol."""
        symbol = Symbol("QRLUSDT")
        assert symbol.value == "QRLUSDT"

    def test_create_symbol_with_parts(self):
        """Test creating a symbol with base and quote."""
        symbol = Symbol("BTCUSDT", base="BTC", quote="USDT")
        assert symbol.value == "BTCUSDT"
        assert symbol.base == "BTC"
        assert symbol.quote == "USDT"

    def test_create_symbol_from_parts(self):
        """Test factory method to create symbol from parts."""
        symbol = Symbol.from_parts("QRL", "USDT")
        assert symbol.value == "QRLUSDT"
        assert symbol.base == "QRL"
        assert symbol.quote == "USDT"

    def test_symbol_immutable(self):
        """Test that symbol is immutable."""
        symbol = Symbol("QRLUSDT")
        with pytest.raises(Exception):  # FrozenInstanceError
            symbol.value = "BTCUSDT"

    def test_symbol_validation_empty(self):
        """Test that empty symbol is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Symbol("")

    def test_symbol_validation_lowercase(self):
        """Test that lowercase symbol is rejected."""
        with pytest.raises(ValueError, match="must be uppercase"):
            Symbol("qrlusdt")

    def test_symbol_validation_too_short(self):
        """Test that too short symbol is rejected."""
        with pytest.raises(ValueError, match="too short"):
            Symbol("AB")

    def test_symbol_validation_non_alphanumeric(self):
        """Test that non-alphanumeric symbol is rejected."""
        with pytest.raises(ValueError, match="must be alphanumeric"):
            Symbol("QRL-USDT")

    def test_symbol_equality(self):
        """Test that symbols are equal by value."""
        symbol1 = Symbol("QRLUSDT")
        symbol2 = Symbol("QRLUSDT")
        assert symbol1 == symbol2
        assert hash(symbol1) == hash(symbol2)

    def test_symbol_inequality(self):
        """Test that different symbols are not equal."""
        symbol1 = Symbol("QRLUSDT")
        symbol2 = Symbol("BTCUSDT")
        assert symbol1 != symbol2

    def test_symbol_str_repr(self):
        """Test string representations."""
        symbol = Symbol("QRLUSDT")
        assert str(symbol) == "QRLUSDT"
        assert "Symbol" in repr(symbol)


class TestPrice:
    """Tests for Price value object."""

    def test_create_valid_price(self):
        """Test creating a valid price."""
        price = Price(Decimal("100.5"), "USDT")
        assert price.value == Decimal("100.5")
        assert price.currency == "USDT"

    def test_create_price_from_float(self):
        """Test factory method to create price from float."""
        price = Price.from_float(100.5, "USDT")
        assert price.value == Decimal("100.5")
        assert price.currency == "USDT"

    def test_create_price_from_string(self):
        """Test factory method to create price from string."""
        price = Price.from_string("100.50", "USDT")
        assert price.value == Decimal("100.50")
        assert price.currency == "USDT"

    def test_price_immutable(self):
        """Test that price is immutable."""
        price = Price.from_float(100.5, "USDT")
        with pytest.raises(Exception):  # FrozenInstanceError
            price.value = Decimal("200")

    def test_price_validation_type(self):
        """Test that non-Decimal value is rejected."""
        with pytest.raises(TypeError, match="must be Decimal"):
            Price(100.5, "USDT")  # type: ignore

    def test_price_validation_negative(self):
        """Test that negative price is rejected."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Price(Decimal("-100"), "USDT")

    def test_price_validation_currency_empty(self):
        """Test that empty currency is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Price(Decimal("100"), "")

    def test_price_validation_currency_lowercase(self):
        """Test that lowercase currency is rejected."""
        with pytest.raises(ValueError, match="must be uppercase"):
            Price(Decimal("100"), "usdt")

    def test_price_equality(self):
        """Test that prices are equal by value."""
        price1 = Price.from_float(100.5, "USDT")
        price2 = Price.from_float(100.5, "USDT")
        assert price1 == price2
        assert hash(price1) == hash(price2)

    def test_price_inequality(self):
        """Test that different prices are not equal."""
        price1 = Price.from_float(100.0, "USDT")
        price2 = Price.from_float(200.0, "USDT")
        assert price1 != price2

    def test_price_comparison_operators(self):
        """Test price comparison operators."""
        price1 = Price.from_float(100.0, "USDT")
        price2 = Price.from_float(200.0, "USDT")

        assert price1 < price2
        assert price1 <= price2
        assert price2 > price1
        assert price2 >= price1

    def test_price_comparison_different_currency(self):
        """Test that comparing different currencies raises error."""
        price1 = Price.from_float(100.0, "USDT")
        price2 = Price.from_float(100.0, "USD")

        with pytest.raises(ValueError, match="different currencies"):
            price1 < price2

    def test_price_multiply(self):
        """Test price multiplication."""
        price = Price.from_float(100.0, "USDT")
        doubled = price.multiply(Decimal("2"))

        assert doubled.value == Decimal("200.0")
        assert doubled.currency == "USDT"
        assert price.value == Decimal("100.0")  # Original unchanged

    def test_price_add(self):
        """Test price addition."""
        price1 = Price.from_float(100.0, "USDT")
        price2 = Price.from_float(50.0, "USDT")
        total = price1.add(price2)

        assert total.value == Decimal("150.0")
        assert total.currency == "USDT"

    def test_price_is_zero(self):
        """Test zero price detection."""
        zero_price = Price.from_float(0.0, "USDT")
        non_zero_price = Price.from_float(100.0, "USDT")

        assert zero_price.is_zero()
        assert not non_zero_price.is_zero()

    def test_price_float_conversion(self):
        """Test conversion to float."""
        price = Price.from_float(100.5, "USDT")
        assert float(price) == 100.5


class TestQuantity:
    """Tests for Quantity value object."""

    def test_create_valid_quantity(self):
        """Test creating a valid quantity."""
        qty = Quantity(Decimal("10.5"))
        assert qty.value == Decimal("10.5")

    def test_create_quantity_from_float(self):
        """Test factory method to create quantity from float."""
        qty = Quantity.from_float(10.5)
        assert qty.value == Decimal("10.5")

    def test_create_quantity_from_string(self):
        """Test factory method to create quantity from string."""
        qty = Quantity.from_string("10.50")
        assert qty.value == Decimal("10.50")

    def test_quantity_immutable(self):
        """Test that quantity is immutable."""
        qty = Quantity.from_float(10.5)
        with pytest.raises(Exception):  # FrozenInstanceError
            qty.value = Decimal("20")

    def test_quantity_validation_type(self):
        """Test that non-Decimal value is rejected."""
        with pytest.raises(TypeError, match="must be Decimal"):
            Quantity(10.5)  # type: ignore

    def test_quantity_validation_negative(self):
        """Test that negative quantity is rejected."""
        with pytest.raises(ValueError, match="must be positive"):
            Quantity(Decimal("-10"))

    def test_quantity_validation_zero(self):
        """Test that zero quantity is rejected."""
        with pytest.raises(ValueError, match="must be positive"):
            Quantity(Decimal("0"))

    def test_quantity_equality(self):
        """Test that quantities are equal by value."""
        qty1 = Quantity.from_float(10.5)
        qty2 = Quantity.from_float(10.5)
        assert qty1 == qty2
        assert hash(qty1) == hash(qty2)

    def test_quantity_inequality(self):
        """Test that different quantities are not equal."""
        qty1 = Quantity.from_float(10.0)
        qty2 = Quantity.from_float(20.0)
        assert qty1 != qty2

    def test_quantity_comparison_operators(self):
        """Test quantity comparison operators."""
        qty1 = Quantity.from_float(10.0)
        qty2 = Quantity.from_float(20.0)

        assert qty1 < qty2
        assert qty1 <= qty2
        assert qty2 > qty1
        assert qty2 >= qty1

    def test_quantity_multiply(self):
        """Test quantity multiplication."""
        qty = Quantity.from_float(10.0)
        doubled = qty.multiply(Decimal("2"))

        assert doubled.value == Decimal("20.0")
        assert qty.value == Decimal("10.0")  # Original unchanged

    def test_quantity_add(self):
        """Test quantity addition."""
        qty1 = Quantity.from_float(10.0)
        qty2 = Quantity.from_float(5.0)
        total = qty1.add(qty2)

        assert total.value == Decimal("15.0")

    def test_quantity_subtract(self):
        """Test quantity subtraction."""
        qty1 = Quantity.from_float(10.0)
        qty2 = Quantity.from_float(5.0)
        result = qty1.subtract(qty2)

        assert result.value == Decimal("5.0")

    def test_quantity_subtract_too_much(self):
        """Test that subtracting too much raises error."""
        qty1 = Quantity.from_float(10.0)
        qty2 = Quantity.from_float(10.0)

        with pytest.raises(ValueError, match="non-positive"):
            qty1.subtract(qty2)

    def test_quantity_float_conversion(self):
        """Test conversion to float."""
        qty = Quantity.from_float(10.5)
        assert float(qty) == 10.5


class TestOrderSide:
    """Tests for OrderSide value object."""

    def test_create_buy_side(self):
        """Test creating a BUY order side."""
        side = OrderSide.buy()
        assert side.value == OrderSideEnum.BUY
        assert side.is_buy()
        assert not side.is_sell()

    def test_create_sell_side(self):
        """Test creating a SELL order side."""
        side = OrderSide.sell()
        assert side.value == OrderSideEnum.SELL
        assert side.is_sell()
        assert not side.is_buy()

    def test_create_from_string(self):
        """Test creating order side from string."""
        buy = OrderSide.from_string("BUY")
        sell = OrderSide.from_string("sell")  # Case insensitive

        assert buy.is_buy()
        assert sell.is_sell()

    def test_create_from_invalid_string(self):
        """Test that invalid string raises error."""
        with pytest.raises(ValueError, match="Invalid order side"):
            OrderSide.from_string("INVALID")

    def test_order_side_immutable(self):
        """Test that order side is immutable."""
        side = OrderSide.buy()
        with pytest.raises(Exception):  # FrozenInstanceError
            side.value = OrderSideEnum.SELL

    def test_order_side_equality(self):
        """Test that order sides are equal by value."""
        side1 = OrderSide.buy()
        side2 = OrderSide.buy()
        assert side1 == side2
        assert hash(side1) == hash(side2)

    def test_order_side_inequality(self):
        """Test that different order sides are not equal."""
        buy = OrderSide.buy()
        sell = OrderSide.sell()
        assert buy != sell

    def test_order_side_opposite(self):
        """Test getting opposite side."""
        buy = OrderSide.buy()
        sell = buy.opposite()

        assert sell.is_sell()
        assert sell.opposite().is_buy()

    def test_order_side_str_repr(self):
        """Test string representations."""
        side = OrderSide.buy()
        assert str(side) == "BUY"
        assert "OrderSide" in repr(side)


class TestOrderStatus:
    """Tests for OrderStatus value object."""

    def test_create_various_statuses(self):
        """Test creating various order statuses."""
        new = OrderStatus.new()
        filled = OrderStatus.filled()
        canceled = OrderStatus.canceled()

        assert new.is_new()
        assert filled.is_filled()
        assert canceled.is_canceled()

    def test_create_from_string(self):
        """Test creating order status from string."""
        status = OrderStatus.from_string("FILLED")
        assert status.is_filled()

        # Case insensitive
        status2 = OrderStatus.from_string("filled")
        assert status2.is_filled()

    def test_create_from_invalid_string(self):
        """Test that invalid string raises error."""
        with pytest.raises(ValueError, match="Invalid order status"):
            OrderStatus.from_string("INVALID")

    def test_order_status_immutable(self):
        """Test that order status is immutable."""
        status = OrderStatus.new()
        with pytest.raises(Exception):  # FrozenInstanceError
            status.value = OrderStatusEnum.FILLED

    def test_order_status_equality(self):
        """Test that order statuses are equal by value."""
        status1 = OrderStatus.new()
        status2 = OrderStatus.new()
        assert status1 == status2
        assert hash(status1) == hash(status2)

    def test_order_status_inequality(self):
        """Test that different order statuses are not equal."""
        new = OrderStatus.new()
        filled = OrderStatus.filled()
        assert new != filled

    def test_order_status_is_active(self):
        """Test checking if order is active."""
        new = OrderStatus.new()
        partially = OrderStatus.partially_filled()
        filled = OrderStatus.filled()

        assert new.is_active()
        assert partially.is_active()
        assert not filled.is_active()

    def test_order_status_is_final(self):
        """Test checking if order is in final state."""
        new = OrderStatus.new()
        filled = OrderStatus.filled()
        canceled = OrderStatus.canceled()

        assert not new.is_final()
        assert filled.is_final()
        assert canceled.is_final()

    def test_order_status_can_cancel(self):
        """Test checking if order can be canceled."""
        new = OrderStatus.new()
        partially = OrderStatus.partially_filled()
        filled = OrderStatus.filled()

        assert new.can_cancel()
        assert partially.can_cancel()
        assert not filled.can_cancel()

    def test_order_status_str_repr(self):
        """Test string representations."""
        status = OrderStatus.new()
        assert str(status) == "NEW"
        assert "OrderStatus" in repr(status)


class TestValueObjectIntegration:
    """Integration tests for value objects working together."""

    def test_value_objects_as_dict_keys(self):
        """Test that value objects can be used as dictionary keys."""
        symbol = Symbol("QRLUSDT")
        price = Price.from_float(100.0, "USDT")

        prices = {symbol: price}
        assert prices[Symbol("QRLUSDT")] == price

    def test_value_objects_in_sets(self):
        """Test that value objects can be used in sets."""
        symbols = {
            Symbol("QRLUSDT"),
            Symbol("BTCUSDT"),
            Symbol("QRLUSDT"),  # Duplicate
        }

        assert len(symbols) == 2  # Duplicate removed

    def test_value_objects_composition(self):
        """Test composing value objects together."""
        symbol = Symbol("QRLUSDT")
        price = Price.from_float(100.5, "USDT")
        quantity = Quantity.from_float(10.0)
        side = OrderSide.buy()
        status = OrderStatus.new()

        # Value objects can be composed to represent complex domain concepts
        order_data = {
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "side": side,
            "status": status,
        }

        assert order_data["symbol"].value == "QRLUSDT"
        assert order_data["side"].is_buy()
        assert order_data["status"].is_active()
