"""
Dashboard page - System overview and status.
"""

import streamlit as st
from src.db.connection import get_db
from src.services.index_service import contar_indices, obter_indice_mais_recente
from src.services.contract_service import contar_contratos
from src.db.models import CalculoRealizado

st.title("Dashboard - Sistema de Reajuste SESP/PR")
st.markdown("---")

# Get database session
db = get_db()

# Metrics section
st.subheader("Estatísticas do Sistema")

col1, col2, col3 = st.columns(3)

with col1:
    total_indices = contar_indices(db)
    st.metric("Índices Cadastrados", total_indices)

with col2:
    total_contratos = contar_contratos(db)
    st.metric("Contratos Ativos", total_contratos)

with col3:
    total_calculos = db.query(CalculoRealizado).count()
    st.metric("Cálculos Realizados", total_calculos)

st.markdown("---")

# Status section
st.subheader("Status dos Índices")

# Get most recent index
indice_recente = obter_indice_mais_recente(db)

if indice_recente:
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"""
        **Último Índice Cadastrado**

        Data: {indice_recente.data_referencia.strftime('%B/%Y')}

        Valor: {indice_recente.valor}
        """)

    with col2:
        st.success("""
        **Sistema Operacional**

        O sistema está pronto para realizar cálculos de reajuste.

        Navegue até "Calcular Reajuste" para iniciar.
        """)
else:
    st.warning("""
    **Nenhum Índice Cadastrado**

    Para começar a usar o sistema, cadastre os índices INCC-DI na página
    "Gestão de Índices".
    """)

st.markdown("---")

# Information section
st.subheader("Sobre o Sistema")

with st.expander("Informações Legais"):
    st.markdown("""
    Este sistema realiza cálculos de reajustamento de contratos de obras públicas
    em conformidade com:

    - **Lei nº 14.133/2021** (Nova Lei de Licitações)
    - **Decreto Estadual nº 10.086/2022**

    **Índice utilizado:** INCC-DI (Índice Nacional de Custo da Construção -
    Disponibilidade Interna), publicado pela Fundação Getúlio Vargas (FGV).

    **Fórmulas aplicadas:**
    - Fator K: K = (I₁ / I₀) - 1
    - Reajuste: R = K × Vr

    **Regra de precisão:** O fator K é truncado (sem arredondamento) na quarta
    casa decimal, conforme cláusula contratual.
    """)

with st.expander("Como Usar o Sistema"):
    st.markdown("""
    **Passo 1: Cadastrar Índices**
    - Navegue até "Gestão de Índices"
    - Cadastre os valores do INCC-DI mensais

    **Passo 2: Cadastrar Contratos**
    - Navegue até "Gestão de Contratos"
    - Cadastre os contratos de obras
    - **Importante:** Informe corretamente a "Data Base do Orçamento"

    **Passo 3: Calcular Reajuste**
    - Navegue até "Calcular Reajuste"
    - Selecione o contrato
    - Informe o valor da medição e o mês de reajuste
    - Gere a Memória de Cálculo em PDF
    """)

# Close database session
db.close()
