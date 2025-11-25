"""
Repositories para acesso aos dados do banco.
Implementa o padrão Repository para cada entidade.
"""

from datetime import datetime


class UsuarioRepository:
    """Repository para gerenciar usuários no banco de dados."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def criar(self, nome, email, senha, cpf, tipo):
        """Cria um novo usuário no banco de dados."""
        query = """
            INSERT INTO usuarios (nome, email, senha, cpf, tipo)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.db.execute_query(query, (nome, email, senha, cpf, tipo))
        self.db.commit()
        return cursor.lastrowid
    
    def buscar_por_id(self, id):
        """Busca usuário por ID."""
        query = "SELECT * FROM usuarios WHERE id = ?"
        return self.db.fetch_one(query, (id,))
    
    def buscar_por_email(self, email):
        """Busca usuário por email."""
        query = "SELECT * FROM usuarios WHERE email = ?"
        return self.db.fetch_one(query, (email,))
    
    def buscar_por_cpf(self, cpf):
        """Busca usuário por CPF."""
        query = "SELECT * FROM usuarios WHERE cpf = ?"
        return self.db.fetch_one(query, (cpf,))
    
    def listar_todos(self):
        """Lista todos os usuários."""
        query = "SELECT * FROM usuarios ORDER BY nome"
        return self.db.fetch_all(query)
    
    def listar_por_tipo(self, tipo):
        """Lista usuários por tipo."""
        query = "SELECT * FROM usuarios WHERE tipo = ? ORDER BY nome"
        return self.db.fetch_all(query, (tipo,))
    
    def atualizar(self, id, nome=None, email=None, senha=None, cpf=None):
        """Atualiza dados do usuário."""
        campos = []
        valores = []
        
        if nome is not None:
            campos.append("nome = ?")
            valores.append(nome)
        if email is not None:
            campos.append("email = ?")
            valores.append(email)
        if senha is not None:
            campos.append("senha = ?")
            valores.append(senha)
        if cpf is not None:
            campos.append("cpf = ?")
            valores.append(cpf)
        
        if not campos:
            return
        
        valores.append(id)
        query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = ?"
        self.db.execute_query(query, tuple(valores))
        self.db.commit()
    
    def deletar(self, id):
        """Remove usuário do banco."""
        query = "DELETE FROM usuarios WHERE id = ?"
        self.db.execute_query(query, (id,))
        self.db.commit()


class ItemRepository:
    """Repository para gerenciar itens (livros e ebooks)."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def criar(self, tipo, nome, autor, num_paginas, isbn, categoria, 
              imagem_url=None, imagem_arquivo=None, emprestavel=True, 
              arquivo=None, url=None):
        """Cria um novo item no banco de dados."""
        query = """
            INSERT INTO itens (tipo, nome, imagem_url, imagem_arquivo, autor, 
                             num_paginas, isbn, categoria, emprestavel, arquivo, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute_query(query, (
            tipo, nome, imagem_url, imagem_arquivo, autor, 
            num_paginas, isbn, categoria, emprestavel, arquivo, url
        ))
        self.db.commit()
        return cursor.lastrowid
    
    def buscar_por_id(self, id):
        """Busca item por ID."""
        query = "SELECT * FROM itens WHERE id = ?"
        return self.db.fetch_one(query, (id,))
    
    def buscar_por_isbn(self, isbn):
        """Busca item por ISBN."""
        query = "SELECT * FROM itens WHERE isbn = ?"
        return self.db.fetch_one(query, (isbn,))
    
    def listar_todos(self):
        """Lista todos os itens."""
        query = "SELECT * FROM itens ORDER BY nome"
        return self.db.fetch_all(query)
    
    def listar_por_tipo(self, tipo):
        """Lista itens por tipo (livro ou ebook)."""
        query = "SELECT * FROM itens WHERE tipo = ? ORDER BY nome"
        return self.db.fetch_all(query, (tipo,))
    
    def buscar_por_nome(self, nome):
        """Busca itens por nome (busca parcial)."""
        query = "SELECT * FROM itens WHERE nome LIKE ? ORDER BY nome"
        return self.db.fetch_all(query, (f'%{nome}%',))
    
    def listar_por_categoria(self, categoria):
        """Lista itens por categoria."""
        query = "SELECT * FROM itens WHERE categoria = ? ORDER BY nome"
        return self.db.fetch_all(query, (categoria,))
    
    def atualizar(self, id, **kwargs):
        """Atualiza dados do item."""
        campos = []
        valores = []
        
        campos_permitidos = ['nome', 'autor', 'num_paginas', 'isbn', 'categoria',
                            'imagem_url', 'imagem_arquivo', 'emprestavel', 'arquivo', 'url']
        
        for campo in campos_permitidos:
            if campo in kwargs and kwargs[campo] is not None:
                campos.append(f"{campo} = ?")
                valores.append(kwargs[campo])
        
        if not campos:
            return
        
        valores.append(id)
        query = f"UPDATE itens SET {', '.join(campos)} WHERE id = ?"
        self.db.execute_query(query, tuple(valores))
        self.db.commit()
    
    def deletar(self, id):
        """Remove item do banco."""
        query = "DELETE FROM itens WHERE id = ?"
        self.db.execute_query(query, (id,))
        self.db.commit()


class EmprestimoRepository:
    """Repository para gerenciar empréstimos."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def criar(self, item_id, membro_id):
        """Cria um novo empréstimo."""
        query = """
            INSERT INTO emprestimos (item_id, membro_id, data_emprestimo, status)
            VALUES (?, ?, ?, 'ativo')
        """
        cursor = self.db.execute_query(query, (item_id, membro_id, datetime.now()))
        self.db.commit()
        return cursor.lastrowid
    
    def buscar_por_id(self, id):
        """Busca empréstimo por ID."""
        query = """
            SELECT e.*, 
                   i.nome as item_nome, i.autor as item_autor,
                   u.nome as membro_nome, u.email as membro_email
            FROM emprestimos e
            JOIN itens i ON e.item_id = i.id
            JOIN usuarios u ON e.membro_id = u.id
            WHERE e.id = ?
        """
        return self.db.fetch_one(query, (id,))
    
    def listar_todos(self):
        """Lista todos os empréstimos."""
        query = """
            SELECT e.*, 
                   i.nome as item_nome, i.autor as item_autor,
                   u.nome as membro_nome, u.email as membro_email
            FROM emprestimos e
            JOIN itens i ON e.item_id = i.id
            JOIN usuarios u ON e.membro_id = u.id
            ORDER BY e.data_emprestimo DESC
        """
        return self.db.fetch_all(query)
    
    def listar_ativos(self):
        """Lista empréstimos ativos."""
        query = """
            SELECT e.*, 
                   i.nome as item_nome, i.autor as item_autor,
                   u.nome as membro_nome, u.email as membro_email
            FROM emprestimos e
            JOIN itens i ON e.item_id = i.id
            JOIN usuarios u ON e.membro_id = u.id
            WHERE e.status = 'ativo'
            ORDER BY e.data_emprestimo DESC
        """
        return self.db.fetch_all(query)
    
    def listar_por_membro(self, membro_id):
        """Lista empréstimos de um membro."""
        query = """
            SELECT e.*, 
                   i.nome as item_nome, i.autor as item_autor
            FROM emprestimos e
            JOIN itens i ON e.item_id = i.id
            WHERE e.membro_id = ?
            ORDER BY e.data_emprestimo DESC
        """
        return self.db.fetch_all(query, (membro_id,))
    
    def listar_por_item(self, item_id):
        """Lista empréstimos de um item."""
        query = """
            SELECT e.*, 
                   u.nome as membro_nome, u.email as membro_email
            FROM emprestimos e
            JOIN usuarios u ON e.membro_id = u.id
            WHERE e.item_id = ?
            ORDER BY e.data_emprestimo DESC
        """
        return self.db.fetch_all(query, (item_id,))
    
    def atualizar_status(self, id, status, data_devolucao=None, data_quitacao=None):
        """Atualiza status do empréstimo."""
        query = "UPDATE emprestimos SET status = ?"
        params = [status]
        
        if data_devolucao:
            query += ", data_devolucao = ?"
            params.append(data_devolucao)
        
        if data_quitacao:
            query += ", data_quitacao = ?"
            params.append(data_quitacao)
        
        query += " WHERE id = ?"
        params.append(id)
        
        self.db.execute_query(query, tuple(params))
        self.db.commit()
    
    def renovar(self, id):
        """Incrementa contador de renovações."""
        query = """
            UPDATE emprestimos 
            SET quantidade_renovacoes = quantidade_renovacoes + 1
            WHERE id = ?
        """
        self.db.execute_query(query, (id,))
        self.db.commit()
    
    def deletar(self, id):
        """Remove empréstimo do banco."""
        query = "DELETE FROM emprestimos WHERE id = ?"
        self.db.execute_query(query, (id,))
        self.db.commit()


class ReservaRepository:
    """Repository para gerenciar reservas."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def criar(self, item_id, membro_id):
        """Cria uma nova reserva."""
        query = """
            INSERT INTO reservas (item_id, membro_id, data_reserva, status)
            VALUES (?, ?, ?, 'aguardando')
        """
        cursor = self.db.execute_query(query, (item_id, membro_id, datetime.now()))
        self.db.commit()
        return cursor.lastrowid
    
    def buscar_por_id(self, id):
        """Busca reserva por ID."""
        query = """
            SELECT r.*, 
                   i.nome as item_nome, i.autor as item_autor,
                   u.nome as membro_nome, u.email as membro_email
            FROM reservas r
            JOIN itens i ON r.item_id = i.id
            JOIN usuarios u ON r.membro_id = u.id
            WHERE r.id = ?
        """
        return self.db.fetch_one(query, (id,))
    
    def listar_todas(self):
        """Lista todas as reservas."""
        query = """
            SELECT r.*, 
                   i.nome as item_nome, i.autor as item_autor,
                   u.nome as membro_nome, u.email as membro_email
            FROM reservas r
            JOIN itens i ON r.item_id = i.id
            JOIN usuarios u ON r.membro_id = u.id
            ORDER BY r.data_reserva DESC
        """
        return self.db.fetch_all(query)
    
    def listar_ativas(self):
        """Lista reservas ativas (aguardando)."""
        query = """
            SELECT r.*, 
                   i.nome as item_nome, i.autor as item_autor,
                   u.nome as membro_nome, u.email as membro_email
            FROM reservas r
            JOIN itens i ON r.item_id = i.id
            JOIN usuarios u ON r.membro_id = u.id
            WHERE r.status = 'aguardando'
            ORDER BY r.data_reserva ASC
        """
        return self.db.fetch_all(query)
    
    def listar_por_membro(self, membro_id):
        """Lista reservas de um membro."""
        query = """
            SELECT r.*, 
                   i.nome as item_nome, i.autor as item_autor
            FROM reservas r
            JOIN itens i ON r.item_id = i.id
            WHERE r.membro_id = ?
            ORDER BY r.data_reserva DESC
        """
        return self.db.fetch_all(query, (membro_id,))
    
    def listar_por_item(self, item_id):
        """Lista reservas de um item (fila de espera)."""
        query = """
            SELECT r.*, 
                   u.nome as membro_nome, u.email as membro_email
            FROM reservas r
            JOIN usuarios u ON r.membro_id = u.id
            WHERE r.item_id = ? AND r.status = 'aguardando'
            ORDER BY r.data_reserva ASC
        """
        return self.db.fetch_all(query, (item_id,))
    
    def atualizar_status(self, id, status, data_cancelamento=None, data_finalizacao=None):
        """Atualiza status da reserva."""
        query = "UPDATE reservas SET status = ?"
        params = [status]
        
        if data_cancelamento:
            query += ", data_cancelamento = ?"
            params.append(data_cancelamento)
        
        if data_finalizacao:
            query += ", data_finalizacao = ?"
            params.append(data_finalizacao)
        
        query += " WHERE id = ?"
        params.append(id)
        
        self.db.execute_query(query, tuple(params))
        self.db.commit()
    
    def deletar(self, id):
        """Remove reserva do banco."""
        query = "DELETE FROM reservas WHERE id = ?"
        self.db.execute_query(query, (id,))
        self.db.commit()


class MultaRepository:
    """Repository para gerenciar multas."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def criar(self, emprestimo_id, valor):
        """Cria uma nova multa."""
        query = """
            INSERT INTO multas (emprestimo_id, valor, paga)
            VALUES (?, ?, 0)
        """
        cursor = self.db.execute_query(query, (emprestimo_id, valor))
        self.db.commit()
        return cursor.lastrowid
    
    def buscar_por_emprestimo(self, emprestimo_id):
        """Busca multa por empréstimo."""
        query = "SELECT * FROM multas WHERE emprestimo_id = ?"
        return self.db.fetch_one(query, (emprestimo_id,))
    
    def listar_todas(self):
        """Lista todas as multas."""
        query = """
            SELECT m.*, 
                   e.membro_id,
                   u.nome as membro_nome,
                   i.nome as item_nome
            FROM multas m
            JOIN emprestimos e ON m.emprestimo_id = e.id
            JOIN usuarios u ON e.membro_id = u.id
            JOIN itens i ON e.item_id = i.id
            ORDER BY m.data_criacao DESC
        """
        return self.db.fetch_all(query)
    
    def listar_pendentes(self):
        """Lista multas não pagas."""
        query = """
            SELECT m.*, 
                   e.membro_id,
                   u.nome as membro_nome,
                   i.nome as item_nome
            FROM multas m
            JOIN emprestimos e ON m.emprestimo_id = e.id
            JOIN usuarios u ON e.membro_id = u.id
            JOIN itens i ON e.item_id = i.id
            WHERE m.paga = 0
            ORDER BY m.data_criacao DESC
        """
        return self.db.fetch_all(query)
    
    def marcar_como_paga(self, emprestimo_id):
        """Marca multa como paga."""
        query = "UPDATE multas SET paga = 1 WHERE emprestimo_id = ?"
        self.db.execute_query(query, (emprestimo_id,))
        self.db.commit()
    
    def atualizar_valor(self, emprestimo_id, novo_valor):
        """Atualiza valor da multa."""
        query = "UPDATE multas SET valor = ? WHERE emprestimo_id = ?"
        self.db.execute_query(query, (novo_valor, emprestimo_id))
        self.db.commit()
