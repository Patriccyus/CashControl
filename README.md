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

Fase 1 (planejamento) e Fase 2 (banco de dados) concluídas. Próxima etapa:
Fase 3 — cadastro (services + interface de lançamento).
