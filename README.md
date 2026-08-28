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

## Estrutura

- `app/database` — conexão, schema e seed do SQLite
- `app/models` — dataclasses das entidades
- `app/repositories` — acesso e persistência dos dados
- `app/services` — regras de negócio (validação, sugestão de categoria, orçamento)
- `app/analytics` — indicadores do dashboard e consumo de orçamento
- `app/reports` — geração de relatórios (em construção)
- `app/interface/cli.py` — interface de linha de comando
- `app/interface/gui` — interface gráfica em PySide6 (dashboard, lançamento, histórico, orçamento)

## Status

Fase 1 (planejamento), Fase 2 (banco de dados), Fase 3 (cadastro), Fase 4
(consultas: histórico com filtros), Fase 5 (orçamento) e Fase 6 (dashboard
gráfico em PySide6, com indicadores e gráficos de entradas/saídas, gastos
por categoria e orçamento) concluídas. Próxima etapa: Fase 7 — relatório
mensal em PDF.
