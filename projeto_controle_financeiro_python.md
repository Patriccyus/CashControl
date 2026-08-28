# Projeto: Controle Financeiro Pessoal em Python

## 1. Visão geral

### Objetivo
Criar uma aplicação desktop instalável em computadores Windows, desenvolvida em Python, para registrar e analisar movimentações financeiras de forma mais rápida, simples e confiável do que uma planilha Excel.

O objetivo central não é apenas registrar receitas e despesas, mas responder claramente:

> **Para onde está indo o meu dinheiro?**

A aplicação deverá permitir:
- registrar entradas e saídas rapidamente;
- classificar os lançamentos por categorias;
- acompanhar limites esperados de gastos;
- consultar o histórico com filtros simples;
- acompanhar saldo e fluxo de caixa;
- identificar padrões e desvios;
- gerar um relatório mensal com gráficos e insights;
- funcionar localmente, sem depender de internet;
- ser instalável em outro computador.

---

# 2. Princípios do projeto

A aplicação deve seguir cinco princípios:

1. **Registro rápido**
   - Um lançamento deve ser criado em poucos segundos.
   - Evitar formulários excessivamente grandes.

2. **Pouca manutenção**
   - O usuário não deve precisar administrar fórmulas, abas ou referências como em uma planilha.

3. **Clareza**
   - O sistema deve mostrar rapidamente quanto entrou, quanto saiu e onde o dinheiro foi gasto.

4. **Histórico confiável**
   - Os lançamentos não devem ser apagados facilmente.
   - Alterações e exclusões devem exigir confirmação.

5. **Análise automática**
   - O sistema deve transformar os registros em informações úteis, não apenas armazená-los.

---

# 3. Escopo inicial do MVP

O primeiro lançamento do projeto deve ser pequeno.

## Funcionalidades obrigatórias

### 3.1 Cadastro de movimentações

Cada movimentação deverá possuir:

- Data
- Tipo: Entrada ou Saída
- Descrição
- Valor
- Categoria
- Subcategoria opcional
- Forma de pagamento
- Conta/Carteira
- Observação opcional
- Status: Pago/Recebido ou Pendente
- Identificador único

### 3.2 Categorias

Exemplos:

**Entradas**
- Salário
- Freelance
- Venda
- Rendimentos
- Outros

**Saídas**
- Supermercado
- Alimentação
- Moradia
- Transporte
- Saúde
- Educação
- Lazer
- Assinaturas
- Compras
- Serviços
- Impostos
- Outros

As categorias devem ser configuráveis pelo usuário.

### 3.3 Limites de gastos

Cada categoria poderá possuir:

- Limite mensal esperado
- Valor gasto no mês
- Percentual consumido
- Valor restante
- Indicador de situação

Exemplo:

| Categoria | Limite | Gasto | Consumo |
|---|---:|---:|---:|
| Supermercado | R$ 1.200 | R$ 950 | 79% |
| Lazer | R$ 400 | R$ 520 | 130% |
| Saúde | R$ 500 | R$ 180 | 36% |

O sistema deverá sinalizar quando:
- o gasto estiver próximo do limite;
- o limite for ultrapassado;
- houver crescimento anormal em relação aos meses anteriores.

---

# 4. Conceito principal da interface

A aplicação não deve começar pelo cadastro de categorias ou configurações.

A tela inicial deve responder imediatamente:

## "Como está minha situação financeira?"

### Dashboard

Mostrar:

- Saldo atual
- Total de entradas no mês
- Total de saídas no mês
- Resultado do mês
- Contas pendentes
- Percentual da renda comprometida
- Principais categorias de gastos

### Visualizações

Gráficos recomendados:

1. Entradas x saídas por mês
2. Gastos por categoria
3. Evolução do saldo
4. Limite x gasto por categoria
5. Gastos por forma de pagamento

Evitar excesso de gráficos.

O dashboard deve priorizar informação acionável.

---

# 5. Tela de lançamento rápido

Essa é uma das partes mais importantes do sistema.

O usuário deve conseguir registrar uma despesa sem navegar por várias telas.

## Fluxo ideal

1. Clicar em "Nova movimentação"
2. Escolher Entrada ou Saída
3. Informar valor
4. Escolher categoria
5. Informar descrição
6. Confirmar

Campos secundários podem ser opcionais.

## Melhorias futuras

Adicionar atalhos para:

- Última categoria utilizada
- Categorias favoritas
- Lançamentos recorrentes
- Duplicar lançamento
- Preenchimento automático da data
- Sugestão de categoria baseada na descrição

Exemplo:

Descrição:
"Compra no Carrefour"

O sistema poderá sugerir:
**Supermercado**

O usuário apenas confirma.

---

# 6. Histórico financeiro

Criar uma tela semelhante a uma tabela, mas mais simples que uma planilha.

Colunas:

- Data
- Descrição
- Categoria
- Tipo
- Valor
- Forma de pagamento
- Status

## Filtros

O usuário deverá conseguir filtrar por:

- Período
- Categoria
- Tipo
- Forma de pagamento
- Conta
- Status

Também deverá existir uma busca por texto.

## Operações

Permitir:

- Editar
- Excluir
- Duplicar
- Visualizar detalhes

A exclusão deve solicitar confirmação.

---

# 7. Contas e formas de pagamento

Separar dois conceitos.

## Conta

Representa onde o dinheiro está:

- Banco
- Conta corrente
- Poupança
- Dinheiro
- Carteira digital

## Forma de pagamento

Representa como uma compra foi realizada:

- Pix
- Débito
- Crédito
- Dinheiro
- Boleto
- Transferência

Isso evita misturar conceitos diferentes no banco de dados.

---

# 8. Cartão de crédito

O cartão merece uma estrutura própria.

No MVP, pode ser tratado inicialmente como uma forma de pagamento.

Em uma segunda etapa, implementar:

- Cartões cadastrados
- Limite do cartão
- Fechamento da fatura
- Vencimento
- Compras parceladas
- Faturas
- Parcelas futuras

### Atenção

Não misturar:

**Data da compra**

com

**Data do pagamento da fatura**

Essa distinção será importante para relatórios financeiros corretos.

---

# 9. Despesas recorrentes

Criar posteriormente um recurso para lançamentos recorrentes.

Exemplos:

- Aluguel
- Internet
- Netflix
- Energia
- Escola
- Academia
- Seguros

O usuário poderá definir:

- Descrição
- Valor
- Categoria
- Frequência
- Data de início
- Data de término, se houver

O sistema poderá gerar automaticamente os lançamentos.

---

# 10. Orçamento mensal

Criar um módulo de planejamento.

Para cada categoria:

- Limite mensal
- Valor utilizado
- Valor restante
- Percentual utilizado

Além disso, permitir um limite geral de despesas.

Exemplo:

**Renda esperada:** R$ 8.000

**Despesas planejadas:** R$ 6.000

**Margem esperada:** R$ 2.000

Isso permite comparar:

> Planejado x Realizado

---

# 11. Relatórios mensais

Ao final de cada mês, gerar automaticamente um relatório.

## Estrutura sugerida

### 1. Resumo

- Total recebido
- Total gasto
- Resultado
- Maior categoria de gasto
- Maior despesa individual
- Taxa de economia

### 2. Distribuição dos gastos

Mostrar quanto foi gasto em cada categoria.

### 3. Comparação com orçamento

Exemplo:

- Supermercado: dentro do limite
- Lazer: acima do limite
- Transporte: dentro do limite
- Saúde: abaixo do limite

### 4. Comparação histórica

Comparar o mês atual com:

- mês anterior;
- média dos últimos 3 meses;
- média dos últimos 6 meses.

### 5. Insights

O sistema deverá gerar observações objetivas.

Exemplos:

> Seus gastos com lazer aumentaram 32% em relação ao mês anterior.

> Supermercado representa 18% das suas despesas no período.

> Você ultrapassou o limite planejado em 2 categorias.

> Sua renda aumentou, mas suas despesas cresceram em proporção maior.

Os insights devem ser baseados nos dados reais e não em frases genéricas.

---

# 12. Indicadores financeiros

Criar indicadores simples.

## Resultado mensal

Entradas - Saídas

## Taxa de economia

Resultado / Entradas × 100

## Participação por categoria

Gasto da categoria / Total de gastos × 100

## Consumo do orçamento

Gasto realizado / Limite × 100

## Crescimento de despesas

(Mês atual - mês anterior) / mês anterior × 100

Esses indicadores serão a base dos relatórios.

---

# 13. Insights inteligentes

Não começar com inteligência artificial.

Primeiro criar um motor de regras determinísticas.

Exemplos:

### Regra 1
Se categoria > 100% do limite:

"Categoria acima do orçamento."

### Regra 2
Se gasto atual > média dos últimos 3 meses em determinado percentual:

"Gasto acima do padrão histórico."

### Regra 3
Se uma categoria representar parcela elevada das despesas:

"Categoria representa grande parte das despesas."

### Regra 4
Se despesas crescerem mais que receitas:

"Despesas cresceram acima das entradas."

Essa abordagem é mais simples, auditável e adequada para um sistema financeiro local.

IA poderá ser estudada futuramente.

---

# 14. Banco de dados

Para a primeira versão, utilizar:

**SQLite**

Motivos:

- Não exige instalação de servidor.
- Funciona localmente.
- É adequado para uma aplicação pessoal.
- Facilita distribuição.
- É muito mais seguro estruturalmente que armazenar dados em CSV.
- Permite consultas SQL.

## Estrutura conceitual

### Tabela movimentacoes

- id
- data
- tipo
- descricao
- valor
- categoria_id
- subcategoria_id
- conta_id
- forma_pagamento_id
- status
- observacao
- criado_em
- atualizado_em

### Tabela categorias

- id
- nome
- tipo
- ativo

### Tabela orcamentos

- id
- categoria_id
- mes
- ano
- limite

### Tabela contas

- id
- nome
- tipo
- saldo_inicial
- ativo

### Tabela formas_pagamento

- id
- nome
- tipo
- ativo

### Tabela recorrencias

- id
- descricao
- valor
- categoria_id
- frequencia
- proxima_data
- ativo

---

# 15. Arquitetura do projeto

Evitar colocar tudo em um único arquivo Python.

A aplicação deverá ser dividida por responsabilidades.

Estrutura conceitual:

```text
controle_financeiro/
│
├── app/
│   ├── interface/
│   ├── models/
│   ├── services/
│   ├── repositories/
│   ├── database/
│   ├── reports/
│   ├── analytics/
│   └── utils/
│
├── data/
│
├── reports/
│
├── tests/
│
├── assets/
│
├── main
│
├── requirements
│
└── README
```

A implementação concreta dessa estrutura deverá ser definida antes do desenvolvimento.

---

# 16. Separação de responsabilidades

## Interface

Responsável somente pela interação com o usuário.

## Models

Representam os dados.

## Repositories

Responsáveis por consultar e salvar dados.

## Services

Contêm as regras de negócio.

## Analytics

Calculam indicadores e análises.

## Reports

Geram relatórios.

## Database

Controla conexão, criação e migração do banco.

Essa separação reduzirá significativamente o risco de transformar o projeto em um script monolítico difícil de manter.

---

# 17. Tecnologia da interface

Para uma aplicação desktop Python, avaliar:

### Opção 1 — CustomTkinter

Vantagens:
- simples;
- leve;
- fácil para quem está aprendendo Python;
- boa opção para desktop.

### Opção 2 — PySide6

Vantagens:
- interface mais profissional;
- maior capacidade de crescimento;
- componentes mais completos.

Para este projeto, **PySide6 é a opção mais robusta para uma aplicação que pretende evoluir**, embora tenha uma curva de aprendizado maior.

---

# 18. Gráficos

Avaliar:

- Matplotlib
- Plotly

Para relatórios estáticos:

**Matplotlib**

Para uma interface interativa:

**Plotly**

Não utilizar várias bibliotecas para resolver o mesmo problema sem necessidade.

---

# 19. Relatório PDF

O sistema deverá gerar um relatório mensal em PDF.

Estrutura:

```text
RELATÓRIO FINANCEIRO
Agosto/2026

Resumo
├── Entradas
├── Saídas
├── Resultado
└── Taxa de economia

Despesas
├── Por categoria
├── Por forma de pagamento
└── Evolução

Orçamento
├── Planejado
├── Realizado
└── Desvios

Insights
└── Principais observações
```

O PDF deverá ser legível mesmo quando impresso.

---

# 20. Backup

Como os dados financeiros são importantes, backup não deve ser opcional.

Implementar:

- Backup manual
- Backup automático
- Restauração
- Exportação dos dados

Formato recomendado para backup:

**cópia do banco SQLite**

Também pode existir exportação para CSV para interoperabilidade.

---

# 21. Segurança e integridade

Como serão armazenados dados financeiros, considerar:

- banco local;
- validação dos valores;
- evitar valores negativos quando não permitidos;
- registro de data e hora;
- confirmação de exclusões;
- backup;
- restauração;
- tratamento de erros;
- integridade referencial no banco.

Se houver necessidade de proteger o arquivo contra acesso de terceiros, considerar posteriormente criptografia do banco ou proteção por senha.

---

# 22. Instalador

A aplicação deverá ser distribuída como programa instalável.

Fluxo desejado:

```text
Instalador
    ↓
Instala aplicação
    ↓
Cria banco local
    ↓
Cria atalhos
    ↓
Aplicação pronta
```

Para Windows, avaliar posteriormente:

- PyInstaller para empacotamento;
- Inno Setup para instalador.

O usuário final não deverá precisar instalar Python.

---

# 23. Estratégia de desenvolvimento

Não tentar construir tudo de uma vez.

## Fase 1 — Planejamento

Definir:

- requisitos;
- telas;
- banco;
- categorias;
- regras;
- fluxo de navegação.

Resultado:

**Documento de especificação do projeto.**

---

## Fase 2 — Banco de dados

Criar:

- estrutura SQLite;
- tabelas;
- relacionamentos;
- índices;
- validações.

Resultado:

**Banco funcional.**

---

## Fase 3 — Cadastro

Implementar:

- criação de movimentações;
- edição;
- exclusão;
- categorias;
- contas;
- formas de pagamento.

Resultado:

**Sistema capaz de armazenar movimentações.**

---

## Fase 4 — Consultas

Implementar:

- histórico;
- filtros;
- pesquisa;
- períodos;
- resumo financeiro.

Resultado:

**Sistema capaz de responder para onde o dinheiro está indo.**

---

## Fase 5 — Orçamento

Implementar:

- limites por categoria;
- comparação planejado x realizado;
- alertas de orçamento.

Resultado:

**Controle financeiro preventivo.**

---

## Fase 6 — Dashboard

Implementar:

- indicadores;
- gráficos;
- visão mensal;
- evolução histórica.

Resultado:

**Visão gerencial.**

---

## Fase 7 — Relatórios

Implementar:

- relatório mensal;
- gráficos;
- indicadores;
- insights;
- exportação PDF.

Resultado:

**Relatório financeiro completo.**

---

## Fase 8 — Recorrências

Implementar:

- despesas recorrentes;
- receitas recorrentes;
- geração automática.

---

## Fase 9 — Cartões

Implementar:

- cartões;
- faturas;
- parcelas;
- projeção futura.

---

## Fase 10 — Distribuição

Implementar:

- empacotamento;
- instalador;
- criação automática do banco;
- backup;
- atualização.

---

# 24. Testes

Antes de criar o instalador, testar situações críticas.

## Testes financeiros

- Entrada de R$ 1.000
- Saída de R$ 300
- Resultado esperado: R$ 700

## Testes de datas

- mudança de mês;
- ano novo;
- fevereiro;
- períodos filtrados.

## Testes de orçamento

- gasto abaixo do limite;
- gasto exatamente no limite;
- gasto acima do limite.

## Testes de recorrência

- geração correta;
- duplicação;
- alteração;
- encerramento.

## Testes de banco

- criação;
- atualização;
- exclusão;
- backup;
- restauração.

---

# 25. Regras importantes de qualidade

## Dinheiro

Nunca tratar valores monetários importantes usando cálculos de ponto flutuante sem uma estratégia adequada.

Avaliar o uso de:

**Decimal**

ou armazenamento de valores monetários em unidades inteiras, como centavos.

Exemplo conceitual:

R$ 25,90

armazenado como:

2590 centavos.

A escolha deverá ser definida durante a implementação do banco.

---

# 26. O que NÃO colocar no MVP

Evitar começar com:

- integração bancária;
- Open Finance;
- inteligência artificial;
- aplicativo mobile;
- sincronização em nuvem;
- múltiplos usuários;
- investimentos;
- criptomoedas;
- sistema complexo de cartões;
- dezenas de gráficos.

Esses recursos podem tornar o projeto excessivamente complexo antes que a função principal esteja funcionando.

O MVP precisa fazer muito bem apenas uma coisa:

> **Registrar, organizar e explicar as movimentações financeiras.**

---

# 27. Fluxo principal do usuário

```text
ABRIR APLICAÇÃO
       ↓
DASHBOARD
       ↓
┌──────────────────────┐
│ Registrar movimento  │
└──────────────────────┘
       ↓
Entrada / Saída
       ↓
Valor
       ↓
Categoria
       ↓
Descrição
       ↓
Salvar
       ↓
Dashboard atualizado
```

Esse fluxo deve ser extremamente rápido.

---

# 28. Fluxo de análise

```text
Movimentações
      ↓
Banco SQLite
      ↓
Consultas
      ↓
Indicadores
      ↓
Comparações
      ↓
Gráficos
      ↓
Insights
      ↓
Relatório mensal
```

---

# 29. Perguntas que o sistema deve responder

O projeto estará cumprindo seu objetivo se conseguir responder facilmente:

### Quanto dinheiro entrou?

### Quanto dinheiro saiu?

### Quanto sobrou?

### Onde estou gastando mais?

### Qual categoria mais cresceu?

### Quanto gasto com supermercado?

### Quanto gasto com lazer?

### Estou ultrapassando algum limite?

### Qual categoria está consumindo mais da minha renda?

### Quanto gastei no cartão?

### Quanto tenho de despesas futuras?

### Meu padrão de gastos está melhorando ou piorando?

### Quanto consegui economizar?

### Como este mês se compara aos anteriores?

Essas perguntas devem orientar o desenho do banco, das consultas e da interface.

---

# 30. Versão futura

Depois que o sistema estiver estável, poderão ser adicionados:

- importação de extratos bancários;
- leitura de CSV/OFX;
- conciliação bancária;
- cartões completos;
- projeção financeira;
- metas de economia;
- patrimônio;
- investimentos;
- sincronização;
- aplicativo mobile;
- autenticação;
- inteligência artificial para análise.

Esses recursos devem ser tratados como fases posteriores.

---

# 31. Roadmap recomendado

## MVP 1.0

- Movimentações
- Categorias
- Contas
- Formas de pagamento
- Histórico
- Filtros
- Dashboard
- Orçamento
- Relatório mensal
- Backup

## Versão 1.1

- Recorrências
- Melhorias de UX
- Exportação CSV
- Melhorias nos insights

## Versão 1.2

- Cartão de crédito
- Parcelamento
- Projeções

## Versão 2.0

- Importação de extratos
- Conciliação
- Recursos avançados de análise

---

# 32. Critério de sucesso

O sistema não deve ser avaliado pela quantidade de funcionalidades.

O principal critério é:

> **Quanto tempo o usuário leva para registrar uma movimentação e quanto esforço precisa para entender sua situação financeira.**

Se registrar uma despesa for mais trabalhoso que lançar na planilha, o projeto falhou.

Se o usuário precisar abrir cinco telas para descobrir quanto gastou com supermercado, o projeto falhou.

Se o relatório mostrar muitos gráficos mas não explicar os principais desvios, o projeto falhou.

---

# 33. Próximo passo

Antes de começar a programar, transformar este documento em uma especificação técnica contendo:

1. Requisitos funcionais
2. Requisitos não funcionais
3. Casos de uso
4. Fluxograma
5. Modelo entidade-relacionamento
6. Estrutura do banco SQLite
7. Wireframes das telas
8. Arquitetura Python
9. Plano de testes
10. Roadmap de desenvolvimento

Somente depois disso iniciar a implementação.

Essa ordem reduz retrabalho e evita que a aplicação cresça de forma desorganizada.
