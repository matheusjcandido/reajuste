"""
Service layer for managing economic indices (INCC-DI).

Provides CRUD operations for the indices_economicos table.
"""

from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.db.models import IndiceEconomico
from src.utils.decimal_utils import ensure_decimal


def criar_indice(
    db: Session,
    data_referencia: date,
    nome_indice: str,
    valor: Decimal
) -> IndiceEconomico:
    """
    Create a new economic index entry.

    Args:
        db: Database session
        data_referencia: Reference date (first day of month)
        nome_indice: Index name (default: "INCC-DI")
        valor: Index value

    Returns:
        IndiceEconomico: Created index record

    Raises:
        IntegrityError: If index for this date already exists
        ValueError: If valor is not positive
    """
    valor = ensure_decimal(valor)

    if valor <= 0:
        raise ValueError(f"Index value must be positive, got {valor}")

    indice = IndiceEconomico(
        data_referencia=data_referencia,
        nome_indice=nome_indice,
        valor=valor
    )

    try:
        db.add(indice)
        db.commit()
        db.refresh(indice)
        return indice
    except IntegrityError:
        db.rollback()
        raise ValueError(
            f"Index for date {data_referencia.strftime('%m/%Y')} already exists. "
            f"Use atualizar_indice() to modify it."
        )


def listar_indices(db: Session, limit: int = 100) -> list[IndiceEconomico]:
    """
    List all economic indices, ordered by date (most recent first).

    Args:
        db: Database session
        limit: Maximum number of records to return

    Returns:
        list[IndiceEconomico]: List of index records
    """
    return db.query(IndiceEconomico)\
        .order_by(IndiceEconomico.data_referencia.desc())\
        .limit(limit)\
        .all()


def buscar_indice_por_data(db: Session, data_referencia: date) -> IndiceEconomico | None:
    """
    Find index by reference date.

    Args:
        db: Database session
        data_referencia: Reference date to search

    Returns:
        IndiceEconomico or None: Index record if found, None otherwise
    """
    return db.query(IndiceEconomico)\
        .filter(IndiceEconomico.data_referencia == data_referencia)\
        .first()


def atualizar_indice(
    db: Session,
    data_referencia: date,
    novo_valor: Decimal
) -> IndiceEconomico:
    """
    Update existing index value.

    Args:
        db: Database session
        data_referencia: Reference date of index to update
        novo_valor: New index value

    Returns:
        IndiceEconomico: Updated index record

    Raises:
        ValueError: If index not found or novo_valor is not positive
    """
    novo_valor = ensure_decimal(novo_valor)

    if novo_valor <= 0:
        raise ValueError(f"Index value must be positive, got {novo_valor}")

    indice = buscar_indice_por_data(db, data_referencia)

    if not indice:
        raise ValueError(
            f"Index for date {data_referencia.strftime('%m/%Y')} not found"
        )

    indice.valor = novo_valor
    db.commit()
    db.refresh(indice)

    return indice


def deletar_indice(db: Session, data_referencia: date) -> bool:
    """
    Delete index by reference date.

    Args:
        db: Database session
        data_referencia: Reference date of index to delete

    Returns:
        bool: True if deleted, False if not found

    Note:
        This may fail if the index is referenced by contracts.
        Consider adding cascade rules or checks.
    """
    indice = buscar_indice_por_data(db, data_referencia)

    if not indice:
        return False

    db.delete(indice)
    db.commit()

    return True


def obter_indice_mais_recente(db: Session) -> IndiceEconomico | None:
    """
    Get the most recent index entry.

    Args:
        db: Database session

    Returns:
        IndiceEconomico or None: Most recent index or None if no indices exist
    """
    return db.query(IndiceEconomico)\
        .order_by(IndiceEconomico.data_referencia.desc())\
        .first()


def contar_indices(db: Session) -> int:
    """
    Count total number of indices in database.

    Args:
        db: Database session

    Returns:
        int: Total count of index records
    """
    return db.query(IndiceEconomico).count()
