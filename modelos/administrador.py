from usuario import Usuario

class Administrador(Usuario):
    
    def __init__(self, nome, email, senha, cpf):
        super().__init__(nome, email, senha, cpf)
        
    def __str__(self):
        return (
            f"--- Dados do Administrador ---\n"
            f"ID: {self.id}\n"
            f"Nome: {self.nome}\n"
            f"Email: {self.email}\n"
            f"Senha: {'*' * len(self.senha)}\n"
            f"CPF: {self.cpf}\n"
            f"-------------------------------"
        )