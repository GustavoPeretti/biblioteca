from .membro import Membro
from .administrador import Administrador
from .bibliotecario import Bibliotecario
from .emprestimo import Emprestimo
from .reserva import Reserva
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import LIMITE_EMPRESTIMOS_SIMULTANEOS, PRAZO_VALIDADE_RESERVA
from database.db_manager import DatabaseManager
from database.repositories import UsuarioRepository, ItemRepository, EmprestimoRepository, ReservaRepository, MultaRepository
from database.adapter import DatabaseAdapter
import datetime


def _get_status(obj):
    return obj.get('status') if isinstance(obj, dict) else getattr(obj, 'status', None)

class Biblioteca:
    def __init__(self):
        # Inicializar banco de dados
        db_path = Path(__file__).parent.parent / 'biblioteca.db'
        self.db = DatabaseManager(str(db_path))
        
        # Inicializar repositories
        self.usuario_repo = UsuarioRepository(self.db)
        self.item_repo = ItemRepository(self.db)
        self.emprestimo_repo = EmprestimoRepository(self.db)
        self.reserva_repo = ReservaRepository(self.db)
        self.multa_repo = MultaRepository(self.db)
        
        # Adapter para conversão
        self.adapter = DatabaseAdapter()
        
        # Properties para compatibilidade com código existente
        # Agora buscam do banco em vez de listas em memória
        
    @property
    def usuarios(self):
        """Retorna lista de usuários do banco de dados."""
        rows = self.usuario_repo.listar_todos()
        return [self.adapter.row_to_usuario(row) for row in rows]
    
    @property
    def itens(self):
        """Retorna lista de itens do banco de dados."""
        rows = self.item_repo.listar_todos()
        return [self.adapter.row_to_item(row) for row in rows]
    
    @property
    def emprestimos(self):
        """Retorna lista de empréstimos do banco de dados."""
        rows = self.emprestimo_repo.listar_todos()
        
        # Mapear itens e usuários para reconstruir objetos
        # Nota: Isso carrega todos os itens e usuários, o que é aceitável para este escopo
        itens_map = {str(i.id): i for i in self.itens}
        usuarios_map = {str(u.id): u for u in self.usuarios}
        
        lista_emprestimos = []
        for row in rows:
            # Tentar buscar por ID (int) ou converter para string se necessário
            item = itens_map.get(str(row['item_id']))
            membro = usuarios_map.get(str(row['membro_id']))
            
            if item and membro:
                lista_emprestimos.append(self.adapter.row_to_emprestimo(row, item, membro))
                
        return lista_emprestimos
    
    @property
    def reservas(self):
        """Retorna lista de reservas do banco de dados."""
        rows = self.reserva_repo.listar_todas()
        
        itens_map = {str(i.id): i for i in self.itens}
        usuarios_map = {str(u.id): u for u in self.usuarios}
        
        lista_reservas = []
        for row in rows:
            item = itens_map.get(str(row['item_id']))
            membro = usuarios_map.get(str(row['membro_id']))
            
            if item and membro:
                lista_reservas.append(self.adapter.row_to_reserva(row, item, membro))
                
        return lista_reservas

    
    def adicionar_usuario(self, nome, email, senha, cpf, tipo):
        # Inserir no banco de dados
        user_id = self.usuario_repo.criar(nome, email, senha, cpf, tipo)
        
        # Buscar do banco e converter para objeto
        row = self.usuario_repo.buscar_por_id(user_id)
        usuario = self.adapter.row_to_usuario(row)
        
        return usuario

        
    def remover_usuario(self, id):
        # Verificar se usuário existe
        usuario = self.usuario_repo.buscar_por_id(id)
        if not usuario:
            raise ValueError(f'Usuário com id {id} não existe')
        
        # Remover do banco
        self.usuario_repo.deletar(id)

    def adicionar_item(self, item):
        # Converter objeto para dicionário e inserir no banco
        data = self.adapter.item_to_dict(item)
        item_id = self.item_repo.criar(**data)
        
        # Buscar do banco e retornar objeto atualizado com ID
        row = self.item_repo.buscar_por_id(item_id)
        return self.adapter.row_to_item(row)

    def remover_item(self, id):
        # Verificar se item existe
        item = self.item_repo.buscar_por_id(id)

        if not item:
            raise ValueError(f'Item com id {id} não existe')
        
        # Remover do banco
        self.item_repo.deletar(id)
    
    def emprestar_item(self, item, membro):
        # Se o usuário não for um membro (apenas membros podem emprestar e reservar)
        if not isinstance(membro, Membro):
            raise TypeError('Apenas membros podem emprestar itens')
        
        # Soma da contagem de reservas e de empréstimos (que não deve ultrapassar o limite de registros)
        soma_emprestimos_reservas = len(
            [e for e in self.emprestimos if _get_status(e) == 'ativo' and getattr(e, 'membro', None) == membro]
            +
            [r for r in self.reservas if _get_status(r) == 'aguardando' and getattr(r, 'membro', None) == membro]
        )

        # Se ultrapasasar o limite de empréstimos
        if soma_emprestimos_reservas >= LIMITE_EMPRESTIMOS_SIMULTANEOS:
            raise ValueError(f'Não é possível ultrapassar o limite de {LIMITE_EMPRESTIMOS_SIMULTANEOS} empréstimos')

        # Obtenção dos empréstimos ativos do item
        emprestimos_ativos_item = [e for e in self.emprestimos if _get_status(e) == 'ativo' and getattr(e, 'item', None) == item]

        # Se há um empréstimo ativo do item, ele não pode ser emprestado
        if emprestimos_ativos_item:
            raise ValueError('Não é possível emprestar um livro com empréstimo ativo')
        
        # Obtenção do último empréstimo
        # Pode ser que não tenha nenhum resultado, um, ou múltiplos
        filtro_ultimo_emprestimo = [e for e in self.emprestimos if _get_status(e) != 'ativo' and getattr(e, 'item', None) == getattr(e, 'item', None)] 
        
        # Se nunca teve empréstimos, nunca teve reserva. Isso significa que temos informações
        # suficientes para saber que o livro pode ser emprestado
        # Se nunca teve empréstimos, nunca teve reserva. Isso significa que temos informações
        # suficientes para saber que o livro pode ser emprestado
        if not filtro_ultimo_emprestimo:
            self.emprestimo_repo.criar(item.id, membro.id)
            return

        # Ordenação e reversão para garantir que o primeiro elemento da lista seja o empŕestimo mais recente
        filtro_ultimo_emprestimo.sort(key=lambda e: e.data_devolucao, reverse=True)

        # O empréstimo mais recente é o primeiro elemento da lista
        emprestimo_mais_recente = filtro_ultimo_emprestimo[0]

        # Data que o item ficou disponível
        data_referencia = emprestimo_mais_recente.data_devolucao

        # Filtro para encontrar reservas ativas do item
        reservas_ativas_item = [r for r in self.reservas if _get_status(r) == 'aguardando' and getattr(r, 'item', None).id == item.id]
        
        # Atualização do status das reservas expiradas
        for reserva in reservas_ativas_item:
            data_validade_reserva = data_referencia + datetime.timedelta(days=PRAZO_VALIDADE_RESERVA)

            # Se passou da data de validade
            if datetime.datetime.now() > data_validade_reserva:
                # Atualizar no banco
                self.reserva_repo.atualizar_status(reserva.id, 'expirada', data_cancelamento=datetime.datetime.now())

        # Recarregar reservas após atualizações
        reservas_ativas_item = [r for r in self.reservas if _get_status(r) == 'aguardando' and getattr(r, 'item', None).id == item.id]

        # Obtenção das reservas "honestas", com prioridade para retirar
        # reservas_ativas_item = [r for r in reservas_ativas_item if _get_status(r) == 'aguardando'] # Já filtrado acima

        # Se não há reservas ativas, não há prioridade para verificar
        if not reservas_ativas_item:
            self.emprestimo_repo.criar(item.id, membro.id)
            return

        # Ordenação das reservas ativas por ordem de reserva (as primeiras reservas vêm primeiro)
        reservas_ativas_item.sort(key=lambda r: r.data_reserva)

        # Membro com preferência para retirar
        primeiro_membro_fila = reservas_ativas_item[0].membro    

        # Se o membro tentando retirar não tem prioridade, ele não pode retirar
        # Comparar IDs para garantir
        if str(membro.id) != str(primeiro_membro_fila.id):
            raise ValueError('Este item possui reservas. Apenas o primeiro membro da fila pode emprestar.')

        # Criar o empréstimo
        reserva = reservas_ativas_item[0]
        self.emprestimo_repo.criar(item.id, membro.id)
        
        # Finalizar a reserva
        self.reserva_repo.atualizar_status(reserva.id, 'finalizada', data_finalizacao=datetime.datetime.now())
        
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
        
        # Persistir renovação
        self.emprestimo_repo.renovar(emprestimo.id)
        
        return emprestimo

    def reservar_item(self, item, membro):
        # Itens disponíveis não podem ser reservados
        emprestimos_ativos_item = [e for e in self.emprestimos if _get_status(e) == 'ativo' and getattr(e, 'item', None) == item]
        if not emprestimos_ativos_item:
            raise ValueError('Item disponível não pode ser reservado')

        # Verificar se o usuário já não tem reserva ativa desse item
        reservas_ativas_membro_item = [r for r in self.reservas if _get_status(r) == 'aguardando' and getattr(r, 'membro', None) == membro and getattr(r, 'item', None) == item]
        
        if reservas_ativas_membro_item:
            raise ValueError('Você já possui uma reserva ativa deste item')

        # Se o usuário não for um membro (apenas membros podem emprestar e reservar)
        if not isinstance(membro, Membro):
            raise TypeError('Apenas membros podem reservar itens')
        
        # Soma da contagem de reservas e de empréstimos (que não deve ultrapassar o limite de registros)
        soma_emprestimos_reservas = len(
            [e for e in self.emprestimos if _get_status(e) == 'ativo' and getattr(e, 'membro', None) == membro] + [r for r in self.reservas if _get_status(r) == 'aguardando' and getattr(r, 'membro', None) == membro]
        )

        # Se ultrapasasar o limite de empréstimos
        if soma_emprestimos_reservas >= LIMITE_EMPRESTIMOS_SIMULTANEOS:
            raise ValueError(f'Não é possível ultrapassar o limite de {LIMITE_EMPRESTIMOS_SIMULTANEOS} empréstimos')
        
        # Criar a reserva
        self.reserva_repo.criar(item.id, membro.id)

    def registrar_pagamento_multa(self, id_emprestimo):
        # Localiza empréstimo pelo id
        emprestimos = [e for e in self.emprestimos if str(e.id) == str(id_emprestimo) or e.id == id_emprestimo]
        if not emprestimos:
            raise ValueError(f'Empréstimo com id {id_emprestimo} não encontrado')

        emprestimo = emprestimos[0]

        # Verificar se a multa existe no banco e marcar como paga diretamente se necessário.
        multa_row = self.multa_repo.buscar_por_emprestimo(emprestimo.id)
        agora = datetime.datetime.now()

        if multa_row:
            # Marcar multa no banco como paga
            self.multa_repo.marcar_como_paga(emprestimo.id)

        # Atualizar status do empréstimo e data de quitação no banco
        self.emprestimo_repo.atualizar_status(emprestimo.id, 'finalizado', data_quitacao=agora)

        # Atualizar o objeto em memória para refletir a quitação
        try:
            emprestimo._status = 'finalizado'
            emprestimo._data_quitacao = agora
            if multa_row:
                # Construir um objeto Multa simples para o empréstimo em memória
                from modelos.multa import Multa
                emprestimo._multa = Multa(multa_row['valor'], True)
        except Exception:
            pass

        return emprestimo

    def registrar_devolucao(self, id_emprestimo):
        # Localiza empréstimo pelo id
        emprestimos = [e for e in self.emprestimos if str(e.id) == str(id_emprestimo) or e.id == id_emprestimo]
        if not emprestimos:
            raise ValueError(f'Empréstimo com id {id_emprestimo} não encontrado')

        emprestimo = emprestimos[0]

        # Processa a devolução (pode gerar multa internamente)
        emprestimo.devolver()
        
        # Persistir mudanças
        self.emprestimo_repo.atualizar_status(emprestimo.id, emprestimo.status, data_devolucao=emprestimo.data_devolucao)
        
        # Se gerou multa, persistir
        if emprestimo.multa:
            self.multa_repo.criar(emprestimo.id, emprestimo.multa.valor)

        # Garantir que o item volte a ficar disponível após a devolução (suporta dicts e objetos)
        # No banco, o status do item não é armazenado explicitamente na tabela itens, mas inferido
        # Porém, se houver campo de status, devemos atualizar.
        # O schema não tem status na tabela itens, mas tem 'emprestavel'.
        # O status 'disponivel'/'emprestado' é derivado dos empréstimos ativos.
        # Então não precisamos atualizar a tabela itens.

        # Se a devolução finalizou o empréstimo, verificar reservas e liberar para o primeiro da fila
        if emprestimo.status == 'finalizado':
            # Buscar reservas do item
            reservas_ativas_item = [r for r in self.reservas if r.status == 'aguardando' and getattr(r, 'item', None).id == emprestimo.item.id]
            if reservas_ativas_item:
                reservas_ativas_item.sort(key=lambda r: r.data_reserva)
                primeira = reservas_ativas_item[0]
                # Marcar reserva como finalizada (prioridade para retirar)
                # Na verdade, a reserva continua 'aguardando' até o usuário vir buscar e transformar em empréstimo
                # Ou podemos ter um status 'disponivel_para_retirada'.
                # O código original chamava 'marcar_como_finalizada' que definia status='finalizada'.
                # Mas isso parece errado se o usuário ainda não retirou.
                # Vou manter o comportamento original de não alterar o status da reserva aqui, 
                # pois a lógica de 'emprestar_item' verifica as reservas 'aguardando'.
                pass

        return emprestimo

