PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    ativo INTEGER NOT NULL DEFAULT 1,
    categoria_pai_id INTEGER,
    FOREIGN KEY (categoria_pai_id) REFERENCES categorias (id)
);

CREATE TABLE IF NOT EXISTS contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('banco', 'conta_corrente', 'poupanca', 'dinheiro', 'carteira_digital')),
    saldo_inicial INTEGER NOT NULL DEFAULT 0,
    ativo INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS formas_pagamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('pix', 'debito', 'credito', 'dinheiro', 'boleto', 'transferencia')),
    ativo INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    descricao TEXT NOT NULL,
    valor INTEGER NOT NULL CHECK (valor > 0),
    categoria_id INTEGER NOT NULL,
    subcategoria_id INTEGER,
    conta_id INTEGER NOT NULL,
    forma_pagamento_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pago' CHECK (status IN ('pago', 'pendente')),
    observacao TEXT,
    criado_em TEXT NOT NULL DEFAULT (datetime('now')),
    atualizado_em TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (categoria_id) REFERENCES categorias (id),
    FOREIGN KEY (subcategoria_id) REFERENCES categorias (id),
    FOREIGN KEY (conta_id) REFERENCES contas (id),
    FOREIGN KEY (forma_pagamento_id) REFERENCES formas_pagamento (id)
);

CREATE TABLE IF NOT EXISTS orcamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria_id INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    ano INTEGER NOT NULL,
    limite INTEGER NOT NULL CHECK (limite >= 0),
    FOREIGN KEY (categoria_id) REFERENCES categorias (id),
    UNIQUE (categoria_id, mes, ano)
);

CREATE TABLE IF NOT EXISTS recorrencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    valor INTEGER NOT NULL CHECK (valor > 0),
    categoria_id INTEGER NOT NULL,
    frequencia TEXT NOT NULL CHECK (frequencia IN ('diaria', 'semanal', 'mensal', 'anual')),
    proxima_data TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
);

CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes (data);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_categoria ON movimentacoes (categoria_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_conta ON movimentacoes (conta_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_tipo ON movimentacoes (tipo);
CREATE INDEX IF NOT EXISTS idx_orcamentos_mes_ano ON orcamentos (mes, ano);
