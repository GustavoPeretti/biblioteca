from modelos.membro import Membro
from modelos.administrador import Administrador
from modelos.bibliotecario import Bibliotecario
from modelos.emprestimo import Emprestimo
from modelos.reserva import Reserva
from config import LIMITE_EMPRESTIMOS_SIMULTANEOS, PRAZO_VALIDADE_RESERVA
import datetime

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
        # Filtro de usuários por ID
        usuarios = [u for u in self.usuarios if u.id == id]

        # Se o filtro não resultar em nenhum usuário
        if not usuarios:
            raise ValueError(f'Usuário com id {id} não existe')
        
        # Considerar o único resultado do filtro
        usuario = usuarios[0]

        # Remover instância da lista
        self.usuarios.remove(usuario)

    def adicionar_item(self, item):
        self.itens.append(item)

    def remover_item(self, id):
        # Filtro de itens por ID
        itens = [i for i in self.itens if i.id == id]

        # Se o filtro não resultar em nenhum item
        if not itens:
            raise ValueError(f'Item com id {id} não existe')
        
        # Considerar o único resultado do filtro
        item = itens[0]

        # Remover instância da lista
        self.itens.remove(item)
    
    def emprestar_item(self, item, membro):
        # Se o usuário não for um membro (apenas membros podem emprestar e reservar)
        if not isinstance(membro, Membro):
            raise TypeError('Apenas membros podem emprestar itens')
        
        # Soma da contagem de reservas e de empréstimos (que não deve ultrapassar o limite de registros)
        soma_emprestimos_reservas = len(
            [e for e in self.emprestimos if e.status == 'ativo' and e.membro == membro] # Filtro para encontrar empréstimos ativos do membro
            +
            [r for r in self.reservas if r.status == 'aguardando' and r.membro == membro] # Filtro para encontrar reservas ativas do membro
        )

        # Se ultrapasasar o limite de empréstimos
        if soma_emprestimos_reservas >= LIMITE_EMPRESTIMOS_SIMULTANEOS:
            raise ValueError(f'Não é possível ultrapassar o limite de {LIMITE_EMPRESTIMOS_SIMULTANEOS} empréstimos')

        # Obtenção dos empréstimos ativos do item
        emprestimos_ativos_item = [e for e in self.emprestimos if e.status == 'ativo']

        # Se há um empréstimo ativo do item, ele não pode ser emprestado
        if emprestimos_ativos_item:
            raise ValueError('Não é possível emprestar um livro com empréstimo ativo')
        
        # Obtenção do último empréstimo
        # Pode ser que não tenha nenhum resultado, um, ou múltiplos
        filtro_ultimo_emprestimo = [e for e in self.emprestimos if e.status != 'ativo'] 
        
        # Se nunca teve empréstimos, nunca teve reserva. Isso significa que temos informações
        # suficientes para saber que o livro pode ser emprestado
        if not filtro_ultimo_emprestimo:
            self.emprestimos.append(Emprestimo(item, membro))
            return

        # Ordenação e reversão para garantir que o primeiro elemento da lista seja o empŕestimo mais recente
        filtro_ultimo_emprestimo.sort(key=lambda e: e.data_devolucao).reverse()

        # O empréstimo mais recente é o primeiro elemento da lista
        emprestimo_mais_recente = filtro_ultimo_emprestimo[0]

        # Data que o item ficou disponível
        data_referencia = emprestimo_mais_recente.data_devolucao

        # Filtro para encontrar reservas ativas do item
        reservas_ativas_item = [r for r in self.reservas if r.status == 'aguardando' and r.item == item]
        
        # Atualização do status das reservas expiradas
        for reserva in reservas_ativas_item:
            data_validade_reserva = data_referencia + datetime.timedelta(days=PRAZO_VALIDADE_RESERVA)

            # Se passou da data de validade
            if datetime.datetime.now() > data_validade_reserva:
                reserva.status = 'expirada'

        # Obtenção das reservas "honestas", com prioridade para retirar
        reservas_ativas_item = [r for r in self.reservas if r.status == 'aguardando' and r.item == item]

        # Se não há reservas ativas, não há prioridade para verificar
        if not reservas_ativas_item:
            self.emprestimos.append(Emprestimo(item, membro))
            return

        # Ordenação das reservas ativas por ordem de reserva (as primeiras reservas vêm primeiro)
        reservas_ativas_item.sort(key=lambda r: r.data_reserva)

        # Membro com preferência para retirar
        primeiro_membro_fila = reservas_ativas_item[0].membro    

        # Se o membro tentando retirar não tem prioridade, ele não pode retirar
        if membro != primeiro_membro_fila:
            raise ValueError('Este item possui reservas. Apenas o primeiro membro da fila pode emprestar.')

        # Criar o empréstimo
        self.emprestimos.append(Emprestimo.de_reserva(reservas_ativas_item[0]))
        
    def renovar_emprestimo(self, id_emprestimo):
        # Localiza empréstimo pelo id
        emprestimos = [e for e in self.emprestimos if str(e.id) == str(id_emprestimo) or e.id == id_emprestimo]
        
        # Se o empréstimo não foi encontrado
        if not emprestimos:
            raise ValueError(f'Empréstimo com id {id_emprestimo} não encontrado')
        
        # Considera o único resultado do filtro
        emprestimo = emprestimos[0]
        
        # Delega a lógica de renovação ao próprio objeto Emprestimo
        emprestimo.renovar()
        
        return emprestimo

    def reservar_item(self, item, membro):
        # Itens disponíveis não podem ser reservados
        emprestimos_ativos_item = [e for e in self.emprestimos if e.status == 'ativo' and e.item == item]
        if not emprestimos_ativos_item:
            raise ValueError('Item disponível não pode ser reservado')

        # Verificar se o usuário já não tem reserva ativa desse item
        reservas_ativas_membro_item = [r for r in self.reservas if r.status == 'aguardando' and r.membro == membro and r.item == item]
        
        if reservas_ativas_membro_item:
            raise ValueError('Você já possui uma reserva ativa deste item')

        # Se o usuário não for um membro (apenas membros podem emprestar e reservar)
        if not isinstance(membro, Membro):
            raise TypeError('Apenas membros podem reservar itens')
        
        # Soma da contagem de reservas e de empréstimos (que não deve ultrapassar o limite de registros)
        soma_emprestimos_reservas = len(
            [e for e in self.emprestimos if e.status == 'ativo' and e.membro == membro] + [r for r in self.reservas if r.status == 'aguardando' and r.membro == membro]
        )

        # Se ultrapasasar o limite de empréstimos
        if soma_emprestimos_reservas >= LIMITE_EMPRESTIMOS_SIMULTANEOS:
            raise ValueError(f'Não é possível ultrapassar o limite de {LIMITE_EMPRESTIMOS_SIMULTANEOS} empréstimos')
        
        # Criar a reserva
        self.reservas.append(Reserva(item, membro))

    def registrar_pagamento_multa(self, id_emprestimo):
        # Localiza empréstimo pelo id
        emprestimos = [e for e in self.emprestimos if str(e.id) == str(id_emprestimo) or e.id == id_emprestimo]
        if not emprestimos:
            raise ValueError(f'Empréstimo com id {id_emprestimo} não encontrado')

        emprestimo = emprestimos[0]

        # Delegar a lógica de quitação ao próprio objeto Emprestimo
        emprestimo.quitar_divida()

        return emprestimo

    def registrar_devolucao(self, id_emprestimo):
        # Localiza empréstimo pelo id
        emprestimos = [e for e in self.emprestimos if str(e.id) == str(id_emprestimo) or e.id == id_emprestimo]
        if not emprestimos:
            raise ValueError(f'Empréstimo com id {id_emprestimo} não encontrado')

        emprestimo = emprestimos[0]

        # Processa a devolução (pode gerar multa internamente)
        emprestimo.devolver()

        # Se a devolução finalizou o empréstimo, verificar reservas e liberar para o primeiro da fila
        if emprestimo.status == 'finalizado':
            reservas_ativas_item = [r for r in self.reservas if r.status == 'aguardando' and r.item == emprestimo.item]
            if reservas_ativas_item:
                reservas_ativas_item.sort(key=lambda r: r.data_reserva)
                primeira = reservas_ativas_item[0]
                # Marcar reserva como finalizada (prioridade para retirar)
                primeira.marcar_como_finalizada()

        return emprestimo

