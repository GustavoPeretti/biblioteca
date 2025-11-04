from abc import ABC, abstractmethod
from uuid import uuid4
import datetime

class Item(ABC):
    def __init__(self, nome, imagem_url, imagem_arquivo, autor, num_paginas, isbn, categoria):
        self.id = uuid4()
        self.nome = nome
        self.imagem_url = imagem_url
        self.imagem_arquivo = imagem_arquivo
        self.autor = autor
        self.num_paginas = num_paginas
        self.isbn = isbn
        self.categoria = categoria
        self.emprestavel = True
        self.data_cadastro = datetime.datetime.now()

    @abstractmethod
    def mostrar_detalhes(self):
        pass
    