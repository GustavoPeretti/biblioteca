from abc import ABC
from uuid import uuid4
import re

class Usuario(ABC):
    def __init__(self, nome, email, senha, cpf):
        self._id = uuid4()
        # Usar os setters para aplicar validações
        self.nome = nome
        self.email = email
        self.senha = senha
        self.cpf = cpf
        
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
        if not novo_email or not isinstance(novo_email, str):
            raise ValueError("Email é obrigatório")
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", novo_email):
            raise ValueError("Email inválido")
        self._email = novo_email
        
    @senha.setter
    def senha(self, nova_senha):
        if not nova_senha or not isinstance(nova_senha, str):
            raise ValueError("Senha é obrigatória")
        if len(nova_senha) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")
        self._senha = nova_senha
        
    @nome.setter
    def nome(self, novo_nome):
        if not novo_nome or not isinstance(novo_nome, str):
            raise ValueError("Nome é obrigatório")
        if not re.match(r"^[a-zA-ZÀ-ÿ\s\.\']+$", novo_nome):
            raise ValueError("Nome deve conter apenas letras")
        self._nome = novo_nome
    
    @cpf.setter
    def cpf(self, novo_cpf):
        if not novo_cpf or not isinstance(novo_cpf, str):
            raise ValueError("CPF é obrigatório")
        cpf_limpo = re.sub(r"\D", "", novo_cpf)
        if len(cpf_limpo) != 11:
            raise ValueError("CPF deve conter 11 dígitos")
        self._cpf = cpf_limpo
    
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
    