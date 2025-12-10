"""
PDF generation service for calculation reports (Memória de Cálculo).

Uses FPDF2 library to generate professional financial reports.
"""

from fpdf import FPDF
from decimal import Decimal
from datetime import date, datetime
from src.utils.decimal_utils import format_brazilian_currency


class RelatorioMemoriaCalculo(FPDF):
    """
    PDF report generator for salary adjustment calculations.

    Generates 'Memória de Cálculo' (Calculation Memory) reports
    with all calculation details for legal compliance.
    """

    def __init__(self):
        """Initialize PDF with A4 portrait format."""
        super().__init__(orientation="P", unit="mm", format="A4")
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        """Page header with SESP branding."""
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "SESP/PR - Centro de Engenharia e Arquitetura", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 6, "Sistema de Cálculo de Reajuste de Obras", ln=True, align="C")
        self.ln(5)

    def footer(self):
        """Page footer with page number and generation date."""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()} - Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", align="C")

    def generate_report(
        self,
        numero_contrato: str,
        empresa: str,
        objeto: str,
        data_base: date,
        data_assinatura: date,
        indice_base: Decimal,
        mes_reajuste: date,
        indice_reajuste: Decimal,
        fator_k: Decimal,
        valor_medicao: Decimal,
        valor_reajuste: Decimal,
        valor_total: Decimal
    ) -> bytes:
        """
        Generate complete calculation memory report.

        Args:
            numero_contrato: Contract number
            empresa: Company name
            objeto: Contract description
            data_base: Budget base date
            data_assinatura: Contract signature date
            indice_base: I_0 (base index value)
            mes_reajuste: Adjustment reference month
            indice_reajuste: I_i (adjustment index value)
            fator_k: K factor (truncated to 4 decimals)
            valor_medicao: Vr (original measurement value)
            valor_reajuste: R (calculated adjustment value)
            valor_total: Total value after adjustment

        Returns:
            bytes: PDF file content as bytes
        """
        # Title
        self.set_font("Arial", "B", 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, "MEMÓRIA DE CÁLCULO - REAJUSTAMENTO", ln=True, align="C", fill=True)
        self.ln(8)

        # Contract Information Section
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "1. INFORMAÇÕES DO CONTRATO", ln=True)
        self.ln(2)

        self.set_font("Arial", "", 10)
        self._add_info_line("Número do Contrato:", numero_contrato)
        self._add_info_line("Empresa Contratada:", empresa)
        self._add_info_line("Objeto:", objeto, multiline=True)
        self._add_info_line("Data de Assinatura:", data_assinatura.strftime("%d/%m/%Y"))
        self._add_info_line("Data Base do Orçamento:", data_base.strftime("%d/%m/%Y"), bold_value=True)
        self.ln(5)

        # Legal Framework Section
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "2. FUNDAMENTAÇÃO LEGAL", ln=True)
        self.ln(2)

        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5,
            "Lei nº 14.133/2021 (Nova Lei de Licitações) e Decreto Estadual nº 10.086/2022.\n"
            "Índice aplicado: INCC-DI (Índice Nacional de Custo da Construção - "
            "Disponibilidade Interna), publicado pela Fundação Getúlio Vargas (FGV)."
        )
        self.ln(5)

        # Calculation Details Section
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "3. CÁLCULO DO FATOR DE REAJUSTE (K)", ln=True)
        self.ln(2)

        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5,
            f"Fórmula: K = (I1 / I0) - 1\n\n"
            f"Onde:\n"
            f"- I0 = Índice na data base do orçamento ({data_base.strftime('%m/%Y')}): {indice_base}\n"
            f"- I1 = Índice no mês de reajuste ({mes_reajuste.strftime('%m/%Y')}): {indice_reajuste}\n"
        )
        self.ln(2)

        # Calculation formula breakdown
        self.set_font("Arial", "B", 10)
        self.cell(0, 6, "Cálculo:", ln=True)
        self.set_font("Arial", "", 10)

        # Show intermediate calculation
        divisao = indice_reajuste / indice_base
        self.multi_cell(0, 5,
            f"K = ({indice_reajuste} / {indice_base}) - 1\n"
            f"K = {divisao:.10f} - 1\n"
            f"K = {divisao - Decimal('1'):.10f}\n"
        )

        # Highlight truncation
        self.set_font("Arial", "B", 10)
        self.set_fill_color(255, 255, 200)
        self.cell(0, 8, f"K (truncado à 4ª casa decimal): {fator_k}", ln=True, fill=True)
        self.ln(2)

        self.set_font("Arial", "I", 9)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 4,
            "Nota: Conforme cláusula contratual, o fator K é truncado (sem arredondamento) "
            "na quarta casa decimal."
        )
        self.set_text_color(0, 0, 0)
        self.ln(5)

        # Adjustment Value Calculation Section
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "4. CÁLCULO DO VALOR DO REAJUSTE (R)", ln=True)
        self.ln(2)

        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5,
            f"Fórmula: R = K × Vr\n\n"
            f"Onde:\n"
            f"- K = Fator de reajuste: {fator_k}\n"
            f"- Vr = Valor da medição/fatura: {format_brazilian_currency(valor_medicao)}\n"
        )
        self.ln(2)

        self.set_font("Arial", "B", 10)
        self.cell(0, 6, "Cálculo:", ln=True)
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5,
            f"R = {fator_k} × {format_brazilian_currency(valor_medicao)}\n"
            f"R = {format_brazilian_currency(valor_reajuste)}"
        )
        self.ln(5)

        # Final Summary Section
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "5. RESUMO DO REAJUSTAMENTO", ln=True)
        self.ln(2)

        # Summary table
        self.set_font("Arial", "B", 10)
        self.set_fill_color(240, 240, 240)
        col_widths = [120, 70]

        self.cell(col_widths[0], 8, "Descrição", border=1, fill=True)
        self.cell(col_widths[1], 8, "Valor (R$)", border=1, align="R", fill=True, ln=True)

        self.set_font("Arial", "", 10)
        self._add_table_row(col_widths, "Valor Original da Medição (Vr)", format_brazilian_currency(valor_medicao))
        self._add_table_row(col_widths, "Fator de Reajuste (K)", f"{fator_k}")
        self._add_table_row(col_widths, "Valor do Reajuste (R)", format_brazilian_currency(valor_reajuste))

        # Total row with highlight
        self.set_font("Arial", "B", 10)
        self.set_fill_color(200, 220, 255)
        self.cell(col_widths[0], 8, "Valor Total Atualizado", border=1, fill=True)
        self.cell(col_widths[1], 8, format_brazilian_currency(valor_total), border=1, align="R", fill=True, ln=True)

        self.ln(10)

        # Footer note
        self.set_font("Arial", "I", 9)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 4,
            "Este documento foi gerado automaticamente pelo Sistema de Cálculo de Reajuste "
            "da SESP/PR. Todos os cálculos seguem estritamente as fórmulas contratuais e "
            "a legislação vigente."
        )

        # Return PDF as bytes
        return bytes(self.output(dest='S'))

    def _add_info_line(self, label: str, value: str, bold_value: bool = False, multiline: bool = False):
        """
        Add an information line with label and value.

        Args:
            label: Label text
            value: Value text
            bold_value: Whether to make the value bold
            multiline: Whether to use multi_cell for long values
        """
        self.set_font("Arial", "B", 10)
        if multiline:
            self.cell(0, 5, label, ln=True)
            self.set_font("Arial", "B" if bold_value else "", 10)
            self.multi_cell(0, 5, f"  {value}")
        else:
            self.cell(50, 6, label)
            self.set_font("Arial", "B" if bold_value else "", 10)
            self.cell(0, 6, value, ln=True)

    def _add_table_row(self, col_widths: list, label: str, value: str):
        """
        Add a row to a table.

        Args:
            col_widths: List of column widths
            label: Row label
            value: Row value
        """
        self.cell(col_widths[0], 7, label, border=1)
        self.cell(col_widths[1], 7, value, border=1, align="R", ln=True)


def gerar_pdf_memoria_calculo(
    numero_contrato: str,
    empresa: str,
    objeto: str,
    data_base: date,
    data_assinatura: date,
    indice_base: Decimal,
    mes_reajuste: date,
    indice_reajuste: Decimal,
    fator_k: Decimal,
    valor_medicao: Decimal,
    valor_reajuste: Decimal,
    valor_total: Decimal
) -> bytes:
    """
    Generate PDF calculation memory report (convenience function).

    Args:
        See RelatorioMemoriaCalculo.generate_report()

    Returns:
        bytes: PDF file content
    """
    pdf = RelatorioMemoriaCalculo()
    return pdf.generate_report(
        numero_contrato=numero_contrato,
        empresa=empresa,
        objeto=objeto,
        data_base=data_base,
        data_assinatura=data_assinatura,
        indice_base=indice_base,
        mes_reajuste=mes_reajuste,
        indice_reajuste=indice_reajuste,
        fator_k=fator_k,
        valor_medicao=valor_medicao,
        valor_reajuste=valor_reajuste,
        valor_total=valor_total
    )
