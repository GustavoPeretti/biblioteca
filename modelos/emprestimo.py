from uuid import uuid4
import datetime
from multa import Multa
from config import PRAZO_DEVOLUCAO, MULTA_POR_DIA, LIMITE_RENOVACOES

class Emprestimo:
    def __init__(self, item, membro):
        self._id = uuid4()
        self._data_emprestimo = datetime.datetime.now()
        self._data_devolucao = None
        self._data_quitacao = None
        self._quantidade_renovacoes = 0
        self._status = 'ativo' # 'ativo', 'multado', 'finalizado'
        self._item = item
        self._membro = membro
        self._multa = None

    @property
    def id(self):
        return self._id

    @property
    def data_emprestimo(self):
        return self._data_emprestimo
    
    @property
    def data_devolucao(self):
        return self._data_devolucao
    
    @property
    def data_quitacao(self):
        return self._data_devolucao
    
    @property
    def status(self):
        return self._status

    @property
    def item(self):
        return self._item
    
    @property
    def membro(self):
        return self._membro
    
    @property
    def multa(self):
        return self._multa

    @property
    def data_prevista_devolucao(self):
        '''Data limite para devolução do item ou renovação do empréstimo'''

        # data do empréstimo + acréscimos das renovações (incluindo a que será realizada, o que justifica o '+ 1')
        return self._data_emprestimo + datetime.timedelta(days=(self._quantidade_renovacoes + 1) * PRAZO_DEVOLUCAO)

    @classmethod
    def de_reserva(cls, reserva):
        '''Cria uma empréstimo a partir de uma reserva'''
        return cls(reserva.item, reserva.membro)
    
    def devolver(self):
        '''Atualiza o status do empréstimo quando um bibliotecário recebe uma devolução'''

        # Se o empréstimo não estiver ativo
        if self._status != 'ativo':
            raise ValueError('Empréstimo já finalizado')

        # Quanto tempo passou desde a data de devolução
        tempo_diferenca = datetime.datetime.now() - self.data_prevista_devolucao

        # Se o tempo de diferença é negativo (está atrasado)
        if tempo_diferenca < datetime.timedelta(0):
            self._status = 'multado'
            self._multa = Multa(MULTA_POR_DIA * abs(tempo_diferenca.days), False)
            return
        
        self._status = 'finalizado'

    def quitar_divida(self):
        # Se não há registro de multas
        if self._status != 'multado':
            raise ValueError('Não há multas para quitar')
        
        # Atualização do estado da multa
        self._multa.paga = True
        self._status = 'finalizado'

        # Registro da data de quitação
        self._data_quitacao = datetime.datetime.now()

    def renovar(self):
        '''Incrementa o número de renovações quando um membro ou um bibliotecário renova um empréstimo no sistema'''

        # Se o empréstimo não estiver ativo
        if self._status != 'ativo':
            raise ValueError('Não é possível renovar um empréstimo finalizado')

        # Se o limite de renovações já foi atingido
        if self._quantidade_renovacoes >= LIMITE_RENOVACOES:
            raise ValueError(f'Não é possível um empréstimo mais de {LIMITE_RENOVACOES}')

        # Data mínima para a permissão da renovação: dois dias antes da data prevista
        data_minima = self.data_prevista_devolucao - datetime.timedelta(days=2)

        data_atual = datetime.datetime.now()

        # Se ainda não chegou a data mínima
        if data_atual < data_minima:
            raise ValueError(f'É preciso esperar até {data_minima.strftime("%d/%m/%Y, %H:%M:%S")} para renovar')

        # Se já passou da data prevista, há atrasos 
        if data_atual > self.data_prevista_devolucao:
            raise ValueError(f'Um item atrasado não pode ser renovado, e sim devolvido')

        # Incrementa a quantidade de renovações
        self._quantidade_renovacoes += 1
