"""
Tests for decimal utility functions.

Critical: These tests verify the truncation rule (no rounding).
"""

import pytest
from decimal import Decimal
from src.utils.decimal_utils import (
    truncate_at_4_decimals,
    truncate_at_2_decimals,
    ensure_decimal,
    format_brazilian_currency,
    format_percentage
)


class TestTruncateAt4Decimals:
    """Test truncation at 4 decimal places."""

    def test_truncate_basic(self):
        """Test basic truncation without rounding."""
        # Critical test from specification
        assert truncate_at_4_decimals(Decimal("0.12349")) == Decimal("0.1234")
        assert truncate_at_4_decimals(Decimal("0.99999")) == Decimal("0.9999")

    def test_truncate_not_round(self):
        """Verify truncation does NOT round up."""
        # These should truncate DOWN, not round up
        assert truncate_at_4_decimals(Decimal("0.12345")) == Decimal("0.1234")
        assert truncate_at_4_decimals(Decimal("0.12348")) == Decimal("0.1234")
        assert truncate_at_4_decimals(Decimal("1.99999")) == Decimal("1.9999")

    def test_truncate_exact_4_decimals(self):
        """Test values that already have 4 decimals."""
        assert truncate_at_4_decimals(Decimal("0.1234")) == Decimal("0.1234")
        assert truncate_at_4_decimals(Decimal("1.5000")) == Decimal("1.5000")

    def test_truncate_fewer_decimals(self):
        """Test values with fewer than 4 decimals."""
        assert truncate_at_4_decimals(Decimal("0.12")) == Decimal("0.1200")
        assert truncate_at_4_decimals(Decimal("5")) == Decimal("5.0000")

    def test_truncate_large_numbers(self):
        """Test truncation with large numbers."""
        assert truncate_at_4_decimals(Decimal("1234.56789")) == Decimal("1234.5678")
        assert truncate_at_4_decimals(Decimal("100000.99999")) == Decimal("100000.9999")

    def test_truncate_none(self):
        """Test None input."""
        assert truncate_at_4_decimals(None) is None

    def test_truncate_invalid_type(self):
        """Test that non-Decimal types raise TypeError."""
        with pytest.raises(TypeError):
            truncate_at_4_decimals(0.12345)

        with pytest.raises(TypeError):
            truncate_at_4_decimals("0.12345")


class TestTruncateAt2Decimals:
    """Test truncation at 2 decimal places (cents)."""

    def test_truncate_cents(self):
        """Test truncation for currency values."""
        assert truncate_at_2_decimals(Decimal("123.456")) == Decimal("123.45")
        assert truncate_at_2_decimals(Decimal("999.999")) == Decimal("999.99")

    def test_truncate_not_round_cents(self):
        """Verify cents truncation does NOT round up."""
        assert truncate_at_2_decimals(Decimal("10.999")) == Decimal("10.99")
        assert truncate_at_2_decimals(Decimal("5.995")) == Decimal("5.99")


class TestEnsureDecimal:
    """Test safe Decimal conversion."""

    def test_ensure_from_decimal(self):
        """Test conversion from Decimal (no-op)."""
        value = Decimal("123.45")
        assert ensure_decimal(value) == value

    def test_ensure_from_string(self):
        """Test conversion from string."""
        assert ensure_decimal("123.45") == Decimal("123.45")
        assert ensure_decimal("0.1234") == Decimal("0.1234")

    def test_ensure_from_int(self):
        """Test conversion from int."""
        assert ensure_decimal(100) == Decimal("100")
        assert ensure_decimal(0) == Decimal("0")

    def test_ensure_reject_float(self):
        """Test that float is rejected to prevent precision loss."""
        with pytest.raises(TypeError, match="Cannot convert float"):
            ensure_decimal(123.45)

    def test_ensure_invalid_string(self):
        """Test that invalid strings raise ValueError."""
        with pytest.raises(ValueError):
            ensure_decimal("invalid")

    def test_ensure_invalid_type(self):
        """Test that unsupported types raise TypeError."""
        with pytest.raises(TypeError):
            ensure_decimal([123])


class TestFormatBrazilianCurrency:
    """Test Brazilian currency formatting."""

    def test_format_basic(self):
        """Test basic currency formatting."""
        assert format_brazilian_currency(Decimal("1234.56")) == "R$ 1.234,56"
        assert format_brazilian_currency(Decimal("100.00")) == "R$ 100,00"

    def test_format_large_values(self):
        """Test formatting large values."""
        assert format_brazilian_currency(Decimal("1000000.00")) == "R$ 1.000.000,00"
        assert format_brazilian_currency(Decimal("123456789.99")) == "R$ 123.456.789,99"

    def test_format_none(self):
        """Test None input."""
        assert format_brazilian_currency(None) == "R$ 0,00"


class TestFormatPercentage:
    """Test percentage formatting."""

    def test_format_percentage_default(self):
        """Test percentage formatting with default 4 decimals."""
        assert format_percentage(Decimal("0.1234")) == "12,3400%"
        assert format_percentage(Decimal("0.05")) == "5,0000%"

    def test_format_percentage_custom_decimals(self):
        """Test percentage formatting with custom decimals."""
        assert format_percentage(Decimal("0.1234"), decimals=2) == "12,34%"
        assert format_percentage(Decimal("0.05"), decimals=1) == "5,0%"

    def test_format_percentage_none(self):
        """Test None input."""
        assert format_percentage(None) == "0,0000%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
