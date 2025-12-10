"""
Service layer for managing contracts (contratos).

Provides CRUD operations for the contratos table.
"""

from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.db.models import Contrato
from src.utils.decimal_utils import ensure_decimal


def criar_contrato(
    db: Session,
    numero_contrato: str,
    objeto: str,
    empresa: str,
    data_base_orcamento: date,
    data_assinatura: date,
    valor_inicial: Decimal
) -> Contrato:
    """
    Create a new contract.

    Args:
        db: Database session
        numero_contrato: Unique contract number
        objeto: Contract description/object
        empresa: Company name
        data_base_orcamento: Budget date (CRITICAL: defines I_0)
        data_assinatura: Contract signature date
        valor_inicial: Initial contract value

    Returns:
        Contrato: Created contract record

    Raises:
        IntegrityError: If contract number already exists
        ValueError: If valor_inicial is not positive
    """
    valor_inicial = ensure_decimal(valor_inicial)

    if valor_inicial <= 0:
        raise ValueError(f"Initial contract value must be positive, got {valor_inicial}")

    if not numero_contrato.strip():
        raise ValueError("Contract number cannot be empty")

    if not empresa.strip():
        raise ValueError("Company name cannot be empty")

    contrato = Contrato(
        numero_contrato=numero_contrato.strip(),
        objeto=objeto.strip(),
        empresa=empresa.strip(),
        data_base_orcamento=data_base_orcamento,
        data_assinatura=data_assinatura,
        valor_inicial=valor_inicial
    )

    try:
        db.add(contrato)
        db.commit()
        db.refresh(contrato)
        return contrato
    except IntegrityError:
        db.rollback()
        raise ValueError(
            f"Contract number '{numero_contrato}' already exists. "
            f"Contract numbers must be unique."
        )


def listar_contratos(db: Session) -> list[Contrato]:
    """
    List all contracts, ordered by creation date (most recent first).

    Args:
        db: Database session

    Returns:
        list[Contrato]: List of contract records
    """
    return db.query(Contrato)\
        .order_by(Contrato.data_criacao.desc())\
        .all()


def buscar_contrato_por_numero(db: Session, numero_contrato: str) -> Contrato | None:
    """
    Find contract by contract number.

    Args:
        db: Database session
        numero_contrato: Contract number to search

    Returns:
        Contrato or None: Contract record if found, None otherwise
    """
    return db.query(Contrato)\
        .filter(Contrato.numero_contrato == numero_contrato.strip())\
        .first()


def buscar_contrato_por_id(db: Session, contrato_id: int) -> Contrato | None:
    """
    Find contract by ID.

    Args:
        db: Database session
        contrato_id: Contract ID to search

    Returns:
        Contrato or None: Contract record if found, None otherwise
    """
    return db.query(Contrato)\
        .filter(Contrato.id == contrato_id)\
        .first()


def atualizar_contrato(
    db: Session,
    contrato_id: int,
    numero_contrato: str = None,
    objeto: str = None,
    empresa: str = None,
    data_base_orcamento: date = None,
    data_assinatura: date = None,
    valor_inicial: Decimal = None
) -> Contrato:
    """
    Update existing contract.

    Only provided fields will be updated (partial update).

    Args:
        db: Database session
        contrato_id: Contract ID to update
        numero_contrato: New contract number (optional)
        objeto: New description (optional)
        empresa: New company name (optional)
        data_base_orcamento: New budget date (optional)
        data_assinatura: New signature date (optional)
        valor_inicial: New initial value (optional)

    Returns:
        Contrato: Updated contract record

    Raises:
        ValueError: If contract not found or invalid values provided
    """
    contrato = buscar_contrato_por_id(db, contrato_id)

    if not contrato:
        raise ValueError(f"Contract with ID {contrato_id} not found")

    # Update only provided fields
    if numero_contrato is not None:
        if not numero_contrato.strip():
            raise ValueError("Contract number cannot be empty")
        contrato.numero_contrato = numero_contrato.strip()

    if objeto is not None:
        contrato.objeto = objeto.strip()

    if empresa is not None:
        if not empresa.strip():
            raise ValueError("Company name cannot be empty")
        contrato.empresa = empresa.strip()

    if data_base_orcamento is not None:
        contrato.data_base_orcamento = data_base_orcamento

    if data_assinatura is not None:
        contrato.data_assinatura = data_assinatura

    if valor_inicial is not None:
        valor_inicial = ensure_decimal(valor_inicial)
        if valor_inicial <= 0:
            raise ValueError(f"Initial contract value must be positive, got {valor_inicial}")
        contrato.valor_inicial = valor_inicial

    try:
        db.commit()
        db.refresh(contrato)
        return contrato
    except IntegrityError:
        db.rollback()
        raise ValueError(
            f"Cannot update: contract number '{numero_contrato}' already exists"
        )


def deletar_contrato(db: Session, contrato_id: int) -> bool:
    """
    Delete contract by ID.

    Args:
        db: Database session
        contrato_id: Contract ID to delete

    Returns:
        bool: True if deleted, False if not found

    Note:
        This may fail if the contract has associated calculations.
        Consider adding cascade rules or checks.
    """
    contrato = buscar_contrato_por_id(db, contrato_id)

    if not contrato:
        return False

    db.delete(contrato)
    db.commit()

    return True


def contar_contratos(db: Session) -> int:
    """
    Count total number of contracts in database.

    Args:
        db: Database session

    Returns:
        int: Total count of contract records
    """
    return db.query(Contrato).count()
