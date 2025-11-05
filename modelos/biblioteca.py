from membro import Membro
from administrador import Administrador
from bibliotecario import Bibliotecario
from emprestimo import Emprestimo
from reserva import Reserva
from config import LIMITE_EMPRESTIMOS_SIMULTANEOS

class Biblioteca:
    def __init__(self):
        self.itens = []
        self.usuarios = []
        self.emprestimos = []
        self.reservas = []
    
    def adicionar_usuario(self, nome, email, senha, cpf, tipo):
        classe_tipo = {
            'membro': Membro,
            'administrador': Administrador,
            'bibliotecario': Bibliotecario
        }[tipo]

        self.usuarios.append(classe_tipo(nome, email, senha, cpf))
        
    def remover_usuario(self, id):
        usuarios = [u for u in self.usuarios if u.id == id]

        if not usuarios:
            raise ValueError(f'Usuário com id {id} não existe')
        
        usuario = usuarios[0]

        self.usuarios.remove(usuario)

    def adicionar_item(self, item):
        self.itens.append(item)

    def remover_item(self, id):
        itens = [i for i in self.itens if i.id == id]

        if not itens:
            raise ValueError(f'Item com id {id} não existe')
        
        item = itens[0]

        self.itens.remove(item)
    
    def emprestar_item(self, item, membro):
        if not isinstance(membro, Membro):
            raise TypeError('Apenas membros podem emprestar itens')
        
        soma_emprestimos_reservas = len(
            [e for e in self.emprestimos if e.status == 'ativo' and e.membro == membro] + [r for r in self.reservas if r.status == 'aguardando' and r.membro == membro]
        )

        if soma_emprestimos_reservas >= LIMITE_EMPRESTIMOS_SIMULTANEOS:
            raise ValueError(f'Não é possível ultrapassar o limite de {LIMITE_EMPRESTIMOS_SIMULTANEOS} empréstimos')

        self.itens.emprestimos.append(Emprestimo(item, membro))
        
    def reservar_item(self, item, membro):
        if not isinstance(membro, Membro):
            raise TypeError('Apenas membros podem reservar itens')
        
        soma_emprestimos_reservas = len(
            [e for e in self.emprestimos if e.status == 'ativo' and e.membro == membro] + [r for r in self.reservas if r.status == 'aguardando' and r.membro == membro]
        )

        if soma_emprestimos_reservas >= LIMITE_EMPRESTIMOS_SIMULTANEOS:
            raise ValueError(f'Não é possível ultrapassar o limite de {LIMITE_EMPRESTIMOS_SIMULTANEOS} empréstimos')
        
        self.itens.reservas.append(Reserva(item, membro))
        