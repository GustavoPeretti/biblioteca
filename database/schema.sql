-- Schema do Banco de Dados SQLite para Sistema de Biblioteca
-- Criado em: 2025-11-25

-- ============================================
-- TABELA: usuarios
-- Armazena todos os tipos de usuários (Administrador, Bibliotecário, Membro)
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('administrador', 'bibliotecario', 'membro')),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhorar performance de buscas
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_cpf ON usuarios(cpf);
CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo);

-- ============================================
-- TABELA: itens
-- Armazena livros e ebooks do acervo
-- ============================================
CREATE TABLE IF NOT EXISTS itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK(tipo IN ('livro', 'ebook')),
    nome TEXT NOT NULL,
    imagem_url TEXT,
    imagem_arquivo TEXT,
    autor TEXT NOT NULL,
    num_paginas INTEGER,
    isbn TEXT UNIQUE,
    categoria TEXT,
    emprestavel BOOLEAN DEFAULT 1,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Campos específicos para ebooks
    arquivo TEXT,
    url TEXT
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_itens_tipo ON itens(tipo);
CREATE INDEX IF NOT EXISTS idx_itens_isbn ON itens(isbn);
CREATE INDEX IF NOT EXISTS idx_itens_categoria ON itens(categoria);
CREATE INDEX IF NOT EXISTS idx_itens_nome ON itens(nome);

-- ============================================
-- TABELA: emprestimos
-- Registra todos os empréstimos (ativos, multados, finalizados)
-- ============================================
CREATE TABLE IF NOT EXISTS emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    membro_id INTEGER NOT NULL,
    data_emprestimo TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_devolucao TIMESTAMP,
    data_quitacao TIMESTAMP,
    quantidade_renovacoes INTEGER DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('ativo', 'multado', 'finalizado')) DEFAULT 'ativo',
    FOREIGN KEY (item_id) REFERENCES itens(id) ON DELETE CASCADE,
    FOREIGN KEY (membro_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_emprestimos_item ON emprestimos(item_id);
CREATE INDEX IF NOT EXISTS idx_emprestimos_membro ON emprestimos(membro_id);
CREATE INDEX IF NOT EXISTS idx_emprestimos_status ON emprestimos(status);
CREATE INDEX IF NOT EXISTS idx_emprestimos_data ON emprestimos(data_emprestimo);

-- ============================================
-- TABELA: reservas
-- Registra reservas de itens emprestados
-- ============================================
CREATE TABLE IF NOT EXISTS reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    membro_id INTEGER NOT NULL,
    data_reserva TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_cancelamento TIMESTAMP,
    data_finalizacao TIMESTAMP,
    status TEXT NOT NULL CHECK(status IN ('aguardando', 'cancelada', 'expirada', 'finalizada')) DEFAULT 'aguardando',
    FOREIGN KEY (item_id) REFERENCES itens(id) ON DELETE CASCADE,
    FOREIGN KEY (membro_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_reservas_item ON reservas(item_id);
CREATE INDEX IF NOT EXISTS idx_reservas_membro ON reservas(membro_id);
CREATE INDEX IF NOT EXISTS idx_reservas_status ON reservas(status);
CREATE INDEX IF NOT EXISTS idx_reservas_data ON reservas(data_reserva);

-- ============================================
-- TABELA: multas
-- Registra multas associadas a empréstimos atrasados
-- ============================================
CREATE TABLE IF NOT EXISTS multas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emprestimo_id INTEGER NOT NULL UNIQUE,
    valor REAL NOT NULL,
    paga BOOLEAN DEFAULT 0,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(id) ON DELETE CASCADE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_multas_emprestimo ON multas(emprestimo_id);
CREATE INDEX IF NOT EXISTS idx_multas_paga ON multas(paga);

-- ============================================
-- TABELA: configuracoes
-- Armazena configurações do sistema
-- ============================================
CREATE TABLE IF NOT EXISTS configuracoes (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL,
    descricao TEXT
);

-- Inserir configurações padrão
INSERT OR IGNORE INTO configuracoes (chave, valor, descricao) VALUES
    ('prazo_devolucao', '15', 'Prazo em dias para devolução de itens'),
    ('multa_por_dia', '1', 'Valor da multa por dia de atraso'),
    ('limite_emprestimos', '15', 'Limite de empréstimos simultâneos por membro'),
    ('limite_renovacoes', '15', 'Limite de renovações por empréstimo'),
    ('prazo_validade_reserva', '3', 'Prazo em dias para validade de reserva');
