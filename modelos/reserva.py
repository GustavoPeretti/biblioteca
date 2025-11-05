from uuid import uuid4
import datetime

class Reserva:
    def __init__(self, item, membro):
        self._id = uuid4()
        self._data_reserva = datetime.datetime.now()
        self._data_cancelamento = None
        self._data_finalizacao = None
        self._status = 'aguardando' # 'aguardando', 'cancelada' ou 'finalizada'
        self._item = item
        self._membro = membro

    @property
    def id(self):
        return self._id
    
    @property
    def data_reserva(self):
        return self._data_reserva

    @property
    def data_cancelamento(self):
        return self._data_cancelamento
    
    @property
    def data_finalizacao(self):
        return self._data_finalizacao
    
    @property
    def status(self):
        return self._status
    
    @property
    def item(self):
        return self._item
    
    @property
    def membro(self):
        return self._membro

    def cancelar(self,):
        self._data_cancelamento = datetime.datetime.now()
        self._status = 'cancelada'

    def marcar_como_finalizada(self):
        self._data_cancelamento = datetime.datetime.now()
        self._status = 'finalizada'
    