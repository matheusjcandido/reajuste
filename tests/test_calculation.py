"""
Tests for calculation service functions.

Critical: These tests verify the K factor and adjustment calculations.
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from src.services.calculation import (
    calcular_fator_k_truncado,
    calcular_valor_reajuste,
    calcular_valor_total_atualizado,
    validar_intersticio_legal
)


class TestCalcularFatorK:
    """Test K factor calculation with truncation."""

    def test_k_factor_basic(self):
        """Test basic K factor calculation."""
        # Example: I_i=105.5 / I_0=105.4 = 1.000948... - 1 = 0.000948... -> 0.0009
        i0 = Decimal("105.4")
        ii = Decimal("105.5")
        k = calcular_fator_k_truncado(i0, ii)
        assert k == Decimal("0.0009")

    def test_k_factor_larger_increase(self):
        """Test K factor with larger index increase."""
        # I_i=110.0 / I_0=100.0 = 1.1 - 1 = 0.1
        i0 = Decimal("100.0")
        ii = Decimal("110.0")
        k = calcular_fator_k_truncado(i0, ii)
        assert k == Decimal("0.1000")

    def test_k_factor_truncation_not_rounding(self):
        """Verify K factor is truncated, not rounded."""
        # Create a case where truncation != rounding
        # I_i=105.6 / I_0=105.0 = 1.005714... - 1 = 0.005714... -> 0.0057 (not 0.0058)
        i0 = Decimal("105.0")
        ii = Decimal("105.6")
        k = calcular_fator_k_truncado(i0, ii)
        assert k == Decimal("0.0057")

    def test_k_factor_real_example(self):
        """Test with real INCC-DI values."""
        # Real example: INCC-DI progression
        i0 = Decimal("105.4560")
        ii = Decimal("106.2340")
        k = calcular_fator_k_truncado(i0, ii)

        # Manual calculation:
        # 106.2340 / 105.4560 = 1.007377...
        # 1.007377... - 1 = 0.007377...
        # Truncated to 4 decimals: 0.0073
        assert k == Decimal("0.0073")

    def test_k_factor_zero_base_index(self):
        """Test that zero base index raises error."""
        with pytest.raises(ValueError, match="cannot be zero"):
            calcular_fator_k_truncado(Decimal("0"), Decimal("100"))

    def test_k_factor_negative_index(self):
        """Test that negative indices raise error."""
        with pytest.raises(ValueError, match="must be positive"):
            calcular_fator_k_truncado(Decimal("-100"), Decimal("105"))

        with pytest.raises(ValueError, match="must be positive"):
            calcular_fator_k_truncado(Decimal("100"), Decimal("-105"))

    def test_k_factor_equal_indices(self):
        """Test K factor when indices are equal (no adjustment)."""
        i0 = Decimal("105.5")
        ii = Decimal("105.5")
        k = calcular_fator_k_truncado(i0, ii)
        assert k == Decimal("0.0000")

    def test_k_factor_with_string_inputs(self):
        """Test that string inputs are converted properly."""
        k = calcular_fator_k_truncado("105.4", "105.5")
        assert k == Decimal("0.0009")


class TestCalcularValorReajuste:
    """Test adjustment value calculation."""

    def test_reajuste_basic(self):
        """Test basic adjustment calculation."""
        # R = K × Vr
        # R = 0.0009 × 10000.00 = 9.00
        vr = Decimal("10000.00")
        k = Decimal("0.0009")
        r = calcular_valor_reajuste(vr, k)
        assert r == Decimal("9.00")

    def test_reajuste_larger_value(self):
        """Test adjustment with larger K factor."""
        # R = 0.1234 × 50000.00 = 6170.00
        vr = Decimal("50000.00")
        k = Decimal("0.1234")
        r = calcular_valor_reajuste(vr, k)
        assert r == Decimal("6170.00")

    def test_reajuste_truncation(self):
        """Test that adjustment value is truncated to cents."""
        # R = 0.0009 × 12345.67 = 11.11113 -> 11.11
        vr = Decimal("12345.67")
        k = Decimal("0.0009")
        r = calcular_valor_reajuste(vr, k)
        assert r == Decimal("11.11")

    def test_reajuste_zero_k(self):
        """Test adjustment when K factor is zero."""
        vr = Decimal("10000.00")
        k = Decimal("0.0000")
        r = calcular_valor_reajuste(vr, k)
        assert r == Decimal("0.00")

    def test_reajuste_negative_value(self):
        """Test that negative measurement value raises error."""
        with pytest.raises(ValueError, match="cannot be negative"):
            calcular_valor_reajuste(Decimal("-1000"), Decimal("0.1"))

    def test_reajuste_with_string_inputs(self):
        """Test that string inputs are converted properly."""
        r = calcular_valor_reajuste("10000.00", "0.0009")
        assert r == Decimal("9.00")


class TestCalcularValorTotal:
    """Test total value calculation."""

    def test_total_basic(self):
        """Test basic total calculation."""
        vr = Decimal("10000.00")
        r = Decimal("9.00")
        total = calcular_valor_total_atualizado(vr, r)
        assert total == Decimal("10009.00")

    def test_total_larger_values(self):
        """Test total with larger values."""
        vr = Decimal("50000.00")
        r = Decimal("6170.00")
        total = calcular_valor_total_atualizado(vr, r)
        assert total == Decimal("56170.00")


class TestValidarIntersticioLegal:
    """Test legal interval validation (365 days)."""

    def test_intersticio_valido(self):
        """Test valid interval (>= 365 days)."""
        data_base = date(2024, 1, 1)
        mes_reajuste = date(2025, 1, 1)  # Exactly 365 days

        valido, mensagem = validar_intersticio_legal(data_base, mes_reajuste)

        assert valido is True
        assert "cumprido" in mensagem.lower()

    def test_intersticio_valido_mais_de_365(self):
        """Test valid interval (> 365 days)."""
        data_base = date(2024, 1, 1)
        mes_reajuste = date(2025, 6, 1)  # More than 365 days

        valido, mensagem = validar_intersticio_legal(data_base, mes_reajuste)

        assert valido is True

    def test_intersticio_invalido(self):
        """Test invalid interval (< 365 days)."""
        data_base = date(2024, 1, 1)
        mes_reajuste = date(2024, 6, 1)  # Only ~150 days

        valido, mensagem = validar_intersticio_legal(data_base, mes_reajuste)

        assert valido is False
        assert "não cumprido" in mensagem.lower()

    def test_intersticio_exato_364_dias(self):
        """Test exactly 364 days (should be invalid)."""
        data_base = date(2023, 1, 1)
        mes_reajuste = date(2023, 12, 31)  # 364 days

        valido, mensagem = validar_intersticio_legal(data_base, mes_reajuste)

        assert valido is False


class TestCompleteWorkflow:
    """Test complete calculation workflow."""

    def test_workflow_example_1(self):
        """
        Complete workflow test with example values.

        Contract: I_0 = 105.4, dated 2024-01-01
        Measurement: Vr = 10,000.00, for month 2025-01-01 (I_i = 105.5)
        Expected: K = 0.0009, R = 9.00
        """
        # Given
        i0 = Decimal("105.4")
        ii = Decimal("105.5")
        vr = Decimal("10000.00")

        # When
        k = calcular_fator_k_truncado(i0, ii)
        r = calcular_valor_reajuste(vr, k)
        total = calcular_valor_total_atualizado(vr, r)

        # Then
        assert k == Decimal("0.0009")
        assert r == Decimal("9.00")
        assert total == Decimal("10009.00")

    def test_workflow_example_2(self):
        """
        Complete workflow test with larger adjustment.

        I_0 = 100.0, I_i = 110.5
        Vr = 1,000,000.00
        Expected: K = 0.1050, R = 105,000.00
        """
        # Given
        i0 = Decimal("100.0")
        ii = Decimal("110.5")
        vr = Decimal("1000000.00")

        # When
        k = calcular_fator_k_truncado(i0, ii)
        r = calcular_valor_reajuste(vr, k)
        total = calcular_valor_total_atualizado(vr, r)

        # Then
        assert k == Decimal("0.1050")
        assert r == Decimal("105000.00")
        assert total == Decimal("1105000.00")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
