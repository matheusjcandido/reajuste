"""
Database models for the SESP salary adjustment calculation system.

This module defines SQLAlchemy ORM models with a custom DecimalType to preserve
precision in SQLite (which doesn't have native DECIMAL support).
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, TypeDecorator, Text
from sqlalchemy.ext.declarative import declarative_base
from decimal import Decimal, InvalidOperation
import datetime

Base = declarative_base()


class DecimalType(TypeDecorator):
    """
    Custom SQLAlchemy TypeDecorator for Decimal values.
    Stores Decimal as TEXT in SQLite to preserve precision.

    This solves the issue where SQLite's NUMERIC type converts to float,
    losing precision required for financial calculations.

    Critical for compliance with truncation rules (4 decimal places without rounding).
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert Python Decimal to string for database storage."""
        if value is None:
            return None
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, (int, float)):
            return str(Decimal(str(value)))
        raise ValueError(f"Expected Decimal, got {type(value)}")

    def process_result_value(self, value, dialect):
        """Convert stored TEXT back to Python Decimal."""
        if value is None:
            return None
        try:
            return Decimal(value)
        except InvalidOperation:
            raise ValueError(f"Could not convert '{value}' to Decimal")


class IndiceEconomico(Base):
    """
    Economic index table - stores INCC-DI historical values.

    Attributes:
        data_referencia: Reference date (first day of month), PRIMARY KEY
        nome_indice: Index name (default: "INCC-DI")
        valor: Index value with full decimal precision
    """
    __tablename__ = "indices_economicos"

    data_referencia = Column(Date, primary_key=True)
    nome_indice = Column(String(50), nullable=False, default="INCC-DI")
    valor = Column(DecimalType, nullable=False)

    def __repr__(self):
        return f"<IndiceEconomico(data={self.data_referencia}, valor={self.valor})>"


class Contrato(Base):
    """
    Contract table - stores public works contract information.

    Attributes:
        id: Primary key
        numero_contrato: Unique contract number
        objeto: Contract description/object
        empresa: Company name
        data_base_orcamento: CRITICAL - Budget date (defines I_0 base index)
        data_assinatura: Contract signature date
        valor_inicial: Initial contract value
        data_criacao: Record creation timestamp
    """
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True)
    numero_contrato = Column(String(50), unique=True, nullable=False)
    objeto = Column(Text, nullable=False)
    empresa = Column(String(100), nullable=False)
    data_base_orcamento = Column(Date, nullable=False)  # CRITICAL: Defines I_0
    data_assinatura = Column(Date, nullable=False)
    valor_inicial = Column(DecimalType, nullable=False)
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Contrato(numero={self.numero_contrato}, empresa={self.empresa})>"


class CalculoRealizado(Base):
    """
    Calculation audit log - stores every adjustment calculation performed.

    This table provides complete traceability for legal compliance,
    recording all parameters used in each calculation.

    Attributes:
        id: Primary key
        contrato_id: Foreign key reference to contracts table
        data_calculo: Timestamp when calculation was performed
        mes_indice_base: Month used for base index I_0
        valor_indice_base: Value of I_0 used
        mes_indice_reajuste: Month used for adjustment index I_i
        valor_indice_reajuste: Value of I_i used
        fator_k_aplicado: K factor applied (truncated to 4 decimals)
        valor_original_medicao: Original measurement value (Vr)
        valor_reajuste: Calculated adjustment value (R)
    """
    __tablename__ = "calculos_realizados"

    id = Column(Integer, primary_key=True)
    contrato_id = Column(Integer, nullable=False)
    data_calculo = Column(DateTime, default=datetime.datetime.utcnow)
    mes_indice_base = Column(Date, nullable=False)
    valor_indice_base = Column(DecimalType, nullable=False)
    mes_indice_reajuste = Column(Date, nullable=False)
    valor_indice_reajuste = Column(DecimalType, nullable=False)
    fator_k_aplicado = Column(DecimalType, nullable=False)
    valor_original_medicao = Column(DecimalType, nullable=False)
    valor_reajuste = Column(DecimalType, nullable=False)

    def __repr__(self):
        return f"<CalculoRealizado(id={self.id}, contrato_id={self.contrato_id}, K={self.fator_k_aplicado})>"
