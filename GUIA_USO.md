# Guia de Uso - Sistema de Reajuste SESP/PR

## Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

Ou com pip3:
```bash
pip3 install -r requirements.txt
```

### 2. Executar a Aplicação

```bash
streamlit run main.py
```

O aplicativo abrirá automaticamente no navegador em `http://localhost:8501`

## Como Usar o Sistema

### Passo 1: Cadastrar Índices INCC-DI

1. Navegue até **"Gestão de Índices"** no menu lateral
2. Preencha o formulário:
   - **Data de Referência**: Use o primeiro dia do mês (ex: 01/01/2025)
   - **Valor do Índice**: Valor do INCC-DI com precisão decimal (ex: 105.4560)
3. Clique em **"Adicionar"**

**Onde obter os valores:**
- Acesse o [Portal FGV IBRE](https://portalibre.fgv.br/)
- Procure por INCC-DI (Índice Nacional de Custo da Construção - Disponibilidade Interna)

### Passo 2: Cadastrar Contratos

1. Navegue até **"Gestão de Contratos"**
2. Preencha todos os campos:
   - **Número do Contrato**: Identificador único (ex: 001/2025)
   - **Empresa Contratada**: Nome completo
   - **Objeto**: Descrição do contrato
   - **Data de Assinatura**: Data da assinatura
   - **Data Base do Orçamento**: ⚠️ **CRÍTICO** - Define o índice I₀
   - **Valor Inicial**: Valor em reais
3. Clique em **"Cadastrar Contrato"**

**⚠️ ATENÇÃO:** A "Data Base do Orçamento" é fundamental! Ela define qual índice será usado como base (I₀) para todos os cálculos de reajuste.

### Passo 3: Calcular Reajuste

1. Navegue até **"Calcular Reajuste"**
2. Selecione o contrato
3. Verifique as informações exibidas (Data Base e Índice I₀)
4. Informe:
   - **Valor da Medição**: Valor a ser reajustado
   - **Mês de Referência**: Mês para o qual deseja calcular o reajuste
5. Clique em **"Calcular Reajuste"**
6. Revise os resultados
7. **Salve** o cálculo no histórico (opcional)
8. **Baixe** a Memória de Cálculo em PDF

## Regras Importantes

### Interstício Legal
- O reajuste só pode ser calculado após **365 dias** da data base do orçamento
- O sistema valida automaticamente este requisito

### Regra de Truncamento
- O fator K é **truncado** (não arredondado) na 4ª casa decimal
- Exemplo: 0.12349 → 0.1234 (não 0.1235)
- Esta regra está em conformidade com a cláusula contratual

### Fórmulas Aplicadas

**Fator de Reajuste (K):**
```
K = (I₁ / I₀) - 1
```
Onde:
- I₀ = Índice na data base do orçamento
- I₁ = Índice no mês de reajuste

**Valor do Reajuste (R):**
```
R = K × Vr
```
Onde:
- Vr = Valor da medição/fatura

## Fundamentação Legal

- **Lei nº 14.133/2021** (Nova Lei de Licitações)
- **Decreto Estadual nº 10.086/2022**
- **Índice:** INCC-DI (FGV)

## Estrutura de Arquivos

```
reajuste/
├── main.py                    # Ponto de entrada da aplicação
├── requirements.txt           # Dependências Python
├── src/                       # Código-fonte
│   ├── db/                    # Modelos e conexão do banco de dados
│   ├── services/              # Lógica de negócio
│   └── utils/                 # Utilitários (truncamento, formatação)
├── pages/                     # Páginas Streamlit
│   ├── dashboard.py           # Visão geral
│   ├── indices.py             # Gestão de índices
│   ├── contracts.py           # Gestão de contratos
│   └── calculate.py           # Cálculo de reajuste
├── tests/                     # Testes automatizados
└── data/                      # Banco de dados SQLite
    └── reajuste.db            # Criado automaticamente
```

## Dados Armazenados

O sistema armazena automaticamente:
- ✅ Histórico de índices INCC-DI
- ✅ Informações dos contratos
- ✅ **Trilha de auditoria** completa de todos os cálculos realizados

Cada cálculo registra:
- Contrato, data, índices utilizados (I₀ e I₁)
- Fator K aplicado
- Valores originais e reajustados

## Troubleshooting

### Erro: "Índice não encontrado"
**Solução:** Cadastre o índice na página "Gestão de Índices" antes de usar no cálculo.

### Erro: "Interstício legal não cumprido"
**Solução:** O reajuste só pode ser calculado após 365 dias da data base do orçamento.

### Aplicação não inicia
**Solução:**
1. Verifique se instalou todas as dependências: `pip install -r requirements.txt`
2. Execute com: `streamlit run main.py`

## Testes

Para executar os testes automatizados (se pytest estiver instalado):

```bash
pytest tests/ -v
```

Os testes verificam:
- ✅ Truncamento correto (sem arredondamento)
- ✅ Cálculo do fator K
- ✅ Cálculo do valor de reajuste
- ✅ Validação do interstício legal

## Suporte

Para problemas ou dúvidas:
1. Verifique este guia
2. Consulte os "ℹ️ Ajuda" em cada página do sistema
3. Revise a especificação técnica no arquivo `readme.md`
