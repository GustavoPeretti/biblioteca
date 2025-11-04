from abc import ABC
from uuid import uuid4

class Usuario(ABC):
    
    def __init__(self, nome, email, senha, cpf):
        
        self._id = uuid4()
        self._nome = nome
        self._email = email
        self._senha = senha
        self._cpf = cpf
        
    @property
    def id(self):
        return self._id

    @property
    def nome(self):
        return self._nome
    
    @property
    def email(self):
        return self._email
    
    @property
    def senha(self):
        return self._senha
    
    @property
    def cpf(self):
        return self._cpf
    
    @email.setter
    def email(self, novo_email):
        self._email = novo_email
        
    @senha.setter
    def senha(self, nova_senha):
        self._senha = nova_senha
        
    @nome.setter
    def nome(self, novo_nome):
        self._nome = novo_nome
    
    @cpf.setter
    def cpf(self, novo_cpf):
        self._cpf = novo_cpf
    
    def __str__(self):
        return (
            f"--- Dados do Usuário ---\n"
            f"ID: {self.id}\n"
            f"Nome: {self.nome}\n"
            f"Email: {self.email}\n"
            f"Senha: {'*' * len(self.senha)}\n"
            f"CPF: {self.cpf}\n"
            f"-------------------------"
        )
        
u1 = Usuario("Ana Silva", "anasilva@gmail.com", "senha123", "123.456.789-00")

print(u1)    