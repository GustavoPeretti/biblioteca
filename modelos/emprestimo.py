from uuid import uuid4
import datetime
from multa import Multa
from config import PRAZO_DEVOLUCAO, MULTA_POR_DIA

class Emprestimo:
    def __init__(self, item, membro):
        self._id = uuid4()
        self._data_emprestimo = datetime.datetime.now()
        self._data_devolucao = None
        self._data_quitacao = None
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

    @classmethod
    def de_reserva(cls, reserva):
        return cls(reserva.item, reserva.membro)
    
    def devolver(self):
        if self._status != 'ativo':
            raise ValueError('Empréstimo já finalizado')

        tempo_diferenca = (datetime.datetime.now() - self._data_emprestimo) # Quantos dias passaram desde o empréstimo

        if tempo_diferenca > datetime.timedelta(days=PRAZO_DEVOLUCAO):
            self._status = 'multado'
            self._multa = Multa(MULTA_POR_DIA * tempo_diferenca.days, False)
            return
        
        self._status = 'finalizado'

    def quitar_divida(self):
        if self._status != 'multado':
            raise ValueError('Não há multas para quitar')
        
        self._multa.paga = True
        self._status = 'finalizado'

        self.data_quitacao = datetime.datetime.now()
