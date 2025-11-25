"""
Script para verificar os dados do banco de dados.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from database.repositories import UsuarioRepository, ItemRepository

def verificar_banco():
    """Verifica os dados no banco."""
    db_path = Path(__file__).parent.parent / 'biblioteca.db'
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return
    
    print("✅ Banco de dados encontrado!")
    print(f"📁 {db_path}\n")
    
    db = DatabaseManager(str(db_path))
    
    # Verificar usuários
    usuario_repo = UsuarioRepository(db)
    usuarios = usuario_repo.listar_todos()
    
    print("👥 USUÁRIOS:")
    print("-" * 60)
    for u in usuarios:
        print(f"  ID: {u['id']} | {u['nome']} ({u['tipo']})")
        print(f"     Email: {u['email']} | CPF: {u['cpf']}")
    
    # Verificar itens
    item_repo = ItemRepository(db)
    itens = item_repo.listar_todos()
    
    print(f"\n📚 ITENS DO ACERVO:")
    print("-" * 60)
    for i in itens:
        print(f"  ID: {i['id']} | {i['nome']}")
        print(f"     Autor: {i['autor']} | Tipo: {i['tipo']}")
        print(f"     ISBN: {i['isbn']} | Categoria: {i['categoria']}")
    
    db.close()
    print("\n✅ Verificação concluída!")

if __name__ == "__main__":
    verificar_banco()
