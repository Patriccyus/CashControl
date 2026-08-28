# Controle Financeiro

Aplicação desktop em Python para controle financeiro pessoal. Ver
[projeto_controle_financeiro_python.md](projeto_controle_financeiro_python.md)
para a especificação completa.

## Uso

```bash
pip install -r requirements.txt
python main.py     # cria o banco SQLite em data/controle_financeiro.db
pytest              # roda os testes
```

## Estrutura

- `app/database` — conexão, schema e seed do SQLite
- `app/models` — dataclasses das entidades
- `app/repositories` — acesso e persistência dos dados
- `app/services` — regras de negócio (em construção)
- `app/analytics` — indicadores e insights (em construção)
- `app/reports` — geração de relatórios (em construção)
- `app/interface` — interface gráfica (em construção)

## Status

Fase 1 (planejamento), Fase 2 (banco de dados), Fase 3 (cadastro), Fase 4
(consultas: histórico com filtros) e Fase 5 (orçamento: limites por
categoria e alerta de consumo) concluídas. Próxima etapa: Fase 6 —
dashboard com indicadores e gráficos (interface gráfica em PySide6).
