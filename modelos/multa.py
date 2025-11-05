class Multa:
    
    def __init__(self, valor, paga):
        self._valor = valor
        self._paga = paga 
        
    @property
    def valor(self):
        return self._valor
    
    @property
    def paga(self):
        return self._paga
    
    @paga.setter
    def paga(self, status): #True ou False
        self._paga = status
    
    @valor.setter
    def valor(self, novo_valor):
        self._valor = novo_valor
    
    