from modelos.membro import Membro
from modelos.administrador import Administrador
from modelos.bibliotecario import Bibliotecario
from modelos.emprestimo import Emprestimo
from modelos.reserva import Reserva
from config import LIMITE_EMPRESTIMOS_SIMULTANEOS, PRAZO_VALIDADE_RESERVA
import datetime

def _get_status(obj):
    return obj.get('status') if isinstance(obj, dict) else getattr(obj, 'status', None)

class Biblioteca:
    def __init__(self):
        self.itens = []
        self.usuarios = []
        self.emprestimos = []
        self.reservas = []
        self._inicializar_dados()
        
    def _inicializar_dados(self):
        # Usuários padrão (usar classes específicas e manter atributo 'tipo' para compatibilidade)
        admin = Administrador("Admin Sistema", "admin@biblioteca.com", "admin123", "000.000.000-00")
        admin.tipo = 'administrador'
        self.usuarios.append(admin)

        bib = Bibliotecario("Maria Silva", "maria@biblioteca.com", "biblio123", "111.111.111-11")
        bib.tipo = 'bibliotecario'
        self.usuarios.append(bib)

        membro = Membro("João Santos", "joao@email.com", "senha123", "222.222.222-22")
        membro.tipo = 'membro'
        self.usuarios.append(membro)

        # Itens de exemplo
        self.itens.append({
            'id': 1,
            'nome': 'O Senhor dos Anéis',
            'autor': 'J.R.R. Tolkien',
            'isbn': '978-8533613379',
            'categoria': 'Fantasia',
            'paginas': 1200,
            'tipo': 'livro',
            'status': 'disponivel'
        })
        self.itens.append({
            'id': 2,
            'nome': '1984',
            'autor': 'George Orwell',
            'isbn': '978-8535914849',
            'categoria': 'Ficção Científica',
            'paginas': 416,
            'tipo': 'livro',
            'status': 'disponivel'
        })
        self.itens.append({
            'id': 3,
            'nome': 'Clean Code',
            'autor': 'Robert C. Martin',
            'isbn': '978-0132350884',
            'categoria': 'Tecnologia',
            'paginas': 464,
            'tipo': 'ebook',
            'status': 'disponivel'
        })
    
    def adicionar_usuario(self, nome, email, senha, cpf, tipo):
        classe_tipo = {
            'membro': Membro,
            'administrador': Administrador,
            'bibliotecario': Bibliotecario
        }[tipo]

        usuario = classe_tipo(nome, email, senha, cpf)
        # manter atributo 'tipo' para compatibilidade com a interface
        usuario.tipo = tipo
        self.usuarios.append(usuario)
        return usuario
        
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
        
        # Verificar se o membro possui multas pendentes
        multas_pendentes = [e for e in self.emprestimos if _get_status(e) == 'multado' and getattr(e, 'membro', None) == membro and getattr(getattr(e, 'multa', None), 'paga', True) == False]
        if multas_pendentes:
            valor_total = sum(getattr(e.multa, 'valor', 0) for e in multas_pendentes)
            raise ValueError(f'Membro possui multas pendentes no valor de R$ {valor_total:.2f}. Não é possível fazer novos empréstimos até que as multas sejam quitadas.')
        
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
        if not filtro_ultimo_emprestimo:
            self.emprestimos.append(Emprestimo(item, membro))
            return

        # Ordenação e reversão para garantir que o primeiro elemento da lista seja o empŕestimo mais recente
        filtro_ultimo_emprestimo.sort(key=lambda e: e.data_devolucao, reverse=True)

        # O empréstimo mais recente é o primeiro elemento da lista
        emprestimo_mais_recente = filtro_ultimo_emprestimo[0]

        # Data que o item ficou disponível
        data_referencia = emprestimo_mais_recente.data_devolucao

        # Filtro para encontrar reservas ativas do item
        reservas_ativas_item = [r for r in self.reservas if _get_status(r) == 'aguardando' and getattr(r, 'item', None) == item]
        
        # Atualização do status das reservas expiradas
        for reserva in reservas_ativas_item:
            data_validade_reserva = data_referencia + datetime.timedelta(days=PRAZO_VALIDADE_RESERVA)

            # Se passou da data de validade
            if datetime.datetime.now() > data_validade_reserva:
                # suportar objetos Reserva e dicionários
                if isinstance(reserva, dict):
                    reserva['status'] = 'expirada'
                    reserva['data_cancelamento'] = datetime.datetime.now()
                else:
                    reserva._status = 'expirada'

        # Obtenção das reservas "honestas", com prioridade para retirar
        reservas_ativas_item = [r for r in reservas_ativas_item if _get_status(r) == 'aguardando']

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
        
        # Verificar se o membro possui multas pendentes
        multas_pendentes = [e for e in self.emprestimos if _get_status(e) == 'multado' and getattr(e, 'membro', None) == membro and getattr(getattr(e, 'multa', None), 'paga', True) == False]
        if multas_pendentes:
            valor_total = sum(getattr(e.multa, 'valor', 0) for e in multas_pendentes)
            raise ValueError(f'Membro possui multas pendentes no valor de R$ {valor_total:.2f}. Não é possível fazer novas reservas até que as multas sejam quitadas.')
        
        # Soma da contagem de reservas e de empréstimos (que não deve ultrapassar o limite de registros)
        soma_emprestimos_reservas = len(
            [e for e in self.emprestimos if _get_status(e) == 'ativo' and getattr(e, 'membro', None) == membro] + [r for r in self.reservas if _get_status(r) == 'aguardando' and getattr(r, 'membro', None) == membro]
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

        # Garantir que o item volte a ficar disponível após a devolução (suporta dicts e objetos)
        item = getattr(emprestimo, 'item', None)
        if isinstance(item, dict):
            item['status'] = 'disponivel'
        else:
            # tentar atribuir atributo 'status' se existir ou ignorar
            try:
                setattr(item, 'status', 'disponivel')
            except Exception:
                pass


        return emprestimo

