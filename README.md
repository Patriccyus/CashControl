# Controle Financeiro

Aplicação desktop em Python para controle financeiro pessoal. Ver
[projeto_controle_financeiro_python.md](projeto_controle_financeiro_python.md)
para a especificação completa.

## Uso

```bash
pip install -r requirements.txt
python main.py       # abre a interface gráfica (PySide6)
python main.py --cli # interface de linha de comando (alternativa)
pytest                # roda os testes
```

## Perfis

O app abre com uma tela de login. Cada perfil (ex: "Tiago", "Débora") tem
senha própria e um banco SQLite totalmente separado dos demais —
`data/perfis/<nome>.db`. O cadastro de perfis fica num banco à parte,
`data/perfis.db` (nome, hash da senha com salt via PBKDF2, nunca a senha
em si). Ao criar o **primeiro** perfil, se já existir o banco antigo
(`data/controle_financeiro.db`, de antes dessa funcionalidade existir),
ele é copiado automaticamente para virar os dados desse perfil — o
arquivo antigo não é apagado, fica como estava.

## Estrutura

- `app/database` — conexão, schema e seed do SQLite (dados financeiros) e do registro de perfis
- `app/models` — dataclasses das entidades
- `app/repositories` — acesso e persistência dos dados
- `app/services` — regras de negócio (validação, sugestão de categoria, orçamento, perfis)
- `app/analytics` — indicadores do dashboard, consumo de orçamento, insights e relatório mensal
- `app/reports` — geração do relatório mensal em PDF
- `app/interface/cli.py` — interface de linha de comando
- `app/interface/gui` — interface gráfica em PySide6 (login, dashboard, lançamento, histórico, orçamento, relatório, recorrências, cartão de crédito, contas)

## Status

Fase 1 (planejamento), Fase 2 (banco de dados), Fase 3 (cadastro), Fase 4
(consultas: histórico com filtros), Fase 5 (orçamento), Fase 6 (dashboard
gráfico em PySide6), Fase 7 (relatório mensal em PDF, com insights por
regras determinísticas), Fase 8 (despesas e receitas recorrentes, com
geração automática de lançamentos pendentes ao abrir o app) e Fase 9
(cartão de crédito: compras parceladas, faturas por fechamento/vencimento,
pagamento gerando movimentação, projeção de despesas futuras) concluídas.

Também foram adicionadas, além do roadmap original: uma tela de cadastro
de contas (banco, poupança, carteira digital etc.), que já existia como
serviço desde a Fase 3 mas não tinha interface própria; edição/exclusão
de movimentações no Histórico (GUI) e via novas opções na CLI, incluindo
a confirmação antes de excluir pedida na seção 6 do documento; e login
com múltiplos perfis, cada um com seu próprio banco de dados isolado
(o documento original listava "múltiplos usuários" como fora do escopo
do MVP — essa é uma extensão pedida depois que o núcleo já estava pronto).

Próxima etapa: Fase 10 — empacotamento e instalador Windows.
