from modelos.item import Item

class Ebook(Item):
    def __init__(self, nome, imagem_url, imagem_arquivo, autor, num_paginas, isbn, categoria, arquivo, url):
        super().__init__(nome, imagem_url, imagem_arquivo, autor, num_paginas, isbn, categoria)
        
        self._arquivo = arquivo
        self._url = url

    @property
    def arquivo(self):
        return self._arquivo
    
    @arquivo.setter
    def arquivo(self, novo_arquivo):
        self._arquivo = novo_arquivo

    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, novo_url):
        self._url = novo_url

    def __str__(self):
        return (
            f"--- Dados do Livro ---\n"
            f"ID: {self._id}\n"
            f"Nome: {self._nome}\n"
            f"Autor: {self._autor}\n"
            f"Número de Páginas: {self._num_paginas}\n"
            f"ISBN: {self._isbn}\n"
            f"Categoria: {self._categoria}\n"
            f"Emprestável: {'Sim' if self._emprestavel else 'Não'}\n"
            f"Data de Cadastro: {self._data_cadastro.strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"URL: {self._url}\n"
            f"-------------------------"
        )
    