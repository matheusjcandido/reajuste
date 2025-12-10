"""
Service for seeding the database with historical data.
"""

import pandas as pd
from sqlalchemy.orm import Session
from src.db.connection import get_db
from src.db.models import IndiceEconomico
from src.utils.decimal_utils import ensure_decimal
from datetime import datetime
import os

EXCEL_FILE = "2bec-serie-historica-incc-di-fgv.xlsx"

def seed_indices():
    """
    Reads the historical INCC-DI Excel file and populates the database.
    Skips records that already exist.
    """
    if not os.path.exists(EXCEL_FILE):
        print(f"Warning: Seeding file '{EXCEL_FILE}' not found.")
        return

    print("Starting data seeding...")
    
    try:
        # Read Excel file
        # The file has a header structure where the actual data starts later
        # Based on previous inspection:
        # Row 2 (index 2) contains the first data: 1994-08-01
        # Columns: 'Unnamed: 0' (Date) and 'Unnamed: 1' (Value) - inferred from previous print
        
        # Let's read with header=2 to get the correct columns
        df = pd.read_excel(EXCEL_FILE, header=2)
        
        # Rename columns for clarity (assuming first column is date, second is value)
        # The previous print showed:
        # 0: 1994-08-01 (Date)
        # 1: 100 (Value)
        
        # We need to be careful with column names. Let's use iloc to be safe.
        
        db = get_db()
        count = 0
        
        for index, row in df.iterrows():
            try:
                data_raw = row.iloc[0]
                valor_raw = row.iloc[1]
                
                # Check if valid date
                if pd.isna(data_raw) or not isinstance(data_raw, datetime):
                    continue
                    
                # Check if valid value
                if pd.isna(valor_raw):
                    continue
                
                data_referencia = data_raw.date()
                
                # Handle float values from Excel by converting to string first
                if isinstance(valor_raw, float):
                    valor = ensure_decimal(str(valor_raw))
                else:
                    valor = ensure_decimal(valor_raw)
                
                # Check if already exists
                existing = db.query(IndiceEconomico).filter(
                    IndiceEconomico.data_referencia == data_referencia,
                    IndiceEconomico.nome_indice == "INCC-DI"
                ).first()
                
                if not existing:
                    novo_indice = IndiceEconomico(
                        data_referencia=data_referencia,
                        nome_indice="INCC-DI",
                        valor=valor
                    )
                    db.add(novo_indice)
                    count += 1
            
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue
        
        db.commit()
        db.close()
        
        if count > 0:
            print(f"Seeding completed: {count} new indices added.")
        else:
            print("Seeding completed: No new indices found.")
            
    except Exception as e:
        print(f"Error during seeding: {e}")


def seed_contracts():
    """
    Seeds an example contract if it doesn't exist.
    """
    from src.db.models import Contrato
    from decimal import Decimal
    from datetime import date

    db = get_db()

    try:
        # Check if example contract exists
        numero_contrato = "001/2023-SESP"
        existing = db.query(Contrato).filter(Contrato.numero_contrato == numero_contrato).first()

        if not existing:
            print(f"Seeding example contract: {numero_contrato}")

            contrato = Contrato(
                numero_contrato=numero_contrato,
                objeto="Construção da Nova Sede do 1º Batalhão de Polícia Militar",
                empresa="Construtora Exemplo Ltda",
                data_base_orcamento=date(2022, 11, 1),  # Proposta de preços: 03/11/2022
                data_assinatura=date(2023, 2, 27),
                valor_inicial=Decimal("9769003.69")
            )

            db.add(contrato)
            db.commit()
            print("Example contract seeded successfully.")
        else:
            print("Example contract already exists.")

    except Exception as e:
        print(f"Error seeding contract: {e}")
    finally:
        db.close()
