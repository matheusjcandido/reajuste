# Sistema de Cálculo de Reajuste de Obras (SESP/PR)

## 🎯 Status: ✅ IMPLEMENTADO E EM PRODUÇÃO

Aplicação web para o Centro de Engenharia e Arquitetura da SESP/PR que automatiza o cálculo de reajustamento de contratos de obras públicas, garantindo segurança jurídica e matemática, eliminando erros de arredondamento e planilhas manuais.

**Contexto de Negócio:**
O sistema adere estritamente às cláusulas contratuais de obras públicas (Lei 14.133/21 e Decreto Estadual 10.086/22), com foco no índice **INCC-DI** da FGV.

## 📊 Visão Geral da Aplicação

**Dados Disponíveis:**
- ✅ **376 índices INCC-DI** importados (08/1994 a 11/2025)
- ✅ Sistema de gestão completo de contratos
- ✅ Trilha de auditoria completa de cálculos
- ✅ Geração automática de Memórias de Cálculo em PDF

**Navegação Otimizada para Usuários:**
1. **Cálculo** (primeira aba - usuário comum):
   - Calcular Reajuste: Interface guiada para cálculo rápido
2. **Gestão de Dados** (administrador):
   - Gestão de Contratos
   - Gestão de Índices INCC-DI
3. **Administração** (apenas administrador):
   - Dashboard com estatísticas do sistema

**Formato de Dados:**
- Datas: dd/mm/yyyy (formato brasileiro)
- Valores: R$ 10.000,00 (ponto para milhares, vírgula para decimais)

---

## 🚀 Como Executar

### Instalação
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run main.py
```

### Acesso
Aplicação disponível em: **http://localhost:8501**

---

## 2. Stack Tecnológica Implementada

* **Linguagem:** Python 3.12
* **Frontend/App Framework:** Streamlit 1.35+ (interface web responsiva)
* **Banco de Dados:** SQLite via SQLAlchemy 2.0+ (com DecimalType customizado)
* **Manipulação de Dados:** Pandas 2.0+ & Decimal (Python Standard Lib)
* **Geração de Relatórios:** FPDF2 2.8+ (Memórias de Cálculo em PDF profissionais)
* **Testes:** pytest 7.0+

---

## 3. Regras de Negócio (Hard Constraints)

Estas regras são derivadas da minuta de edital padrão da SESP e **não podem** ser flexibilizadas.

### 3.1. Definição de Índices e Datas
* [cite_start]**Índice Padrão:** INCC-DI (Índice Nacional de Custo da Construção - Disponibilidade Interna), da FGV[cite: 46].
* **Data Base ($I_0$):** O índice inicial **NÃO** é o da assinatura do contrato. [cite_start]É estritamente o índice vigente na **Data do Orçamento**[cite: 35].
* [cite_start]**Periodicidade:** O reajuste ocorre após 365 dias da data do orçamento (interstício legal)[cite: 37, 42].

### 3.2. Fórmula de Cálculo
O cálculo deve seguir a fórmula exata do contrato:

$$R = K \times Vr$$

Onde:
* $R$: Valor do Reajustamento.
* [cite_start]$Vr$: Valor da medição/fatura a ser reajustada[cite: 29].
* $K$: Fator de reajustamento, calculado como:
    $$K = \left( \frac{I_i}{I_0} \right) - 1$$
    * [cite_start]$I_i$: Índice do mês de aniversário anual (ou mês de competência da medição, conforme o caso)[cite: 37].
    * [cite_start]$I_0$: Índice da data do orçamento[cite: 35].

### 3.3. Regra de Precisão (Crítica)
* [cite_start]**Truncamento:** O quociente de reajuste ($K$) deve considerar até a **quarta casa decimal, SEM ARREDONDAMENTO**[cite: 49].
    * *Exemplo:* Se o cálculo matemático resultar em `0.12349`, o sistema deve utilizar `0.1234`. O `9` final deve ser ignorado (floor), jamais arredondado para `0.1235`.
* **Tipagem:** É proibido o uso de `float` para valores monetários ou índices. Deve-se usar exclusivamente a classe `Decimal` do Python.

---

## 4. Modelagem de Dados (Implementada)

O sistema utiliza SQLAlchemy com **DecimalType customizado** para preservar precisão total no SQLite.

### Tabela: `indices_economicos`
Série histórica de índices INCC-DI (376 registros: 08/1994 a 11/2025).
* `data_referencia` (Date, PK): Primeiro dia do mês (ex: 01/01/2025)
* `nome_indice` (String): "INCC-DI"
* `valor` (DecimalType): Valor com precisão total (ex: 1225.633)

### Tabela: `contratos`
Contratos de obras públicas cadastrados.
* `id` (Integer, PK)
* `numero_contrato` (String, unique): Identificador único
* `objeto` (Text): Descrição da obra
* `empresa` (String): Nome da empresa contratada
* `data_base_orcamento` (Date): **Campo Crítico** - Define o índice I₀
* `data_assinatura` (Date): Data de assinatura do contrato
* `valor_inicial` (DecimalType): Valor contratual inicial
* `data_criacao` (DateTime): Timestamp de cadastro

**Exemplo de Contrato:**
- Número: 042/2024-SESP
- Objeto: Construção do Batalhão de Polícia Militar - 5ª Companhia
- Empresa: Engenharia & Construções Forte Ltda
- Valor: R$ 8.500.000,00
- Data Base: 01/01/2024

### Tabela: `calculos_realizados`
Trilha de auditoria completa de todos os cálculos realizados.
* `id` (Integer, PK)
* `contrato_id` (Integer, FK)
* `data_calculo` (DateTime): Timestamp do cálculo
* `mes_indice_base` (Date): Data do índice I₀
* `valor_indice_base` (DecimalType): Valor I₀ utilizado
* `mes_indice_reajuste` (Date): Data do índice I₁
* `valor_indice_reajuste` (DecimalType): Valor I₁ utilizado
* `fator_k_aplicado` (DecimalType): Fator K truncado na 4ª casa
* `valor_original_medicao` (DecimalType): Valor original (Vr)
* `valor_reajuste` (DecimalType): Valor do reajuste calculado (R)

**DecimalType Customizado:**
- Armazena valores como TEXT no SQLite
- Preserva precisão total (não converte para float)
- Essencial para conformidade legal

---

## 5. Algoritmos Implementados

### Função de Truncamento (Crítica)
Localização: [src/services/calculation.py](src/services/calculation.py)

```python
from decimal import Decimal, ROUND_FLOOR, getcontext

# Configurar precisão global segura
getcontext().prec = 28

def calcular_fator_k_truncado(indice_inicial: Decimal, indice_final: Decimal) -> Decimal:
    """
    Calcula o fator K com truncamento na 4ª casa decimal (sem arredondamento).
    Requisito: Cláusula 11.4 do Edital.

    Validações implementadas:
    - Divisão por zero
    - Valores negativos
    - Conversão automática para Decimal
    """
    if indice_inicial == 0:
        raise ValueError("Base index (I_0) cannot be zero")

    if indice_inicial < 0 or indice_final < 0:
        raise ValueError("Indices must be positive values")

    # K = (Ii / Io) - 1
    k_bruto = (indice_final / indice_inicial) - Decimal("1")

    # Aplica Truncamento (ROUND_FLOOR) para 0.0001
    k_truncado = k_bruto.quantize(Decimal("0.0001"), rounding=ROUND_FLOOR)

    return k_truncado

def calcular_valor_reajuste(valor_medicao: Decimal, fator_k: Decimal) -> Decimal:
    """
    Calcula o valor do reajuste.
    Fórmula: R = K × Vr
    Resultado truncado para 2 casas decimais (centavos).
    """
    valor_reajuste = valor_medicao * fator_k
    return valor_reajuste.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)
```

### Validação de Interstício Legal
```python
def validar_intersticio_legal(data_base: date, mes_reajuste: date) -> tuple[bool, str]:
    """
    Valida se passaram 365 dias desde a data base do orçamento.
    Retorna: (is_valid, message)
    """
    diferenca = (mes_reajuste - data_base).days

    if diferenca < 365:
        return (False, f"Interstício legal não cumprido. Passaram-se {diferenca} dias,
                        mas são necessários 365 dias.")

    return (True, f"Interstício legal cumprido ({diferenca} dias).")
```

---

## 6. Interface do Usuário (Implementada)

### Navegação (Sidebar Streamlit)

**Prioridade para Usuário Comum:**

1. **🧮 Cálculo** (Primeira Aba - Acesso Direto):
   - **Calcular Reajuste**: Interface guiada em 5 passos
     - Passo 1: Selecionar Contrato (Dropdown)
     - Passo 2: Visualizar Data Base e Índice I₀ automaticamente
     - Passo 3: Informar Valor da Medição e Mês de Reajuste
     - Passo 4: Validação automática de interstício legal (365 dias)
     - Passo 5: Botão "Calcular" → Exibe resultados
     - Exportação: Botão "Baixar Memória de Cálculo (PDF)"
     - Histórico: Visualização de cálculos anteriores do contrato

2. **📋 Gestão de Dados** (Administrador):
   - **Gestão de Contratos**:
     - Cadastro completo de contratos
     - Validação automática de índice base
     - Visualização em cards expansíveis
     - Exclusão de contratos
   - **Gestão de Índices**:
     - Formulário de cadastro manual INCC-DI
     - Visualização da tabela histórica (376 índices)
     - Exclusão de índices

3. **📊 Administração** (Apenas Administrador):
   - **Dashboard**:
     - Estatísticas: Total de índices, contratos e cálculos
     - Status do último índice cadastrado
     - Informações legais e ajuda

### Recursos da Interface

**Formatação Brasileira:**
- Datas: dd/mm/yyyy (01/01/2024)
- Valores: R$ 10.000,00 (ponto para milhares)
- Percentuais: 0,82% (vírgula para decimais)

**Validações em Tempo Real:**
- Campos obrigatórios
- Valores positivos
- Datas válidas
- Interstício legal de 365 dias
- Disponibilidade de índices

**Mensagens de Erro Claras:**
- Índice não encontrado → Orientação para cadastrar
- Interstício não cumprido → Mostra dias restantes
- Valores inválidos → Explicação do erro

**Ajuda Contextual:**
- Ícones ℹ️ em cada página
- Seções expansíveis "Como usar"
- Exemplos práticos inline

---

## 7. Documentação Disponível

- **[GUIA_USO.md](GUIA_USO.md)**: Manual completo para usuários
- **[EXEMPLOS.md](EXEMPLOS.md)**: Casos práticos de cálculo
- **[README_IMPLEMENTACAO.md](README_IMPLEMENTACAO.md)**: Detalhes técnicos da implementação
- **Ajuda inline**: Disponível em todas as páginas do sistema

---

## 8. Testes e Validação

### Testes Automatizados
Localização: [tests/](tests/)

**Cobertura:**
- ✅ Truncamento em 4 casas decimais (test_decimal_utils.py)
- ✅ Cálculo do fator K (test_calculation.py)
- ✅ Cálculo do reajuste R (test_calculation.py)
- ✅ Validação de interstício legal (test_calculation.py)
- ✅ Conversão segura para Decimal (test_decimal_utils.py)

**Exemplo de Teste:**
```python
def test_truncate_not_round():
    """Verifica que 0.12349 vira 0.1234 (não 0.1235)"""
    assert truncate_at_4_decimals(Decimal("0.12349")) == Decimal("0.1234")
    assert truncate_at_4_decimals(Decimal("0.99999")) == Decimal("0.9999")
```

### Executar Testes
```bash
pytest tests/ -v
```

---

## 9. Conformidade Legal

✅ **Lei nº 14.133/2021** (Nova Lei de Licitações)
✅ **Decreto Estadual nº 10.086/2022**
✅ **Índice INCC-DI** (Fundação Getúlio Vargas)
✅ **Truncamento na 4ª casa decimal** (Cláusula 11.4)
✅ **Interstício legal de 365 dias**
✅ **Trilha de auditoria completa**

---

## 10. Contato e Suporte

Para dúvidas sobre o sistema:
- Consulte a documentação em GUIA_USO.md
- Veja exemplos práticos em EXEMPLOS.md
- Acesse a ajuda inline nas páginas do sistema

**Versão:** 1.0.0
**Desenvolvido para:** SESP/PR - Centro de Engenharia e Arquitetura
**Status:** ✅ Em Produção