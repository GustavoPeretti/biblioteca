"""
Script para inicializar o banco de dados SQLite.
Cria as tabelas e popula com dados de exemplo.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from database.repositories import (
    UsuarioRepository,
    ItemRepository,
    EmprestimoRepository,
    ReservaRepository
)
import sqlite3


def inicializar_banco():
    """Inicializa o banco de dados e popula com dados de exemplo."""
    
    # Caminho do banco de dados (na raiz do projeto)
    db_path = Path(__file__).parent.parent / 'biblioteca.db'
    
    print("🗄️  Inicializando banco de dados...")
    print(f"📁 Caminho: {db_path}")
    
    # Detectar se o arquivo do banco já existia antes — se não, trata-se de criação nova
    db_existed = db_path.exists()
    
    # Criar gerenciador do banco
    db = DatabaseManager(str(db_path))
    
    # Criar tabelas
    print("📋 Criando tabelas...")
    db.create_tables()
    print("✅ Tabelas criadas com sucesso!")
    
    # Criar repositories
    usuario_repo = UsuarioRepository(db)
    item_repo = ItemRepository(db)

    # Garantir que apenas os 3 usuários desejados existam no banco.
    # Esta operação remove quaisquer outros usuários existentes (e, devido a
    # FOREIGN KEY ... ON DELETE CASCADE, também remove empréstimos/reservas vinculados).
    # Foi decidido explicitamente manter esse comportamento para garantir que o banco
    # inicial seja sempre populado com apenas as contas de teste especificadas.
    try:
        print("\n🧹 Normalizando usuários: removendo usuários existentes e criando usuários padrão...")
        # Remover todos os usuários (cascata para registros dependentes)
        db.execute_query("DELETE FROM usuarios")
        db.commit()

        # Inserir os três usuários desejados
        admin_id = usuario_repo.criar(
            nome="Admin",
            email="admin@biblioteca.com",
            senha="admin123",
            cpf="000.000.000-00",
            tipo="administrador"
        )
        print(f"    ✓ Administrador criado (ID: {admin_id})")

        bib_id = usuario_repo.criar(
            nome="Maria",
            email="maria@biblioteca.com",
            senha="biblio123",
            cpf="111.111.111-11",
            tipo="bibliotecario"
        )
        print(f"    ✓ Bibliotecário criado (ID: {bib_id})")

        membro_id = usuario_repo.criar(
            nome="João",
            email="joao@email.com",
            senha="senha123",
            cpf="222.222.222-22",
            tipo="membro"
        )
        print(f"    ✓ Membro criado (ID: {membro_id})")

    except Exception as e:
        print(f"Aviso: falha ao normalizar/ inserir usuários de teste: {e}")
    # Inserir itens de exemplo (ignorar duplicações de ISBN)
    try:
        item1_id = item_repo.criar(
            tipo="livro",
            nome="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            num_paginas=1200,
            isbn="978-8533613379",
            categoria="Fantasia"
        )
        print(f"    ✓ Livro criado: O Senhor dos Anéis (ID: {item1_id})")
    except sqlite3.IntegrityError:
        print("    ⚠️  Livro 'O Senhor dos Anéis' já existe (ISBN duplicado). Ignorando.")

    try:
        item2_id = item_repo.criar(
            tipo="livro",
            nome="1984",
            autor="George Orwell",
            num_paginas=416,
            isbn="978-8535914849",
            categoria="Ficção Científica"
        )
        print(f"    ✓ Livro criado: 1984 (ID: {item2_id})")
    except sqlite3.IntegrityError:
        print("    ⚠️  Livro '1984' já existe (ISBN duplicado). Ignorando.")

    try:
        item3_id = item_repo.criar(
            tipo="ebook",
            nome="Clean Code",
            autor="Robert C. Martin",
            num_paginas=464,
            isbn="978-0132350884",
            categoria="Tecnologia",
            url="https://exemplo.com/clean-code.pdf"
        )
        print(f"    ✓ Ebook criado: Clean Code (ID: {item3_id})")
    except sqlite3.IntegrityError:
        print("    ⚠️  Ebook 'Clean Code' já existe (ISBN duplicado). Ignorando.")
    
    # Confirmar mudanças
    db.commit()
    
    print("\n✅ Banco de dados inicializado com sucesso!")
    print(f"📊 Resumo:")
    print(f"   - {len(usuario_repo.listar_todos())} usuários")
    print(f"   - {len(item_repo.listar_todos())} itens")
    
    # Fechar conexão
    db.close()
    print("\n🔒 Conexão fechada.")


if __name__ == "__main__":
    try:
        inicializar_banco()
    except Exception as e:
        print(f"\n❌ Erro ao inicializar banco de dados: {e}")
        sys.exit(1)
