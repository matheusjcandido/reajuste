"""
Index management page - CRUD operations for economic indices (INCC-DI).
"""

import streamlit as st
from datetime import date
from decimal import Decimal
from src.db.connection import get_db
from src.services.index_service import (
    criar_indice,
    listar_indices,
    deletar_indice,
    atualizar_indice
)
import pandas as pd

st.title("Gestão de Índices Econômicos")
st.markdown("Cadastro e gerenciamento dos valores do INCC-DI (Índice Nacional de Custo da Construção)")
st.markdown("---")

# Get database session
db = get_db()

# Form to add new index
st.subheader("Cadastrar Novo Índice")

with st.form("novo_indice"):
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        data_referencia = st.date_input(
            "Data de Referência",
            value=date.today().replace(day=1),
            help="Primeiro dia do mês de referência do índice"
        )

    with col2:
        valor_str = st.text_input(
            "Valor do Índice",
            placeholder="Ex: 105.4560",
            help="Use ponto (.) como separador decimal"
        )

    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        submitted = st.form_submit_button("➕ Adicionar", use_container_width=True)

    if submitted:
        try:
            # Validate input
            if not valor_str:
                st.error("Por favor, informe o valor do índice.")
            else:
                # Convert to Decimal
                valor = Decimal(valor_str.replace(",", "."))

                # Create index
                criar_indice(db, data_referencia, "INCC-DI", valor)

                st.success(f"✅ Índice de {data_referencia.strftime('%m/%Y')} cadastrado com sucesso!")
                st.rerun()

        except ValueError as e:
            st.error(f"❌ Erro: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erro ao cadastrar índice: {str(e)}")

st.markdown("---")

# Display historical indices
st.subheader("Histórico de Índices")

try:
    indices = listar_indices(db, limit=100)

    if indices:
        # Convert to DataFrame for better display
        df_data = []
        for idx in indices:
            df_data.append({
                "Data": idx.data_referencia.strftime("%m/%Y"),
                "Índice": idx.nome_indice,
                "Valor": str(idx.valor),
                "Data Completa": idx.data_referencia  # Hidden column for operations
            })

        df = pd.DataFrame(df_data)

        # Display configuration
        st.dataframe(
            df[["Data", "Índice", "Valor"]],
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Total: {len(indices)} índice(s) cadastrado(s)")

        # Delete functionality
        st.markdown("---")
        st.subheader("Excluir Índice")

        with st.form("excluir_indice"):
            col1, col2 = st.columns([3, 1])

            with col1:
                datas_disponiveis = [idx.data_referencia for idx in indices]
                datas_formatadas = [d.strftime("%m/%Y") for d in datas_disponiveis]

                idx_selecionado = st.selectbox(
                    "Selecione o índice a excluir",
                    range(len(datas_formatadas)),
                    format_func=lambda i: datas_formatadas[i]
                )

            with col2:
                st.write("")
                st.write("")
                excluir = st.form_submit_button("🗑️ Excluir", use_container_width=True)

            if excluir:
                data_excluir = datas_disponiveis[idx_selecionado]
                try:
                    if deletar_indice(db, data_excluir):
                        st.success(f"✅ Índice de {data_excluir.strftime('%m/%Y')} excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Índice não encontrado.")
                except Exception as e:
                    st.error(f"❌ Erro ao excluir índice: {str(e)}")

    else:
        st.info("📊 Nenhum índice cadastrado ainda. Use o formulário acima para adicionar o primeiro índice.")

except Exception as e:
    st.error(f"❌ Erro ao carregar índices: {str(e)}")

finally:
    db.close()

# Help section
with st.expander("ℹ️ Ajuda - Como cadastrar índices"):
    st.markdown("""
    **Onde obter os valores do INCC-DI?**

    Os valores do INCC-DI são publicados mensalmente pela Fundação Getúlio Vargas (FGV).
    Acesse: [Portal FGV IBRE](https://portalibre.fgv.br/)

    **Formato da data:**
    - Use sempre o primeiro dia do mês (ex: 01/01/2025 para Janeiro/2025)
    - Isso facilita a busca e organização dos índices

    **Formato do valor:**
    - Use ponto (.) como separador decimal
    - Mantenha a precisão original do índice (geralmente 4 casas decimais)
    - Exemplo: 105.4560

    **Atenção:**
    - Não é possível cadastrar dois índices para a mesma data
    - Ao excluir um índice, verifique se não há contratos ou cálculos que dependem dele
    """)
