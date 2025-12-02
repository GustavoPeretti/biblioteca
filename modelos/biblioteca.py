from modelos.membro import Membro
from modelos.administrador import Administrador
from modelos.bibliotecario import Bibliotecario
from modelos.emprestimo import Emprestimo
from modelos.reserva import Reserva
from modelos.livro import Livro
from modelos.ebook import Ebook
from modelos import database
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
        database.inicializar_banco()
        self._carregar_dados()
        
    def _carregar_dados(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # 1. Carregar Usuários
        cursor.execute("SELECT * FROM usuarios")
        for row in cursor.fetchall():
            classe_tipo = {
                'membro': Membro,
                'administrador': Administrador,
                'bibliotecario': Bibliotecario
            }.get(row['tipo'], Membro)
            
            usuario = classe_tipo(row['nome'], row['email'], row['senha'], row['cpf'])
            usuario._id = row['id']
            usuario.tipo = row['tipo']
            self.usuarios.append(usuario)
            
        # 2. Carregar Itens
        cursor.execute("SELECT * FROM itens")
        for row in cursor.fetchall():
            if row['tipo'] == 'livro':
                item = Livro(row['nome'], None, None, row['autor'], row['paginas'], row['isbn'], row['categoria'])
            else:
                
                item = Ebook(row['nome'], None, None, row['autor'], row['paginas'], row['isbn'], row['categoria'], None, None)
                
            item._id = row['id']
            item._status = row['status']
            item.tipo = row['tipo']
            self.itens.append(item)
            
        #Carregar Empréstimos
        cursor.execute("SELECT * FROM emprestimos")
        for row in cursor.fetchall():
            # Encontrar objetos reais
            item_obj = next((i for i in self.itens if str(i.id) == row['item_id']), None)
            membro_obj = next((u for u in self.usuarios if str(u.id) == row['membro_id']), None)
            
            if item_obj and membro_obj:
                emp = Emprestimo(item_obj, membro_obj)
                emp._id = row['id']
                emp._data_emprestimo = datetime.datetime.fromisoformat(row['data_emprestimo']) if row['data_emprestimo'] else None
                emp._data_devolucao = datetime.datetime.fromisoformat(row['data_devolucao']) if row['data_devolucao'] else None
                emp._data_quitacao = datetime.datetime.fromisoformat(row['data_quitacao']) if row['data_quitacao'] else None
                emp._quantidade_renovacoes = row['quantidade_renovacoes']
                emp._status = row['status']
                # Restaurar multa
                if row['multa_valor'] is not None:
                    from modelos.multa import Multa
                    emp._multa = Multa(row['multa_valor'], bool(row['multa_paga']))
                
                self.emprestimos.append(emp)

        #Carregar Reservas
        cursor.execute("SELECT * FROM reservas")
        for row in cursor.fetchall():
            item_obj = next((i for i in self.itens if str(i.id) == row['item_id']), None)
            membro_obj = next((u for u in self.usuarios if str(u.id) == row['membro_id']), None)
            
            if item_obj and membro_obj:
                res = Reserva(item_obj, membro_obj)
                res._id = row['id']
                res._data_reserva = datetime.datetime.fromisoformat(row['data_reserva'])
                res._data_cancelamento = datetime.datetime.fromisoformat(row['data_cancelamento']) if row['data_cancelamento'] else None
                res._data_finalizacao = datetime.datetime.fromisoformat(row['data_finalizacao']) if row['data_finalizacao'] else None
                res._status = row['status']
                self.reservas.append(res)
        
        conn.close()
        
        #Se vazio, inicia padrão
        if not self.usuarios:
            self._inicializar_dados_padrao()

    def _inicializar_dados_padrao(self):
        #Usuários padrão
        admin = Administrador("Admin Sistema", "admin@biblioteca.com", "admin123", "000.000.000-00")
        admin.tipo = 'administrador'
        self.adicionar_usuario(admin.nome, admin.email, admin.senha, admin.cpf, admin.tipo)

        bib = Bibliotecario("Maria Silva", "maria@biblioteca.com", "biblio123", "111.111.111-11")
        bib.tipo = 'bibliotecario'
        self.adicionar_usuario(bib.nome, bib.email, bib.senha, bib.cpf, bib.tipo)

        membro = Membro("João Santos", "joao@email.com", "senha123", "222.222.222-22")
        membro.tipo = 'membro'
        self.adicionar_usuario(membro.nome, membro.email, membro.senha, membro.cpf, membro.tipo)

        #Itens de exemplo
        livro1 = Livro('O Senhor dos Anéis', None, None, 'J.R.R. Tolkien', 1200, '978-8533613379', 'Fantasia')
        self.adicionar_item(livro1)
        
        livro2 = Livro('1984', None, None, 'George Orwell', 416, '978-8535914849', 'Ficção Científica')
        self.adicionar_item(livro2)
        
        ebook1 = Ebook('Clean Code', None, None, 'Robert C. Martin', 464, '978-0132350884', 'Tecnologia', None, None)
        self.adicionar_item(ebook1)
    
    def adicionar_usuario(self, nome, email, senha, cpf, tipo):
        # Validar se o email já existe
        email_existente = next((u for u in self.usuarios if u.email == email), None)
        if email_existente:
            raise ValueError("Email já cadastrado no sistema")
        
        classe_tipo = {
            'membro': Membro,
            'administrador': Administrador,
            'bibliotecario': Bibliotecario
        }[tipo]

        usuario = classe_tipo(nome, email, senha, cpf)
        #manter atributo 'tipo' para interface
        usuario.tipo = tipo
        self.usuarios.append(usuario)
        
        conn = database.get_connection()
        conn.execute(
            "INSERT INTO usuarios (id, nome, email, senha, cpf, tipo) VALUES (?, ?, ?, ?, ?, ?)",
            (str(usuario.id), usuario.nome, usuario.email, usuario.senha, usuario.cpf, tipo)
        )
        conn.commit()
        conn.close()
        
        return usuario
        
    def remover_usuario(self, id):
        # Filtro de usuários por ID
        # aceitar tanto UUID objects quanto strings
        usuarios = [u for u in self.usuarios if getattr(u, 'id', None) == id or str(getattr(u, 'id', None)) == str(id)]

        # Se o filtro não resultar em nenhum usuário
        if not usuarios:
            raise ValueError(f'Usuário com id {id} não existe')
        
        # Considerar o único resultado do filtro
        usuario = usuarios[0]

        # Remover instância da lista
        self.usuarios.remove(usuario)
        
        conn = database.get_connection()
        conn.execute("DELETE FROM usuarios WHERE id = ?", (str(usuario.id),))
        conn.commit()
        conn.close()

    def adicionar_item(self, item):
        self.itens.append(item)
        
        if isinstance(item, dict):
             pass
        else:
            conn = database.get_connection()
            tipo = 'ebook' if isinstance(item, Ebook) else 'livro'
            item.tipo = tipo
            item._status = 'disponivel'
            conn.execute(
                '''INSERT INTO itens (id, tipo, nome, autor, isbn, categoria, paginas, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (str(item.id), tipo, item.nome, item.autor, item.isbn, item.categoria, item.num_paginas, 'disponivel')
            )
            conn.commit()
            conn.close()

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
        
        # Persistência
        conn = database.get_connection()
        item_id = item['id'] if isinstance(item, dict) else str(item.id)
        conn.execute("DELETE FROM itens WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
    
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
        filtro_ultimo_emprestimo = [e for e in self.emprestimos if _get_status(e) != 'ativo' and getattr(e, 'item', None) == item]
        
        # Se nunca teve empréstimos, nunca teve reserva. Isso significa que temos informações
        # suficientes para saber que o livro pode ser emprestado
        if not filtro_ultimo_emprestimo:
            novo_emp = Emprestimo(item, membro)
            self.emprestimos.append(novo_emp)
            
            # Persistência
            conn = database.get_connection()
            conn.execute(
                '''INSERT INTO emprestimos (id, item_id, membro_id, data_emprestimo, status, quantidade_renovacoes) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (str(novo_emp.id), str(item.id), str(membro.id), novo_emp.data_emprestimo, 'ativo', 0)
            )
            conn.execute("UPDATE itens SET status = ? WHERE id = ?", ('emprestado', str(item.id)))
            item._status = 'emprestado'
            conn.commit()
            conn.close()
            return

        # Ordenação e reversão para garantir que o primeiro elemento da lista seja o empŕestimo mais recente
        filtro_ultimo_emprestimo.sort(key=lambda e: e.data_devolucao, reverse=True)

        # O empréstimo mais recente é o primeiro elemento da lista
        emprestimo_mais_recente = filtro_ultimo_emprestimo[0]

        # Data que o item ficou disponível
        data_referencia = emprestimo_mais_recente.data_devolucao

        # Checar reservas relacionadas para atualizar expiração (inclui 'aguardando' e 'finalizada')
        reservas_para_validade = [r for r in self.reservas if _get_status(r) in ['aguardando', 'finalizada'] and getattr(r, 'item', None) == item]

        # Atualização do status das reservas expiradas
        for reserva in reservas_para_validade:
            data_validade_reserva = data_referencia + datetime.timedelta(days=PRAZO_VALIDADE_RESERVA)

            # Se passou da data de validade
            if datetime.datetime.now() > data_validade_reserva:
                # suportar objetos Reserva e dicionários
                if isinstance(reserva, dict):
                    reserva['status'] = 'expirada'
                    reserva['data_cancelamento'] = datetime.datetime.now()
                else:
                    reserva._status = 'expirada'
                
                # Persistência da expiração
                res_id = reserva['id'] if isinstance(reserva, dict) else str(reserva.id)
                conn = database.get_connection()
                conn.execute("UPDATE reservas SET status = ?, data_cancelamento = ? WHERE id = ?", ('expirada', datetime.datetime.now(), res_id))
                conn.commit()
                conn.close()

        # Obtenção das reservas que efetivamente bloqueiam empréstimos: apenas 'aguardando'
        reservas_ativas_item = [r for r in self.reservas if _get_status(r) == 'aguardando' and getattr(r, 'item', None) == item]

        # Se não há reservas ativas, não há prioridade para verificar
        if not reservas_ativas_item:
            novo_emp = Emprestimo(item, membro)
            self.emprestimos.append(novo_emp)
            
            # Persistência
            conn = database.get_connection()
            conn.execute(
                '''INSERT INTO emprestimos (id, item_id, membro_id, data_emprestimo, status, quantidade_renovacoes) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (str(novo_emp.id), str(item.id), str(membro.id), novo_emp.data_emprestimo, 'ativo', 0)
            )
            conn.execute("UPDATE itens SET status = ? WHERE id = ?", ('emprestado', str(item.id)))
            item._status = 'emprestado'
            conn.commit()
            conn.close()
            return

        # Ordenação das reservas ativas por ordem de reserva (as primeiras reservas vêm primeiro)
        reservas_ativas_item.sort(key=lambda r: r.data_reserva)

        # Membro com preferência para retirar
        primeiro_membro_fila = reservas_ativas_item[0].membro    

        # Se o membro tentando retirar não tem prioridade, ele não pode retirar
        if membro != primeiro_membro_fila:
            raise ValueError('Este item possui reservas. Apenas o primeiro membro da fila pode emprestar.')

        # Criar o empréstimo
        novo_emp = Emprestimo.de_reserva(reservas_ativas_item[0])
        self.emprestimos.append(novo_emp)
        
        # Persistência
        reserva_utilizada = reservas_ativas_item[0]
        conn = database.get_connection()
        # Atualizar reserva (se já não estiver finalizada)
        if _get_status(reserva_utilizada) != 'finalizada':
             conn.execute("UPDATE reservas SET status = ?, data_finalizacao = ? WHERE id = ?", ('finalizada', datetime.datetime.now(), str(reserva_utilizada.id)))
             # Atualiza objeto em memória também, caso não esteja atualizado
             if isinstance(reserva_utilizada, dict):
                 reserva_utilizada['status'] = 'finalizada'
                 reserva_utilizada['data_finalizacao'] = datetime.datetime.now()
             else:
                 reserva_utilizada.marcar_como_finalizada()

        # Inserir empréstimo
        conn.execute(
            '''INSERT INTO emprestimos (id, item_id, membro_id, data_emprestimo, status, quantidade_renovacoes) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (str(novo_emp.id), str(item.id), str(membro.id), novo_emp.data_emprestimo, 'ativo', 0)
        )
        conn.execute("UPDATE itens SET status = ? WHERE id = ?", ('emprestado', str(item.id)))
        item._status = 'emprestado'
        conn.commit()
        conn.close()
        
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
        
        # Persistência
        conn = database.get_connection()
        conn.execute("UPDATE emprestimos SET quantidade_renovacoes = ? WHERE id = ?", (emprestimo._quantidade_renovacoes, str(emprestimo.id)))
        conn.commit()
        conn.close()
        
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
        nova_reserva = Reserva(item, membro)
        self.reservas.append(nova_reserva)
        
        # Persistência
        conn = database.get_connection()
        conn.execute(
            '''INSERT INTO reservas (id, item_id, membro_id, data_reserva, status) 
               VALUES (?, ?, ?, ?, ?)''',
            (str(nova_reserva.id), str(item.id), str(membro.id), nova_reserva.data_reserva, 'aguardando')
        )
        conn.commit()
        conn.close()

    def cancelar_reserva(self, id_reserva):
        # Localiza reserva pelo id
        reservas = [r for r in self.reservas if str(r.id) == str(id_reserva) or r.id == id_reserva]
        
        if not reservas:
            raise ValueError(f'Reserva com id {id_reserva} não encontrada')
        
        reserva = reservas[0]
        
        # Delega a lógica de cancelamento ao objeto Reserva
        reserva.cancelar()
        
        # Persistência
        conn = database.get_connection()
        conn.execute("UPDATE reservas SET status = ?, data_cancelamento = ? WHERE id = ?", 
                     ('cancelada', reserva.data_cancelamento, str(reserva.id)))
        conn.commit()
        conn.close()

    def registrar_pagamento_multa(self, id_emprestimo):
        # Localiza empréstimo pelo id
        emprestimos = [e for e in self.emprestimos if str(e.id) == str(id_emprestimo) or e.id == id_emprestimo]
        if not emprestimos:
            raise ValueError(f'Empréstimo com id {id_emprestimo} não encontrado')

        emprestimo = emprestimos[0]

        # Delegar a lógica de quitação ao próprio objeto Emprestimo
        emprestimo.quitar_divida()
        
        # Persistência
        conn = database.get_connection()
        conn.execute("UPDATE emprestimos SET status = ?, data_quitacao = ?, multa_paga = ? WHERE id = ?", 
                     ('finalizado', emprestimo.data_quitacao, True, str(emprestimo.id)))
        conn.commit()
        conn.close()

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
                if hasattr(item, '_status'):
                    item._status = 'disponivel'
                else:
                    setattr(item, 'status', 'disponivel')
            except Exception:
                pass
                
        # Persistência
        conn = database.get_connection()
        multa_valor = emprestimo.multa.valor if emprestimo.multa else None
        multa_paga = emprestimo.multa.paga if emprestimo.multa else None
        
        conn.execute(
            "UPDATE emprestimos SET status = ?, data_devolucao = ?, multa_valor = ?, multa_paga = ? WHERE id = ?",
            (emprestimo.status, emprestimo.data_devolucao, multa_valor, multa_paga, str(emprestimo.id))
        )
        
        item_id = item['id'] if isinstance(item, dict) else str(item.id)
        conn.execute("UPDATE itens SET status = ? WHERE id = ?", ('disponivel', item_id))
        
        conn.commit()
        conn.close()


        return emprestimo

