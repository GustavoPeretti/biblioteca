from abc import ABC, abstractmethod
from uuid import uuid4
import datetime

class Item(ABC):
    def __init__(self, nome, imagem_url, imagem_arquivo, autor, num_paginas, isbn, categoria):
        self._id = uuid4()
        self._nome = nome
        self._imagem_url = imagem_url
        self._imagem_arquivo = imagem_arquivo
        self._autor = autor
        self._num_paginas = num_paginas
        self._isbn = isbn
        self._categoria = categoria
        self._emprestavel = True
        self._data_cadastro = datetime.datetime.now()

    @property
    def id(self):
        return self._id
    
    @property
    def nome(self):
        return self._nome
    
    @nome.setter
    def nome(self, novo_nome):
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
        self._autor = novo_autor

    @property
    def num_paginas(self):
        return self._num_paginas
    
    @num_paginas.setter
    def num_paginas(self, novo_num_paginas):
        self._num_paginas = novo_num_paginas

    @property
    def isbn(self):
        return self._isbn
    
    @isbn.setter
    def isbn(self, novo_isbn):
        self._isbn = novo_isbn

    @property
    def categoria(self):
        return self._categoria
    
    @categoria.setter
    def categoria(self, nova_categoria):
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

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return str(self.id) == str(other.id)
