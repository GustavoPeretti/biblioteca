"""
Adaptador para integrar o banco de dados com as classes existentes do modelo.
Converte entre objetos Python e registros do banco de dados.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modelos.administrador import Administrador
from modelos.bibliotecario import Bibliotecario
from modelos.membro import Membro
from modelos.livro import Livro
from modelos.ebook import Ebook
from modelos.emprestimo import Emprestimo
from modelos.reserva import Reserva
from modelos.multa import Multa
from datetime import datetime



class DatabaseAdapter:
    """Adaptador para converter entre objetos do modelo e registros do banco."""
    
    @staticmethod
    def row_to_usuario(row):
        """Converte uma linha do banco para objeto Usuario."""
        if not row:
            return None
        
        # Criar objeto baseado no tipo
        tipo = row['tipo']
        if tipo == 'administrador':
            usuario = Administrador(row['nome'], row['email'], row['senha'], row['cpf'])
        elif tipo == 'bibliotecario':
            usuario = Bibliotecario(row['nome'], row['email'], row['senha'], row['cpf'])
        elif tipo == 'membro':
            usuario = Membro(row['nome'], row['email'], row['senha'], row['cpf'])
        else:
            raise ValueError(f"Tipo de usuário desconhecido: {tipo}")
        
        # Substituir o ID gerado pelo UUID com o ID do banco
        usuario._id = row['id']
        # Adicionar atributo tipo para compatibilidade com interface
        usuario.tipo = tipo
        
        return usuario
    
    @staticmethod
    def row_to_item(row):
        """Converte uma linha do banco para objeto Item (Livro ou Ebook)."""
        if not row:
            return None
        
        tipo = row['tipo']
        
        if tipo == 'livro':
            item = Livro(
                nome=row['nome'],
                imagem_url=row['imagem_url'],
                imagem_arquivo=row['imagem_arquivo'],
                autor=row['autor'],
                num_paginas=row['num_paginas'],
                isbn=row['isbn'],
                categoria=row['categoria']
            )
        elif tipo == 'ebook':
            item = Ebook(
                nome=row['nome'],
                imagem_url=row['imagem_url'],
                imagem_arquivo=row['imagem_arquivo'],
                autor=row['autor'],
                num_paginas=row['num_paginas'],
                isbn=row['isbn'],
                categoria=row['categoria'],
                arquivo=row['arquivo'],
                url=row['url']
            )
        else:
            raise ValueError(f"Tipo de item desconhecido: {tipo}")
        
        # Substituir o ID gerado pelo UUID com o ID do banco
        item._id = row['id']
        item._emprestavel = bool(row['emprestavel'])
        
        # Converter data de cadastro se for string
        if isinstance(row['data_cadastro'], str):
            item._data_cadastro = datetime.fromisoformat(row['data_cadastro'])
        
        return item
    
    @staticmethod
    def usuario_to_dict(usuario):
        """Converte objeto Usuario para dicionário para inserção no banco."""
        return {
            'nome': usuario.nome,
            'email': usuario.email,
            'senha': usuario.senha,
            'cpf': usuario.cpf,
            'tipo': usuario.tipo
        }
    
    @staticmethod
    def item_to_dict(item):
        """Converte objeto Item para dicionário para inserção no banco."""
        from modelos.ebook import Ebook
        
        data = {
            'tipo': 'ebook' if isinstance(item, Ebook) else 'livro',
            'nome': item.nome,
            'imagem_url': item.imagem_url,
            'imagem_arquivo': item.imagem_arquivo,
            'autor': item.autor,
            'num_paginas': item.num_paginas,
            'isbn': item.isbn,
            'categoria': item.categoria,
            'emprestavel': item.emprestavel
        }
        
        # Adicionar campos específicos de ebook
        if isinstance(item, Ebook):
            data['arquivo'] = item.arquivo
            data['url'] = item.url
        else:
            data['arquivo'] = None
            data['url'] = None
        
        return data

    @staticmethod
    def row_to_emprestimo(row, item, membro):
        """Converte uma linha do banco para objeto Emprestimo."""
        if not row:
            return None
        
        emprestimo = Emprestimo(item, membro)
        
        # Substituir atributos privados
        emprestimo._id = row['id']
        
        if isinstance(row['data_emprestimo'], str):
            emprestimo._data_emprestimo = datetime.fromisoformat(row['data_emprestimo'])
        else:
            emprestimo._data_emprestimo = row['data_emprestimo']
            
        if row['data_devolucao']:
            if isinstance(row['data_devolucao'], str):
                emprestimo._data_devolucao = datetime.fromisoformat(row['data_devolucao'])
            else:
                emprestimo._data_devolucao = row['data_devolucao']
                
        if row['data_quitacao']:
            if isinstance(row['data_quitacao'], str):
                emprestimo._data_quitacao = datetime.fromisoformat(row['data_quitacao'])
            else:
                emprestimo._data_quitacao = row['data_quitacao']
                
        emprestimo._quantidade_renovacoes = row['quantidade_renovacoes']
        emprestimo._status = row['status']
        
        return emprestimo

    @staticmethod
    def row_to_reserva(row, item, membro):
        """Converte uma linha do banco para objeto Reserva."""
        if not row:
            return None
        
        reserva = Reserva(item, membro)
        
        # Substituir atributos privados
        reserva._id = row['id']
        
        if isinstance(row['data_reserva'], str):
            reserva._data_reserva = datetime.fromisoformat(row['data_reserva'])
        else:
            reserva._data_reserva = row['data_reserva']
            
        if row['data_cancelamento']:
            if isinstance(row['data_cancelamento'], str):
                reserva._data_cancelamento = datetime.fromisoformat(row['data_cancelamento'])
            else:
                reserva._data_cancelamento = row['data_cancelamento']
                
        if row['data_finalizacao']:
            if isinstance(row['data_finalizacao'], str):
                reserva._data_finalizacao = datetime.fromisoformat(row['data_finalizacao'])
            else:
                reserva._data_finalizacao = row['data_finalizacao']
                
        reserva._status = row['status']
        
        return reserva
