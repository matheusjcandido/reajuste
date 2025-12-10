# Exemplos de Uso - Sistema de Reajuste

## Exemplo 1: Cálculo Simples

### Cenário
- **Contrato:** 001/2024
- **Data Base do Orçamento:** 01/01/2024
- **Índice I₀:** 105.4
- **Mês de Reajuste:** 01/01/2025 (após 365 dias)
- **Índice I₁:** 105.5
- **Valor da Medição:** R$ 10.000,00

### Cálculo Passo a Passo

**1. Calcular Fator K:**
```
K = (I₁ / I₀) - 1
K = (105.5 / 105.4) - 1
K = 1.000948767... - 1
K = 0.000948767...
K = 0.0009 (truncado à 4ª casa decimal, SEM arredondamento)
```

**2. Calcular Valor do Reajuste:**
```
R = K × Vr
R = 0.0009 × 10.000,00
R = 9,00
```

**3. Valor Total Atualizado:**
```
Total = Vr + R
Total = 10.000,00 + 9,00
Total = 10.009,00
```

### Resultado
- Fator K: **0.0009**
- Valor do Reajuste: **R$ 9,00**
- Valor Total: **R$ 10.009,00**

---

## Exemplo 2: Reajuste Maior

### Cenário
- **Contrato:** 002/2023
- **Data Base do Orçamento:** 01/06/2023
- **Índice I₀:** 100.0
- **Mês de Reajuste:** 01/06/2024
- **Índice I₁:** 110.5
- **Valor da Medição:** R$ 1.000.000,00

### Cálculo

**Fator K:**
```
K = (110.5 / 100.0) - 1
K = 1.105 - 1
K = 0.105
K = 0.1050 (já está com 4 casas decimais)
```

**Reajuste:**
```
R = 0.1050 × 1.000.000,00
R = 105.000,00
```

**Total:**
```
Total = 1.000.000,00 + 105.000,00
Total = 1.105.000,00
```

### Resultado
- Fator K: **0.1050** (10,50% de reajuste)
- Valor do Reajuste: **R$ 105.000,00**
- Valor Total: **R$ 1.105.000,00**

---

## Exemplo 3: Demonstração do Truncamento (Não Arredondamento)

### Cenário
- **I₀:** 100.0
- **I₁:** 100.6
- **Vr:** R$ 50.000,00

### Cálculo Detalhado

**Fator K (sem truncamento):**
```
K = (100.6 / 100.0) - 1
K = 1.006 - 1
K = 0.006
```

**Fator K (truncado - regra correta):**
```
K = 0.0060 (já está com 4 casas decimais exatas)
```

**Agora um exemplo onde o truncamento importa:**
- **I₁:** 100.5714

```
K = (100.5714 / 100.0) - 1
K = 1.005714 - 1
K = 0.005714
K = 0.0057 (truncado, não 0.0058!)
```

**Reajuste:**
```
R = 0.0057 × 50.000,00
R = 285,00
```

**Se tivesse arredondado (ERRADO):**
```
K = 0.0058 (arredondado - ERRADO!)
R = 0.0058 × 50.000,00
R = 290,00 (diferença de R$ 5,00!)
```

### Importância do Truncamento
O truncamento garante que o cálculo seja sempre conservador e juridicamente defensável, evitando reajustes maiores do que o permitido pela lei.

---

## Exemplo 4: Validação de Interstício Legal

### Cenário Inválido
- **Data Base:** 01/01/2024
- **Tentativa de Reajuste:** 01/06/2024 (apenas 152 dias)

**Resultado:** ❌ Sistema bloqueia o cálculo
```
Erro: Interstício legal não cumprido.
Passaram-se 152 dias, mas são necessários 365 dias
desde a data base do orçamento (01/01/2024).
```

### Cenário Válido
- **Data Base:** 01/01/2024
- **Reajuste:** 01/01/2025 (365 dias)

**Resultado:** ✅ Cálculo permitido
```
Interstício legal cumprido (365 dias desde a data base).
```

---

## Fluxo Completo de Uso

### 1. Cadastrar Índices
```
Data: 01/01/2024 → Valor: 105.4560
Data: 01/02/2024 → Valor: 105.8920
Data: 01/03/2024 → Valor: 106.1230
...
Data: 01/01/2025 → Valor: 106.5400
```

### 2. Cadastrar Contrato
```
Número: 001/2024
Empresa: Construtora ABC Ltda
Objeto: Construção de escola municipal
Data Base do Orçamento: 01/01/2024 ⚠️
Data de Assinatura: 15/02/2024
Valor Inicial: R$ 5.000.000,00
```

### 3. Calcular Primeiro Reajuste (após 1 ano)
```
Contrato: 001/2024
Valor da Medição: R$ 250.000,00
Mês de Reajuste: 01/01/2025

Resultado:
├─ I₀: 105.4560 (01/01/2024)
├─ I₁: 106.5400 (01/01/2025)
├─ K: 0.0102
├─ R: R$ 2.550,00
└─ Total: R$ 252.550,00
```

### 4. Gerar Memória de Cálculo (PDF)
O sistema gera automaticamente um PDF com:
- Informações do contrato
- Fundamentação legal
- Cálculo detalhado do fator K
- Cálculo do reajuste
- Resumo final
- Nota sobre truncamento

### 5. Histórico Mantido
Todos os cálculos são salvos automaticamente com:
- Data e hora
- Índices utilizados
- Fator K aplicado
- Valores calculados

---

## Dicas Práticas

### ✅ Boas Práticas

1. **Sempre cadastre os índices mensalmente**
   - Facilita cálculos futuros
   - Evita atrasos

2. **Verifique a Data Base do Orçamento**
   - É o campo mais importante
   - Confirme no edital/contrato

3. **Salve os cálculos no histórico**
   - Mantém trilha de auditoria
   - Facilita consultas futuras

4. **Baixe as Memórias de Cálculo em PDF**
   - Documentação oficial
   - Anexe aos processos

### ❌ Erros Comuns

1. **Confundir Data Base com Data de Assinatura**
   - São datas diferentes!
   - Data Base define o I₀

2. **Tentar reajustar antes de 365 dias**
   - Sistema bloqueia automaticamente
   - Aguarde o interstício legal

3. **Usar vírgula ao invés de ponto em valores**
   - Sistema aceita ambos
   - Mas ponto é mais seguro

4. **Não cadastrar índices antes dos contratos**
   - Cadastre índices primeiro
   - Depois os contratos

---

## Validação de Resultados

Para validar manualmente um cálculo:

1. **Confira os índices**
   - I₀ corresponde à data base?
   - I₁ corresponde ao mês de reajuste?

2. **Calcule K manualmente**
   - Use calculadora com precisão decimal
   - Verifique o truncamento (4ª casa)

3. **Calcule R**
   - R = K × Vr
   - Verifique se está em reais e centavos

4. **Compare com o sistema**
   - Valores devem ser exatamente iguais
   - Qualquer diferença indica erro

---

## Casos Especiais

### Reajuste Zero
Se os índices forem iguais:
```
I₀ = 105.5
I₁ = 105.5
K = 0.0000
R = 0.00
```

### Deflação (índice menor)
O sistema permite cálculo mesmo se I₁ < I₀:
```
I₀ = 105.5
I₁ = 104.5
K = (104.5 / 105.5) - 1 = -0.0094
R = -0.0094 × 10.000,00 = -94,00 (desconto!)
```

### Múltiplos Reajustes
Para o mesmo contrato, pode-se calcular:
- Reajuste anual (após 365 dias)
- Reajuste em cada medição
- Histórico completo mantido

---

## Suporte e Verificação

Em caso de dúvida sobre um cálculo:

1. Confira este arquivo de exemplos
2. Consulte o GUIA_USO.md
3. Verifique a ajuda inline nas páginas
4. Compare com cálculos manuais
5. Revise a especificação original (readme.md)
