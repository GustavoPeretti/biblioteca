# inicializar_dados.py
"""Inicializa dados padrão no banco de dados se ainda não existirem.
Isso garante que os usuários de teste (admin, bibliotecário, membro) e alguns itens estejam sempre presentes.
"""

from modelos.biblioteca import Biblioteca
from modelos.livro import Livro
from modelos.ebook import Ebook
import sqlite3


def garantir_usuarios(bib: Biblioteca):
    # Lista de usuários padrão: (nome, email, senha, cpf, tipo)
    usuarios_padrao = [
        ("Admin", "admin@biblioteca.com", "admin123", "000.000.000-00", "administrador"),
        ("Maria", "maria@biblioteca.com", "biblio123", "111.111.111-11", "bibliotecario"),
        ("João", "joao@email.com", "senha123", "222.222.222-22", "membro"),
    ]
    for nome, email, senha, cpf, tipo in usuarios_padrao:
        # Verifica se já existe usuário com esse email ou CPF
        existente_email = any(u.email == email for u in bib.usuarios)
        existente_cpf = any(u.cpf == cpf for u in bib.usuarios)
        if not (existente_email or existente_cpf):
            bib.adicionar_usuario(nome, email, senha, cpf, tipo)


def garantir_itens(bib: Biblioteca):
    # Itens de exemplo
    itens_padrao = [
        Livro("O Senhor dos Anéis", None, None, "J.R.R. Tolkien", 1178, "978-0-618-00222-8", "Fantasia"),
        Livro("Dom Casmurro", None, None, "Machado de Assis", 256, "978-85-352-0010-9", "Romance"),
        Ebook("Clean Code", None, None, "Robert Martin", 464, "978-0-13-235088-4", "Programação", None, None),
    ]
    for item in itens_padrao:
        # Tenta inserir o item; se já existir (violação de UNIQUE), ignora
        try:
            bib.adicionar_item(item)
        except sqlite3.IntegrityError:
            # Item já está no banco, ignoramos a duplicação
            pass


def inicializar():
    bib = Biblioteca()
    try:
        garantir_usuarios(bib)
        garantir_itens(bib)
    finally:
        # Garantir fechamento da conexão com o banco para não manter locks
        try:
            bib.db.close()
        except Exception:
            pass

if __name__ == "__main__":
    inicializar()
