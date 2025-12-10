"""
Decimal utility functions for financial calculations.

This module implements the critical truncation rule required by law:
"O quociente de reajuste (K) deve considerar até a quarta casa decimal,
SEM ARREDONDAMENTO" (Clause 11.4 of the Standard Tender Document)

IMPORTANT: All financial values must use Python's Decimal type, never float.
"""

from decimal import Decimal, ROUND_FLOOR, ROUND_DOWN, getcontext

# Set global precision context for safe financial calculations
getcontext().prec = 28


def truncate_at_4_decimals(value: Decimal) -> Decimal:
    """
    Truncate a Decimal to 4 decimal places WITHOUT rounding.

    This implements the hard constraint from the specification:
    "O quociente de reajuste (K) deve considerar até a quarta casa
     decimal, SEM ARREDONDAMENTO"

    Examples:
        >>> truncate_at_4_decimals(Decimal("0.12349"))
        Decimal('0.1234')  # NOT 0.1235

        >>> truncate_at_4_decimals(Decimal("0.99999"))
        Decimal('0.9999')  # NOT 1.0000

        >>> truncate_at_4_decimals(Decimal("1.23456"))
        Decimal('1.2345')

    Args:
        value: A Decimal number to truncate

    Returns:
        Decimal truncated to 4 decimal places (always rounds DOWN)

    Raises:
        TypeError: If value is not a Decimal
    """
    if value is None:
        return None

    if not isinstance(value, Decimal):
        raise TypeError(f"Expected Decimal, got {type(value).__name__}")

    # quantize with ROUND_FLOOR: always rounds DOWN (toward -infinity)
    # For positive numbers, this is true truncation (floor)
    # For negative numbers, this also truncates toward -infinity
    return value.quantize(Decimal("0.0001"), rounding=ROUND_FLOOR)


def truncate_at_2_decimals(value: Decimal) -> Decimal:
    """
    Truncate a Decimal to 2 decimal places (cents precision).

    Used for final monetary values in Brazilian Real (R$).

    Examples:
        >>> truncate_at_2_decimals(Decimal("123.456"))
        Decimal('123.45')

        >>> truncate_at_2_decimals(Decimal("999.999"))
        Decimal('999.99')

    Args:
        value: A Decimal number to truncate

    Returns:
        Decimal truncated to 2 decimal places

    Raises:
        TypeError: If value is not a Decimal
    """
    if value is None:
        return None

    if not isinstance(value, Decimal):
        raise TypeError(f"Expected Decimal, got {type(value).__name__}")

    return value.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)


def ensure_decimal(value) -> Decimal:
    """
    Safely convert input to Decimal.

    NEVER accept float directly - always use string representation
    to avoid precision loss.

    Examples:
        >>> ensure_decimal("123.45")
        Decimal('123.45')

        >>> ensure_decimal(100)
        Decimal('100')

        >>> ensure_decimal(Decimal("50.25"))
        Decimal('50.25')

    Args:
        value: Value to convert (Decimal, str, or int)

    Returns:
        Decimal representation of the value

    Raises:
        TypeError: If value type cannot be safely converted to Decimal
        ValueError: If string value is not a valid decimal number
    """
    if isinstance(value, Decimal):
        return value

    if isinstance(value, str):
        try:
            return Decimal(value)
        except Exception as e:
            raise ValueError(f"Cannot convert string '{value}' to Decimal: {e}")

    if isinstance(value, int):
        return Decimal(value)

    # Explicitly reject float to prevent precision loss
    if isinstance(value, float):
        raise TypeError(
            f"Cannot convert float to Decimal directly. "
            f"Use string conversion: Decimal(str({value})) instead of Decimal({value})"
        )

    raise TypeError(
        f"Cannot convert {type(value).__name__} to Decimal. "
        f"Supported types: Decimal, str, int"
    )


def format_brazilian_currency(value: Decimal) -> str:
    """
    Format a Decimal value as Brazilian currency (R$).

    Examples:
        >>> format_brazilian_currency(Decimal("1234.56"))
        'R$ 1.234,56'

        >>> format_brazilian_currency(Decimal("1000000.00"))
        'R$ 1.000.000,00'

    Args:
        value: Decimal value to format

    Returns:
        Formatted currency string with Brazilian conventions
    """
    if value is None:
        return "R$ 0,00"

    # Convert to string with 2 decimal places
    value_str = f"{value:.2f}"

    # Split integer and decimal parts
    integer_part, decimal_part = value_str.split(".")

    # Add thousand separators (dots in Brazilian format)
    integer_with_separators = "{:,}".format(int(integer_part)).replace(",", ".")

    # Return formatted string
    return f"R$ {integer_with_separators},{decimal_part}"


def format_percentage(value: Decimal, decimals: int = 4) -> str:
    """
    Format a Decimal value as percentage.

    Examples:
        >>> format_percentage(Decimal("0.1234"))
        '12,3400%'

        >>> format_percentage(Decimal("0.05"), decimals=2)
        '5,00%'

    Args:
        value: Decimal value (e.g., 0.1234 for 12.34%)
        decimals: Number of decimal places to display

    Returns:
        Formatted percentage string
    """
    if value is None:
        return "0,0000%"

    percentage = value * 100
    formatted = f"{percentage:.{decimals}f}".replace(".", ",")
    return f"{formatted}%"


def format_date_br(date_obj) -> str:
    """
    Format date in Brazilian format (dd/mm/yyyy).

    Args:
        date_obj: datetime.date object

    Returns:
        Formatted date string (dd/mm/yyyy)
    """
    if date_obj is None:
        return ""
    return date_obj.strftime("%d/%m/%Y")
