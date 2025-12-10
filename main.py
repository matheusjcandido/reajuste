"""
SESP/PR - Sistema de Cálculo de Reajuste de Obras

Main entry point for the Streamlit application.
Sets up page configuration and navigation.
"""

import streamlit as st

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="SESP Reajuste",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.db.connection import init_db
from src.services.seeding import seed_indices, seed_contracts

# Initialize database on first run
init_db()
seed_indices()
seed_contracts()

# Define navigation pages (ordem invertida para priorizar cálculo)
pg = st.navigation({
    "Cálculo": [
        st.Page("views/calculate.py", title="Calcular Reajuste", icon="🧮"),
    ],
    "Gestão de Dados": [
        st.Page("views/contracts.py", title="Gestão de Contratos", icon="📋"),
        st.Page("views/indices.py", title="Gestão de Índices", icon="📈"),
    ],
    "Administração": [
        st.Page("views/dashboard.py", title="Dashboard", icon="📊"),
    ],
})

# Run the navigation
pg.run()
