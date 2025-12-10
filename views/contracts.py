"""
Contract management page - CRUD operations for contracts.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from src.db.connection import get_db
from src.services.contract_service import (
    criar_contrato,
    listar_contratos,
    deletar_contrato
)
from src.services.index_service import buscar_indice_por_data
from src.utils.decimal_utils import format_brazilian_currency
import pandas as pd

st.title("Gestão de Contratos")
st.markdown("Cadastro e gerenciamento de contratos de obras públicas")
st.markdown("---")

# Get database session
db = get_db()

# Form to add new contract
st.subheader("Cadastrar Novo Contrato")

with st.form("novo_contrato"):
    col1, col2 = st.columns(2)

    with col1:
        numero_contrato = st.text_input(
            "Número do Contrato*",
            placeholder="Ex: 001/2025",
            help="Número único que identifica o contrato"
        )

        empresa = st.text_input(
            "Empresa Contratada*",
            placeholder="Ex: Construtora ABC Ltda",
            help="Nome da empresa que executará a obra"
        )

        data_assinatura = st.date_input(
            "Data de Assinatura*",
            value=date.today(),
            help="Data em que o contrato foi assinado"
        )

    with col2:
        objeto = st.text_area(
            "Objeto do Contrato*",
            placeholder="Ex: Construção de escola municipal",
            help="Descrição do objeto/finalidade do contrato",
            height=100
        )

        data_base_orcamento = st.date_input(
            "Data Base do Orçamento* ⚠️",
            value=date.today().replace(day=1),
            help="CRÍTICO: Esta data define o índice I₀ usado nos cálculos de reajuste"
        )

        valor_inicial_str = st.text_input(
            "Valor Inicial (R$)*",
            placeholder="Ex: 1000000.00",
            help="Valor inicial do contrato em Reais"
        )

    # Warning about data_base_orcamento
    st.warning(
        "⚠️ **ATENÇÃO:** A 'Data Base do Orçamento' é o campo mais importante! "
        "Ela define o índice I₀ que será usado em todos os cálculos de reajuste deste contrato. "
        "Verifique se esta data está correta antes de cadastrar."
    )

    submitted = st.form_submit_button("➕ Cadastrar Contrato", use_container_width=True)

    if submitted:
        try:
            # Validate inputs
            if not numero_contrato or not empresa or not objeto or not valor_inicial_str:
                st.error("❌ Por favor, preencha todos os campos obrigatórios (*)")
            else:
                # Convert valor_inicial to Decimal
                valor_inicial = Decimal(valor_inicial_str.replace(",", "."))

                # Check if there's an index for the base date
                indice_base = buscar_indice_por_data(db, data_base_orcamento)
                if not indice_base:
                    st.error(
                        f"❌ Não há índice cadastrado para a data base do orçamento "
                        f"({data_base_orcamento.strftime('%m/%Y')}). "
                        f"Cadastre o índice primeiro na página 'Gestão de Índices'."
                    )
                else:
                    # Create contract
                    criar_contrato(
                        db,
                        numero_contrato=numero_contrato,
                        objeto=objeto,
                        empresa=empresa,
                        data_base_orcamento=data_base_orcamento,
                        data_assinatura=data_assinatura,
                        valor_inicial=valor_inicial
                    )

                    st.success(f"✅ Contrato {numero_contrato} cadastrado com sucesso!")
                    st.info(
                        f"📊 Índice base (I₀): {indice_base.valor} "
                        f"({data_base_orcamento.strftime('%m/%Y')})"
                    )
                    st.rerun()

        except ValueError as e:
            st.error(f"❌ Erro: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erro ao cadastrar contrato: {str(e)}")

st.markdown("---")

# Display contracts list
st.subheader("Contratos Cadastrados")

try:
    contratos = listar_contratos(db)

    if contratos:
        # Display contracts in expandable cards
        for contrato in contratos:
            # Get base index
            indice_base = buscar_indice_por_data(db, contrato.data_base_orcamento)

            with st.expander(f"📋 {contrato.numero_contrato} - {contrato.empresa}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    **Número:** {contrato.numero_contrato}

                    **Empresa:** {contrato.empresa}

                    **Objeto:** {contrato.objeto}
                    """)

                with col2:
                    st.markdown(f"""
                    **Data de Assinatura:** {contrato.data_assinatura.strftime('%d/%m/%Y')}

                    **Data Base do Orçamento:** {contrato.data_base_orcamento.strftime('%d/%m/%Y')}

                    **Índice Base (I₀):** {indice_base.valor if indice_base else '⚠️ Não encontrado'}

                    **Valor Inicial:** {format_brazilian_currency(contrato.valor_inicial)}
                    """)

                # Delete button
                if st.button(f"🗑️ Excluir contrato {contrato.numero_contrato}", key=f"del_{contrato.id}"):
                    try:
                        if deletar_contrato(db, contrato.id):
                            st.success(f"✅ Contrato {contrato.numero_contrato} excluído!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao excluir contrato.")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")

        st.caption(f"Total: {len(contratos)} contrato(s) cadastrado(s)")

    else:
        st.info("📋 Nenhum contrato cadastrado ainda. Use o formulário acima para adicionar o primeiro contrato.")

except Exception as e:
    st.error(f"❌ Erro ao carregar contratos: {str(e)}")

finally:
    db.close()

# Help section
with st.expander("ℹ️ Ajuda - Como cadastrar contratos"):
    st.markdown("""
    **Campos obrigatórios:**

    - **Número do Contrato:** Identificador único (ex: 001/2025)
    - **Empresa Contratada:** Nome completo da empresa
    - **Objeto:** Descrição clara do que será executado
    - **Data de Assinatura:** Quando o contrato foi assinado
    - **Data Base do Orçamento:** ⚠️ **CRÍTICO** - Define o índice I₀
    - **Valor Inicial:** Valor total do contrato em Reais

    **Sobre a Data Base do Orçamento:**

    Esta é a data mais importante do contrato! Ela define qual índice (I₀) será usado
    como base para todos os cálculos de reajuste.

    Normalmente, esta data é:
    - A data em que o orçamento foi elaborado
    - **NÃO** é a data de assinatura do contrato
    - Geralmente é anterior à data de assinatura

    Verifique o edital ou minuta contratual para confirmar qual é a data correta.

    **Importante:**
    - Antes de cadastrar, certifique-se de que o índice para a data base já está cadastrado
    - O sistema verificará automaticamente e alertará se o índice não existir
    """)
