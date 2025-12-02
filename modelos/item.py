from abc import ABC, abstractmethod
from uuid import uuid4
import datetime
import re

class Item(ABC):
    def __init__(self, nome, imagem_url, imagem_arquivo, autor, num_paginas, isbn, categoria):
        self._id = uuid4()
        self._imagem_url = imagem_url
        self._imagem_arquivo = imagem_arquivo
        self._emprestavel = True
        self._data_cadastro = datetime.datetime.now()
        # Usar os setters para aplicar validações
        self.nome = nome
        self.autor = autor
        self.num_paginas = num_paginas
        self.isbn = isbn
        self.categoria = categoria

    @property
    def id(self):
        return self._id
    
    @property
    def nome(self):
        return self._nome
    
    @nome.setter
    def nome(self, novo_nome):
        if not novo_nome or not isinstance(novo_nome, str):
            raise ValueError("Nome/Título do item é obrigatório")
        self._nome = novo_nome

    @property
    def imagem_url(self):
        return self._imagem_url
    
    @imagem_url.setter
    def imagem_url(self, nova_imagem_url):
        self._imagem_url = nova_imagem_url

    @property
    def imagem_arquivo(self):
        return self._imagem_arquivo
    
    @imagem_arquivo.setter
    def imagem_arquivo(self, nova_imagem_arquivo):
        self._imagem_arquivo = nova_imagem_arquivo

    @property
    def autor(self):
        return self._autor
    
    @autor.setter
    def autor(self, novo_autor):
        if not novo_autor or not isinstance(novo_autor, str):
            raise ValueError("Autor é obrigatório")
        if not re.match(r"^[a-zA-ZÀ-ÿ\s\.\']+$", novo_autor):
            raise ValueError("Nome do autor deve conter apenas letras")
        self._autor = novo_autor

    @property
    def num_paginas(self):
        return self._num_paginas
    
    @num_paginas.setter
    def num_paginas(self, novo_num_paginas):
        if not isinstance(novo_num_paginas, int) or novo_num_paginas <= 0:
            raise ValueError("Número de páginas deve ser um valor inteiro positivo")
        self._num_paginas = novo_num_paginas

    @property
    def isbn(self):
        return self._isbn
    
    @isbn.setter
    def isbn(self, novo_isbn):
        if not novo_isbn or not isinstance(novo_isbn, str):
            raise ValueError("ISBN é obrigatório")
        if not re.match(r"^[0-9-]+$", novo_isbn):
            raise ValueError("ISBN deve conter apenas números e hífens")
        self._isbn = novo_isbn

    @property
    def categoria(self):
        return self._categoria
    
    @categoria.setter
    def categoria(self, nova_categoria):
        if nova_categoria and not re.match(r"^[a-zA-ZÀ-ÿ\s\.\']+$", nova_categoria):
            raise ValueError("Categoria deve conter apenas letras")
        self._categoria = nova_categoria

    @property
    def emprestavel(self):
        return self._emprestavel
    
    @emprestavel.setter
    def emprestavel(self, novo_emprestavel):
        self._emprestavel = novo_emprestavel

    @property
    def data_cadastro(self):
        return self._data_cadastro

    @abstractmethod
    def __str__(self):
        pass
