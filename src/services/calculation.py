"""
Core calculation service for salary adjustment (reajuste) calculations.

Implements the formulas specified in Lei 14.133/21 and Decreto Estadual 10.086/22:
- K = (I_i / I_0) - 1
- R = K × Vr

All calculations use Decimal type and follow strict truncation rules.
"""

from decimal import Decimal
from sqlalchemy.orm import Session
from src.utils.decimal_utils import truncate_at_4_decimals, truncate_at_2_decimals, ensure_decimal
from src.db.models import CalculoRealizado
import datetime


def calcular_fator_k_truncado(indice_inicial: Decimal, indice_final: Decimal) -> Decimal:
    """
    Calculate adjustment factor K with truncation at 4th decimal place.

    Formula: K = (I_i / I_0) - 1

    Where:
    - I_i: Index at revaluation month (índice no mês de reajuste)
    - I_0: Index at budget date (índice na data base do orçamento)

    The result is truncated (not rounded) to 0.0001 precision.

    Examples:
        >>> calcular_fator_k_truncado(Decimal("105.4"), Decimal("105.5"))
        Decimal('0.0009')  # Not 0.0010

        >>> calcular_fator_k_truncado(Decimal("100.0"), Decimal("110.5"))
        Decimal('0.1050')

    Args:
        indice_inicial: I_0 (base index from budget date)
        indice_final: I_i (revaluation month index)

    Returns:
        Decimal: K factor truncated to 4 decimal places

    Raises:
        ValueError: If indice_inicial is zero or negative
        TypeError: If inputs are not Decimal
    """
    # Input validation and conversion
    indice_inicial = ensure_decimal(indice_inicial)
    indice_final = ensure_decimal(indice_final)

    # Handle division by zero
    if indice_inicial == 0:
        raise ValueError("Base index (I_0) cannot be zero")

    if indice_inicial < 0 or indice_final < 0:
        raise ValueError("Indices must be positive values")

    # K = (I_i / I_0) - 1
    k_bruto = (indice_final / indice_inicial) - Decimal("1")

    # Truncate to 4 decimals (ROUND_FLOOR, no rounding up)
    k_truncado = truncate_at_4_decimals(k_bruto)

    return k_truncado


def calcular_valor_reajuste(valor_medicao: Decimal, fator_k: Decimal) -> Decimal:
    """
    Calculate adjustment value.

    Formula: R = K × Vr

    Where:
    - R: Adjustment value (valor do reajuste)
    - Vr: Measurement/invoice value (valor da medição)
    - K: Adjustment factor (fator de reajuste)

    Result is truncated to 2 decimal places (cents).

    Examples:
        >>> calcular_valor_reajuste(Decimal("10000.00"), Decimal("0.0009"))
        Decimal('9.00')

        >>> calcular_valor_reajuste(Decimal("50000.00"), Decimal("0.1234"))
        Decimal('6170.00')

    Args:
        valor_medicao: Vr (measurement value in R$)
        fator_k: K (adjustment factor, should be pre-truncated to 4 decimals)

    Returns:
        Decimal: Adjustment value in cents precision (2 decimals)

    Raises:
        ValueError: If valor_medicao is negative
        TypeError: If inputs are not Decimal
    """
    valor_medicao = ensure_decimal(valor_medicao)
    fator_k = ensure_decimal(fator_k)

    if valor_medicao < 0:
        raise ValueError("Measurement value (Vr) cannot be negative")

    # R = K × Vr
    valor_reajuste = valor_medicao * fator_k

    # Truncate to 2 decimals (cents precision)
    return truncate_at_2_decimals(valor_reajuste)


def calcular_valor_total_atualizado(valor_medicao: Decimal, valor_reajuste: Decimal) -> Decimal:
    """
    Calculate total updated value after adjustment.

    Formula: Total = Vr + R

    Args:
        valor_medicao: Original measurement value
        valor_reajuste: Calculated adjustment value

    Returns:
        Decimal: Total value after adjustment
    """
    valor_medicao = ensure_decimal(valor_medicao)
    valor_reajuste = ensure_decimal(valor_reajuste)

    return truncate_at_2_decimals(valor_medicao + valor_reajuste)


def salvar_calculo(
    db: Session,
    contrato_id: int,
    mes_indice_base: datetime.date,
    valor_indice_base: Decimal,
    mes_indice_reajuste: datetime.date,
    valor_indice_reajuste: Decimal,
    fator_k_aplicado: Decimal,
    valor_original_medicao: Decimal,
    valor_reajuste: Decimal
) -> CalculoRealizado:
    """
    Save calculation to audit log.

    This creates a permanent record of the calculation for legal compliance
    and traceability.

    Args:
        db: Database session
        contrato_id: Contract ID
        mes_indice_base: Base index month (I_0 reference date)
        valor_indice_base: Base index value (I_0)
        mes_indice_reajuste: Adjustment index month (I_i reference date)
        valor_indice_reajuste: Adjustment index value (I_i)
        fator_k_aplicado: K factor applied (truncated to 4 decimals)
        valor_original_medicao: Original measurement value (Vr)
        valor_reajuste: Calculated adjustment value (R)

    Returns:
        CalculoRealizado: Saved calculation record

    Raises:
        SQLAlchemyError: If database operation fails
    """
    calculo = CalculoRealizado(
        contrato_id=contrato_id,
        data_calculo=datetime.datetime.utcnow(),
        mes_indice_base=mes_indice_base,
        valor_indice_base=ensure_decimal(valor_indice_base),
        mes_indice_reajuste=mes_indice_reajuste,
        valor_indice_reajuste=ensure_decimal(valor_indice_reajuste),
        fator_k_aplicado=ensure_decimal(fator_k_aplicado),
        valor_original_medicao=ensure_decimal(valor_original_medicao),
        valor_reajuste=ensure_decimal(valor_reajuste)
    )

    db.add(calculo)
    db.commit()
    db.refresh(calculo)

    return calculo


def validar_intersticio_legal(
    data_base_orcamento: datetime.date,
    mes_reajuste: datetime.date
) -> tuple[bool, str]:
    """
    Validate if the legal interval (365 days) has passed for adjustment.

    According to Lei 14.133/21, adjustments can only occur after 365 days
    from the budget date.

    Args:
        data_base_orcamento: Budget date (contract base date)
        mes_reajuste: Proposed adjustment month

    Returns:
        tuple: (is_valid, message)
            - is_valid: True if interval is valid
            - message: Explanation message
    """
    # Calculate difference in days
    diferenca = (mes_reajuste - data_base_orcamento).days

    if diferenca < 365:
        return (
            False,
            f"Interstício legal não cumprido. "
            f"Passaram-se {diferenca} dias, mas são necessários 365 dias "
            f"desde a data base do orçamento ({data_base_orcamento.strftime('%d/%m/%Y')})."
        )

    return (
        True,
        f"Interstício legal cumprido ({diferenca} dias desde a data base)."
    )
