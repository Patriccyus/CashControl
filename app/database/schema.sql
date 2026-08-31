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
    conta_id INTEGER NOT NULL,
    forma_pagamento_id INTEGER NOT NULL,
    frequencia TEXT NOT NULL CHECK (frequencia IN ('diaria', 'semanal', 'mensal', 'anual')),
    proxima_data TEXT NOT NULL,
    data_fim TEXT,
    ativo INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (categoria_id) REFERENCES categorias (id),
    FOREIGN KEY (conta_id) REFERENCES contas (id),
    FOREIGN KEY (forma_pagamento_id) REFERENCES formas_pagamento (id)
);

CREATE TABLE IF NOT EXISTS cartoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    limite INTEGER NOT NULL CHECK (limite >= 0),
    dia_fechamento INTEGER NOT NULL CHECK (dia_fechamento BETWEEN 1 AND 28),
    dia_vencimento INTEGER NOT NULL CHECK (dia_vencimento BETWEEN 1 AND 28),
    conta_id INTEGER NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (conta_id) REFERENCES contas (id)
);

CREATE TABLE IF NOT EXISTS compras_cartao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cartao_id INTEGER NOT NULL,
    categoria_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    data_compra TEXT NOT NULL,
    valor_total INTEGER NOT NULL CHECK (valor_total > 0),
    numero_parcelas INTEGER NOT NULL CHECK (numero_parcelas >= 1),
    criado_em TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (cartao_id) REFERENCES cartoes (id),
    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
);

CREATE TABLE IF NOT EXISTS parcelas_cartao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compra_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    valor INTEGER NOT NULL CHECK (valor > 0),
    fatura_mes INTEGER NOT NULL CHECK (fatura_mes BETWEEN 1 AND 12),
    fatura_ano INTEGER NOT NULL,
    FOREIGN KEY (compra_id) REFERENCES compras_cartao (id)
);

CREATE TABLE IF NOT EXISTS faturas_pagas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cartao_id INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    ano INTEGER NOT NULL,
    valor_pago INTEGER NOT NULL,
    data_pagamento TEXT NOT NULL,
    movimentacao_id INTEGER,
    FOREIGN KEY (cartao_id) REFERENCES cartoes (id),
    FOREIGN KEY (movimentacao_id) REFERENCES movimentacoes (id),
    UNIQUE (cartao_id, mes, ano)
);

CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes (data);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_categoria ON movimentacoes (categoria_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_conta ON movimentacoes (conta_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_tipo ON movimentacoes (tipo);
CREATE INDEX IF NOT EXISTS idx_orcamentos_mes_ano ON orcamentos (mes, ano);
CREATE INDEX IF NOT EXISTS idx_compras_cartao_cartao ON compras_cartao (cartao_id);
CREATE INDEX IF NOT EXISTS idx_parcelas_cartao_compra ON parcelas_cartao (compra_id);
CREATE INDEX IF NOT EXISTS idx_parcelas_cartao_fatura ON parcelas_cartao (fatura_mes, fatura_ano);
