from item import Item

class Livro(Item):
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
            f"-------------------------"
        )
    