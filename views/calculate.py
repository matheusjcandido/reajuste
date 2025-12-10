"""
Calculation page - Main interface for salary adjustment calculations.
"""

import streamlit as st
from datetime import date
from decimal import Decimal
import re
from src.db.connection import get_db
from src.services.contract_service import listar_contratos, buscar_contrato_por_id
from src.services.index_service import buscar_indice_por_data
from src.services.calculation import (
    calcular_fator_k_truncado,
    calcular_valor_reajuste,
    calcular_valor_total_atualizado,
    salvar_calculo,
    validar_intersticio_legal
)
from src.services.pdf_service import gerar_pdf_memoria_calculo
from src.utils.decimal_utils import format_brazilian_currency
from src.db.models import CalculoRealizado


def format_currency_input(value_str: str) -> str:
    """
    Formata entrada de valor monetário em tempo real.
    Remove caracteres não numéricos e formata como R$ 10.000,00
    """
    if not value_str:
        return ""

    # Remove tudo exceto dígitos
    digits_only = re.sub(r'[^\d]', '', value_str)

    if not digits_only:
        return ""

    # Remove leading zeros but keep at least one digit if needed (handled by zfill later)
    digits_only = digits_only.lstrip('0')
    
    if not digits_only:
        return "R$ 0,00"

    # Pad with zeros to ensure at least 3 digits (e.g. "5" -> "005")
    if len(digits_only) < 3:
        digits_only = digits_only.zfill(3)

    # Separate integer and decimal parts
    integer_part = digits_only[:-2]
    decimal_part = digits_only[-2:]

    # Add thousand separators
    integer_with_separators = f"{int(integer_part):,}".replace(",", ".")

    return f"R$ {integer_with_separators},{decimal_part}"


def parse_brazilian_currency(value_str: str) -> Decimal:
    """
    Converte string em formato brasileiro (R$ 10.000,00) para Decimal.
    """
    if not value_str:
        raise ValueError("Valor não pode ser vazio")

    # Remove "R$", espaços, pontos (separador de milhar)
    clean_str = value_str.replace("R$", "").replace(" ", "").replace(".", "")

    # Substitui vírgula por ponto (separador decimal)
    clean_str = clean_str.replace(",", ".")

    try:
        return Decimal(clean_str)
    except:
        raise ValueError(f"Formato de valor inválido: {value_str}")

st.title("Calcular Reajuste")
st.markdown("Sistema de cálculo de reajustamento conforme Lei 14.133/2021")
st.markdown("---")

# Get database session
db = get_db()

# Step 1: Select contract
st.subheader("1️⃣ Selecionar Contrato")

contratos = listar_contratos(db)

if not contratos:
    st.warning(
        "⚠️ Nenhum contrato cadastrado. "
        "Por favor, cadastre um contrato na página 'Gestão de Contratos' primeiro."
    )
    db.close()
    st.stop()

# Create contract selection
contrato_opcoes = {f"{c.numero_contrato} - {c.empresa}": c.id for c in contratos}
contrato_selecionado_str = st.selectbox(
    "Selecione o contrato",
    options=list(contrato_opcoes.keys()),
    help="Escolha o contrato para o qual deseja calcular o reajuste"
)

contrato_id = contrato_opcoes[contrato_selecionado_str]
contrato = buscar_contrato_por_id(db, contrato_id)

st.markdown("---")

# Step 2: Display contract information
st.subheader("2️⃣ Informações do Contrato")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Número do Contrato", contrato.numero_contrato)
    st.metric("Empresa", contrato.empresa)

with col2:
    st.metric("Data de Assinatura", contrato.data_assinatura.strftime("%d/%m/%Y"))
    st.metric("Valor Inicial", format_brazilian_currency(contrato.valor_inicial))

with col3:
    st.metric(
        "Data Base do Orçamento",
        contrato.data_base_orcamento.strftime("%m/%Y"),
        help="Esta data define o índice I₀"
    )

    # Get base index
    indice_base = buscar_indice_por_data(db, contrato.data_base_orcamento)

    if indice_base:
        st.metric("Índice Base (I₀)", str(indice_base.valor))
    else:
        st.error("⚠️ Índice I₀ não encontrado!")
        st.stop()

st.info(f"📋 **Objeto:** {contrato.objeto}")

st.markdown("---")

# Step 3: Input measurement value and adjustment months
st.subheader("3️⃣ Dados do Reajuste")

# Initialize session state for currency input and multiple adjustments
if "valor_input" not in st.session_state:
    st.session_state.valor_input = ""

if "num_reajustes" not in st.session_state:
    st.session_state.num_reajustes = 1

def atualizar_formatacao():
    """Callback para formatar o valor quando o usuário aperta Enter ou sai do campo"""
    st.session_state.valor_input = format_currency_input(st.session_state.valor_input)

# Value input
valor_medicao_str = st.text_input(
    "Valor a ser reajustado*",
    key="valor_input",
    on_change=atualizar_formatacao,
    placeholder="Digite o valor (ex: 100000)",
    help="Digite apenas números. O valor será formatado automaticamente como R$ 10.000,00"
)

if valor_medicao_str:
    st.caption(f"💰 Valor formatado: **{valor_medicao_str}**")

st.markdown("---")

# Multiple adjustment periods
st.markdown("**Períodos de Reajuste**")
st.caption("Para contratos com mais de 2 anos, adicione múltiplos períodos de reajuste.")

col_add, col_remove = st.columns([1, 1])
with col_add:
    if st.button("➕ Adicionar período", use_container_width=True):
        st.session_state.num_reajustes += 1
        st.rerun()

with col_remove:
    if st.session_state.num_reajustes > 1:
        if st.button("➖ Remover período", use_container_width=True):
            st.session_state.num_reajustes -= 1
            st.rerun()

# Collect adjustment periods
meses_reajuste = []
for i in range(st.session_state.num_reajustes):
    col1, col2 = st.columns([2, 1])
    with col1:
        mes = st.date_input(
            f"Mês de Referência do Reajuste {i + 1}*",
            value=date.today().replace(day=1),
            help=f"Mês para o {i + 1}º período de reajuste",
            format="DD/MM/YYYY",
            key=f"mes_reajuste_{i}"
        )
        meses_reajuste.append(mes)
    with col2:
        if i == 0:
            st.caption("📅 Primeiro reajuste")
        else:
            st.caption(f"📅 {i + 1}º reajuste")

st.markdown("---")

# Step 4: Calculate
if st.button("🧮 Calcular Reajuste", type="primary", use_container_width=True):
    try:
        # Validate inputs
        if not valor_medicao_str:
            st.error("❌ Por favor, informe o valor a ser reajustado.")
            st.stop()

        # Parse Brazilian currency format to Decimal
        valor_medicao = parse_brazilian_currency(valor_medicao_str)

        if valor_medicao <= 0:
            st.error("❌ O valor a ser reajustado deve ser maior que zero.")
            st.stop()

        # Process all adjustment periods
        resultados = []
        valor_reajuste_total = Decimal('0')
        tem_erro = False

        for i, mes_reajuste in enumerate(meses_reajuste):
            # Normalize date to first day of month for index lookup
            mes_reajuste_normalizado = mes_reajuste.replace(day=1)

            # Validate legal interval (365 days) - only for first period from base date
            if i == 0:
                intervalo_valido, mensagem_intervalo = validar_intersticio_legal(
                    contrato.data_base_orcamento,
                    mes_reajuste
                )
                if not intervalo_valido:
                    st.error(f"❌ Período {i + 1}: {mensagem_intervalo}")
                    tem_erro = True
                    continue

            # Get adjustment index (I_i)
            indice_reajuste = buscar_indice_por_data(db, mes_reajuste_normalizado)

            if not indice_reajuste:
                st.error(
                    f"❌ Período {i + 1}: Índice para o mês {mes_reajuste_normalizado.strftime('%m/%Y')} não encontrado. "
                    f"Por favor, cadastre o índice na página 'Gestão de Índices'."
                )
                tem_erro = True
                continue

            # Calculate K factor
            fator_k = calcular_fator_k_truncado(indice_base.valor, indice_reajuste.valor)

            # Calculate adjustment value
            valor_reajuste = calcular_valor_reajuste(valor_medicao, fator_k)

            # Store result
            resultados.append({
                'periodo': i + 1,
                'mes_reajuste': mes_reajuste_normalizado,
                'indice_reajuste': indice_reajuste,
                'fator_k': fator_k,
                'valor_reajuste': valor_reajuste
            })

            valor_reajuste_total += valor_reajuste

        if tem_erro and not resultados:
            st.stop()

        # Calculate total updated value
        valor_total = calcular_valor_total_atualizado(valor_medicao, valor_reajuste_total)

        # Display results
        st.markdown("---")
        st.subheader("4️⃣ Resultado do Cálculo")

        # Show results for each period
        for resultado in resultados:
            periodo_label = f"Período {resultado['periodo']}" if len(resultados) > 1 else "Reajuste"
            with st.expander(f"📊 {periodo_label} - {resultado['mes_reajuste'].strftime('%m/%Y')}", expanded=True):
                st.markdown(f"""
                **Fórmula do Fator K:**

                K = (I₁ / I₀) - 1

                K = ({resultado['indice_reajuste'].valor} / {indice_base.valor}) - 1

                K = {resultado['indice_reajuste'].valor / indice_base.valor} - 1

                K = {(resultado['indice_reajuste'].valor / indice_base.valor) - Decimal('1')}

                **K (truncado à 4ª casa decimal) = {resultado['fator_k']}**

                ---

                **Fórmula do Reajuste:**

                R = K × Vr

                R = {resultado['fator_k']} × {format_brazilian_currency(valor_medicao)}

                **R = {format_brazilian_currency(resultado['valor_reajuste'])}**
                """)

        # Summary metrics
        st.markdown("### Resumo")

        if len(resultados) > 1:
            # Multiple periods - show summary table
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Valor Original", format_brazilian_currency(valor_medicao))

            with col2:
                st.metric("Reajuste Total", format_brazilian_currency(valor_reajuste_total))

            with col3:
                st.metric(
                    "Valor Total Atualizado",
                    format_brazilian_currency(valor_total),
                    delta=format_brazilian_currency(valor_reajuste_total)
                )

            # Detailed breakdown
            st.markdown("**Detalhamento por Período:**")
            for resultado in resultados:
                st.write(
                    f"- Período {resultado['periodo']} ({resultado['mes_reajuste'].strftime('%m/%Y')}): "
                    f"K = {resultado['fator_k']} → R = {format_brazilian_currency(resultado['valor_reajuste'])}"
                )
        else:
            # Single period
            resultado = resultados[0]
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Fator K", f"{resultado['fator_k']}")

            with col2:
                st.metric("Valor Original", format_brazilian_currency(valor_medicao))

            with col3:
                st.metric("Valor do Reajuste", format_brazilian_currency(resultado['valor_reajuste']))

            with col4:
                st.metric(
                    "Valor Total Atualizado",
                    format_brazilian_currency(valor_total),
                    delta=format_brazilian_currency(resultado['valor_reajuste'])
                )

        # Save calculation and generate PDF
        st.markdown("---")
        st.subheader("5️⃣ Memória de Cálculo")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Salvar Cálculo(s) no Histórico", use_container_width=True):
                try:
                    ids_salvos = []
                    for resultado in resultados:
                        calculo_salvo = salvar_calculo(
                            db,
                            contrato_id=contrato.id,
                            mes_indice_base=contrato.data_base_orcamento,
                            valor_indice_base=indice_base.valor,
                            mes_indice_reajuste=resultado['mes_reajuste'],
                            valor_indice_reajuste=resultado['indice_reajuste'].valor,
                            fator_k_aplicado=resultado['fator_k'],
                            valor_original_medicao=valor_medicao,
                            valor_reajuste=resultado['valor_reajuste']
                        )
                        ids_salvos.append(calculo_salvo.id)

                    if len(ids_salvos) == 1:
                        st.success(f"✅ Cálculo salvo com ID #{ids_salvos[0]}")
                    else:
                        st.success(f"✅ {len(ids_salvos)} cálculos salvos (IDs: {', '.join(map(str, ids_salvos))})")

                except Exception as e:
                    st.error(f"❌ Erro ao salvar cálculo: {str(e)}")

        with col2:
            # Generate PDF for the first/main calculation
            try:
                resultado_principal = resultados[0]
                pdf_bytes = gerar_pdf_memoria_calculo(
                    numero_contrato=contrato.numero_contrato,
                    empresa=contrato.empresa,
                    objeto=contrato.objeto,
                    data_base=contrato.data_base_orcamento,
                    data_assinatura=contrato.data_assinatura,
                    indice_base=indice_base.valor,
                    mes_reajuste=resultado_principal['mes_reajuste'],
                    indice_reajuste=resultado_principal['indice_reajuste'].valor,
                    fator_k=resultado_principal['fator_k'],
                    valor_medicao=valor_medicao,
                    valor_reajuste=resultado_principal['valor_reajuste'],
                    valor_total=valor_medicao + resultado_principal['valor_reajuste']
                )

                st.download_button(
                    label="📄 Baixar Memória de Cálculo (PDF)",
                    data=pdf_bytes,
                    file_name=f"memoria_calculo_{contrato.numero_contrato.replace('/', '_')}_{resultado_principal['mes_reajuste'].strftime('%Y%m')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ Erro ao gerar PDF: {str(e)}")

    except ValueError as e:
        st.error(f"❌ Erro: {str(e)}")
    except Exception as e:
        st.error(f"❌ Erro ao calcular reajuste: {str(e)}")

# Display calculation history
st.markdown("---")
st.subheader("📜 Histórico de Cálculos deste Contrato")

calculos = db.query(CalculoRealizado)\
    .filter(CalculoRealizado.contrato_id == contrato.id)\
    .order_by(CalculoRealizado.data_calculo.desc())\
    .limit(10)\
    .all()

if calculos:
    for calculo in calculos:
        with st.expander(
            f"Cálculo #{calculo.id} - {calculo.mes_indice_reajuste.strftime('%m/%Y')} - "
            f"{calculo.data_calculo.strftime('%d/%m/%Y %H:%M')}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                **Índices Utilizados:**
                - I₀: {calculo.valor_indice_base} ({calculo.mes_indice_base.strftime('%m/%Y')})
                - I₁: {calculo.valor_indice_reajuste} ({calculo.mes_indice_reajuste.strftime('%m/%Y')})

                **Fator K:** {calculo.fator_k_aplicado}
                """)

            with col2:
                st.markdown(f"""
                **Valores:**
                - Original: {format_brazilian_currency(calculo.valor_original_medicao)}
                - Reajuste: {format_brazilian_currency(calculo.valor_reajuste)}
                - Total: {format_brazilian_currency(calculo.valor_original_medicao + calculo.valor_reajuste)}
                """)
else:
    st.info("Nenhum cálculo realizado ainda para este contrato.")

# Close database session
db.close()

# Help section
with st.expander("ℹ️ Ajuda - Como calcular reajustes"):
    st.markdown("""
    **Passo a passo:**

    1. **Selecione o contrato** para o qual deseja calcular o reajuste
    2. **Verifique** as informações do contrato, especialmente a Data Base do Orçamento
    3. **Informe** o valor a ser reajustado
    4. **Adicione os períodos de reajuste:**
       - Para contratos com até 2 anos: use apenas 1 período
       - Para contratos com mais de 2 anos: adicione múltiplos períodos para verificação
    5. **Clique** em "Calcular Reajuste"
    6. **Revise** os resultados e a memória de cálculo
    7. **Salve** o(s) cálculo(s) no histórico (opcional)
    8. **Baixe** a Memória de Cálculo em PDF

    **Múltiplos Períodos de Reajuste:**

    Para contratos com mais de 2 anos desde a proposta, você pode adicionar
    múltiplos períodos de reajuste usando os botões "Adicionar período" e
    "Remover período". Isso permite verificar os valores de reajuste em
    diferentes momentos do contrato.

    **Regras importantes:**

    - O primeiro reajuste só pode ser calculado após 365 dias da data base do orçamento
    - O fator K é **truncado** (não arredondado) na 4ª casa decimal
    - Os índices I₀ e I₁ devem estar cadastrados no sistema
    - Todos os cálculos são salvos em um histórico para auditoria

    **Fórmulas utilizadas:**

    - **K = (I₁ / I₀) - 1** → Fator de reajuste
    - **R = K × Vr** → Valor do reajuste
    """)
