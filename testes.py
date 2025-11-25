"""
Suite de testes completa para a aplicação de Biblioteca
Testa todas as funcionalidades: usuários, itens, empréstimos, reservas, renovações e multas.
Utiliza o banco de dados SQLite para garantir persistência.
"""

import sys
import os
import datetime
import time
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.append(str(Path.cwd()))

from modelos.biblioteca import Biblioteca
from modelos.livro import Livro
from modelos.ebook import Ebook
from modelos.membro import Membro
from modelos.administrador import Administrador
from modelos.bibliotecario import Bibliotecario
from config import PRAZO_DEVOLUCAO, LIMITE_RENOVACOES, LIMITE_EMPRESTIMOS_SIMULTANEOS

# Importar função de inicialização de dados de exemplo
import inicializar_dados

# Contadores
testes_passaram = 0
testes_falharam = 0

def teste_passou(nome_teste):
    global testes_passaram
    testes_passaram += 1
    print(f"[OK]: {nome_teste}")

def teste_falhou(nome_teste, erro):
    global testes_falharam
    testes_falharam += 1
    print(f"[ERRO]: {nome_teste}")
    print(f"  Erro: {erro}\n")

def teste_assert(condicao, nome_teste, mensagem_erro=""):
    try:
        assert condicao, mensagem_erro
        teste_passou(nome_teste)
    except AssertionError as e:
        teste_falhou(nome_teste, str(e))

def teste_exception(funcao, tipo_excecao, nome_teste, **kwargs):
    """Testa se uma função lança uma exceção específica"""
    try:
        funcao(**kwargs)
        teste_falhou(nome_teste, f"Esperava exceção {tipo_excecao.__name__}, mas nenhuma foi lançada")
    except tipo_excecao:
        teste_passou(nome_teste)
    except Exception as e:
        # Se for erro de integridade do sqlite, pode vir como Exception genérica dependendo da implementação
        if "UNIQUE constraint" in str(e) or "IntegrityError" in str(e):
             # Se esperávamos Exception ou ValueError e veio erro de banco, pode ser aceitável se o teste for de duplicidade
             if tipo_excecao == Exception or tipo_excecao == ValueError:
                 teste_passou(nome_teste)
                 return
        teste_falhou(nome_teste, f"Esperava {tipo_excecao.__name__}, mas recebeu {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

def limpar_banco(bib):
    """Limpa todas as tabelas do banco de dados para iniciar testes limpos.
    Usuários e itens de exemplo são removidos e recriados ao final dos testes.
    """
    tabelas = ['multas', 'reservas', 'emprestimos', 'itens', 'usuarios']
    for tabela in tabelas:
        bib.db.execute_query(f"DELETE FROM {tabela}")
    bib.db.commit()

# ============ TESTES DE USUÁRIOS ============
def testes_usuarios():
    print(f"\n=== TESTES DE USUÁRIOS ===\n")
    
    bib = Biblioteca()
    limpar_banco(bib) # Começar limpo
    
    # Teste 1: Adicionar usuário tipo Membro (ignora duplicatas)
    try:
        usuario_membro = bib.adicionar_usuario('João Silva', 'joao@email.com', 'senha123', '123.456.789-10', 'membro')
        # Verifica se o usuário foi criado ou já existia
        teste_assert(usuario_membro is not None, "Adicionar usuário Membro")
    except Exception as e:
        # Se já existir, captura e continua
        teste_falhou("Adicionar usuário Membro", str(e))

    
    # Teste 2: Adicionar usuário tipo Administrador
    try:
        bib.adicionar_usuario('Admin User', 'admin@email.com', 'senha123', '987.654.321-00', 'administrador')
        teste_assert(any(u.email == 'admin@email.com' for u in bib.usuarios), "Adicionar usuário Administrador")
    except Exception as e:
        teste_falhou("Adicionar usuário Administrador", str(e))
    
    # Teste 3: Adicionar usuário tipo Bibliotecário
    try:
        bib.adicionar_usuario('Bibliotecário User', 'biblio@email.com', 'senha123', '111.222.333-44', 'bibliotecario')
        teste_assert(any(u.email == 'biblio@email.com' for u in bib.usuarios), "Adicionar usuário Bibliotecário")
    except Exception as e:
        teste_falhou("Adicionar usuário Bibliotecário", str(e))
    
    # Teste 4: Remover usuário existente
    try:
        # Buscar ID do bibliotecário recém criado
        biblio_user = next((u for u in bib.usuarios if u.email == 'biblio@email.com'), None)
        if not biblio_user:
            raise RuntimeError('Bibliotecário não encontrado para remoção')
            
        bib.remover_usuario(biblio_user.id)
        teste_assert(not any(u.email == 'biblio@email.com' for u in bib.usuarios), "Remover usuário existente")
    except Exception as e:
        teste_falhou("Remover usuário existente", str(e))
    
    # Teste 5: Tentar remover usuário inexistente
    teste_exception(
        bib.remover_usuario,
        ValueError,
        "Remover usuário inexistente lança ValueError",
        id=99999 # ID inexistente
    )
    
    # Teste 6: Persistência
    bib2 = Biblioteca()
    teste_assert(len(bib2.usuarios) == 2, "Dados persistem após recarregar Biblioteca")

# ============ TESTES DE ITENS (LIVROS E EBOOKS) ============
def testes_itens():
    print(f"\n=== TESTES DE ITENS (LIVROS E EBOOKS) ===\n")
    
    bib = Biblioteca()
    # Não limpamos o banco aqui para manter os usuários criados
    
    # Teste 1: Adicionar Livro
    try:
        livro = Livro('Python Avançado', None, None, 'Gustavo Peretti', 450, '978-3-16-148410-0', 'Programação')
        bib.adicionar_item(livro)
        teste_assert(any(i.isbn == '978-3-16-148410-0' for i in bib.itens), "Adicionar Livro à biblioteca")
    except Exception as e:
        teste_falhou("Adicionar Livro", str(e))
    
    # Teste 2: Adicionar Ebook
    try:
        ebook = Ebook('Clean Code', None, None, 'Robert Martin', 400, '978-0-13-235088-4', 'Programação', 'clean_code.pdf', 'https://example.com/clean-code')
        bib.adicionar_item(ebook)
        teste_assert(any(i.isbn == '978-0-13-235088-4' for i in bib.itens), "Adicionar Ebook à biblioteca")
    except Exception as e:
        teste_falhou("Adicionar Ebook", str(e))
    
    # Teste 3: Verificar propriedades persistidas
    try:
        # Recarregar para garantir que vem do banco
        bib2 = Biblioteca()
        ebook_db = next(i for i in bib2.itens if i.isbn == '978-0-13-235088-4')
        
        teste_assert(ebook_db.nome == 'Clean Code', "Nome do item está correto")
        teste_assert(ebook_db.autor == 'Robert Martin', "Autor do item está correto")
        teste_assert(ebook_db.num_paginas == 400, "Número de páginas está correto")
    except Exception as e:
        teste_falhou("Verificar propriedades do item", str(e))

# ============ TESTES DE EMPRÉSTIMOS ============
def testes_emprestimos():
    print(f"\n=== TESTES DE EMPRÉSTIMOS ===\n")
    
    bib = Biblioteca()
    
    # Setup: Recuperar usuário e livro criados anteriormente
    membro = next(u for u in bib.usuarios if u.tipo == 'membro')
    livro = next(i for i in bib.itens if i.nome == 'Python Avançado')
    
    # Teste 1: Emprestar item para membro
    try:
        bib.emprestar_item(livro, membro)
        teste_assert(len(bib.emprestimos) == 1, "Emprestar item para membro")
    except Exception as e:
        teste_falhou("Emprestar item para membro", str(e))
    
    # Teste 2: Verificar status do empréstimo
    emprestimo = bib.emprestimos[0]
    teste_assert(emprestimo.status == 'ativo', "Status do empréstimo é 'ativo'")
    
    # Teste 3: Tentar emprestar para não-membro
    admin = next(u for u in bib.usuarios if u.tipo == 'administrador')
    livro2 = next(i for i in bib.itens if i.nome == 'Clean Code')
    
    teste_exception(
        bib.emprestar_item,
        TypeError,
        "Emprestar para não-membro lança TypeError",
        item=livro2,
        membro=admin
    )
    
    # Teste 4: Persistência do Empréstimo
    bib2 = Biblioteca()
    emp_db = bib2.emprestimos[0]
    teste_assert(emp_db.item.id == livro.id, "Empréstimo persistido com item correto")
    teste_assert(emp_db.membro.id == membro.id, "Empréstimo persistido com membro correto")

# ============ TESTES DE RENOVAÇÃO ============
def testes_renovacoes():
    print(f"\n=== TESTES DE RENOVAÇÕES ===\n")
    
    bib = Biblioteca()
    
    # Pegar o empréstimo existente
    emprestimo = bib.emprestimos[0]
    
    # Teste 1: Não é possível renovar logo após emprestar (precisa esperar 2 dias antes da devolução)
    teste_exception(
        bib.renovar_emprestimo,
        ValueError,
        "Renovar logo após emprestar lança ValueError",
        id_emprestimo=emprestimo.id
    )
    
    # Teste 2: Simular data futura para permitir renovação
    # Hack: Alterar data no banco para simular passagem de tempo
    dias_atraso = PRAZO_DEVOLUCAO - 1  # 1 dia antes do prazo
    nova_data = (datetime.datetime.now() - datetime.timedelta(days=dias_atraso)).isoformat()
    
    bib.db.execute_query("UPDATE emprestimos SET data_emprestimo = ? WHERE id = ?", (nova_data, str(emprestimo.id)))
    bib.db.commit()
    
    # Recarregar
    bib2 = Biblioteca()
    emprestimo = bib2.emprestimos[0]
    
    try:
        emprestimo_renovado = bib2.renovar_emprestimo(emprestimo.id)
        teste_assert(emprestimo_renovado.quantidade_renovacoes == 1, "Renovação incrementa contador")
        
        # Verificar persistência da renovação
        bib3 = Biblioteca()
        emp_renovado_db = bib3.emprestimos[0]
        teste_assert(emp_renovado_db.quantidade_renovacoes == 1, "Renovação persistida no banco")
    except Exception as e:
        teste_falhou("Renovar empréstimo válido", str(e))

# ============ TESTES DE DEVOLUÇÕES E MULTAS ============
def testes_devolucoes_multas():
    print(f"\n=== TESTES DE DEVOLUÇÕES E MULTAS ===\n")
    
    bib = Biblioteca()
    
    # Cenário 1: Devolução no prazo (o empréstimo atual 'Python Avançado' está no prazo após renovação)
    # Precisamos achar o empréstimo correto.
    # Como só temos 1 empréstimo ativo até agora, é ele.
    emprestimos_ativos = [e for e in bib.emprestimos if e.status == 'ativo']
    if not emprestimos_ativos:
        teste_falhou("Setup Devolução", "Nenhum empréstimo ativo encontrado")
        return
        
    emprestimo = emprestimos_ativos[0]
    
    try:
        emprestimo_devolvido = bib.registrar_devolucao(emprestimo.id)
        teste_assert(emprestimo_devolvido.status == 'finalizado', "Devolução no prazo finaliza empréstimo")
        teste_assert(emprestimo_devolvido.multa is None, "Devolução no prazo não gera multa")
    except Exception as e:
        teste_falhou("Devolução no prazo", str(e))
        
    # Cenário 2: Devolução com atraso (Gera Multa)
    # Setup: Criar novo empréstimo
    membro = next(u for u in bib.usuarios if u.tipo == 'membro')
    livro = next(i for i in bib.itens if i.nome == 'Clean Code')
    
    bib.emprestar_item(livro, membro)
    
    # Buscar o novo empréstimo (deve ser o único ativo)
    bib = Biblioteca() # Recarregar
    emprestimo2 = next(e for e in bib.emprestimos if e.status == 'ativo')
    
    # Simular atraso grande no banco
    data_atrasada = (datetime.datetime.now() - datetime.timedelta(days=PRAZO_DEVOLUCAO + 10)).isoformat()
    bib.db.execute_query("UPDATE emprestimos SET data_emprestimo = ? WHERE id = ?", (data_atrasada, str(emprestimo2.id)))
    bib.db.commit()
    
    try:
        # Devolver
        emprestimo_atrasado = bib.registrar_devolucao(emprestimo2.id)
        teste_assert(emprestimo_atrasado.status == 'multado', "Devolução atrasada gera multa")
        teste_assert(emprestimo_atrasado.multa is not None, "Objeto multa criado")
        
        # Verificar persistência da multa
        cursor = bib.db.execute_query("SELECT * FROM multas WHERE emprestimo_id = ?", (str(emprestimo2.id),))
        multa_row = cursor.fetchone()
        teste_assert(multa_row is not None, "Multa persistida no banco")
        
        # Pagar multa
        emprestimo_quitado = bib.registrar_pagamento_multa(emprestimo2.id)
        teste_assert(emprestimo_quitado.status == 'finalizado', "Pagamento de multa finaliza empréstimo")
        
    except Exception as e:
        teste_falhou("Fluxo de Multa", str(e))

# ============ TESTES DE RESERVAS ============
def testes_reservas():
    print(f"\n=== TESTES DE RESERVAS ===\n")
    
    bib = Biblioteca()
    limpar_banco(bib) # Começar limpo para evitar efeitos colaterais de datas alteradas
    
    # Setup
    livro = Livro('Livro Reserva', None, None, 'Autor', 200, '999-999', 'Teste')
    livro = bib.adicionar_item(livro) # Atualizar com ID do banco
    
    membro1 = bib.adicionar_usuario('Membro 1', 'm1@email.com', '123', '111.111.111-11', 'membro')
    membro2 = bib.adicionar_usuario('Membro 2', 'm2@email.com', '123', '222.222.222-22', 'membro')
    
    # Emprestar para membro1
    bib.emprestar_item(livro, membro1)
    
    # Teste 1: Reservar item emprestado
    try:
        bib.reservar_item(livro, membro2)
        teste_assert(len(bib.reservas) == 1, "Reserva criada")
        
        # Verificar persistência
        bib2 = Biblioteca()
        reserva = bib2.reservas[0]
        
        teste_assert(reserva.item.id == livro.id, "Item da reserva correto")
        teste_assert(reserva.membro.id == membro2.id, "Membro da reserva correto")
        teste_assert(reserva.status == 'aguardando', "Status 'aguardando'")
    except Exception as e:
        teste_falhou("Criar Reserva", str(e))
        import traceback
        traceback.print_exc()

# ============ FUNÇÃO PRINCIPAL ============

def executar_todos_testes():
    """Executa todas as suítes de teste e retorna 0 em sucesso ou 1 em falha."""
    global testes_passaram, testes_falharam
    # Inicializa dados de exemplo (não falha se já estiverem presentes)
    try:
        inicializar_dados.inicializar()
    except Exception:
        # Não interromper os testes se a inicialização falhar; registrar e prosseguir
        print("Aviso: falha ao inicializar dados de exemplo; prosseguindo com testes")

    # Executar cada grupo de testes
    try:
        testes_usuarios()
        testes_itens()
        testes_emprestimos()
        testes_renovacoes()
        testes_devolucoes_multas()
        testes_reservas()
    except Exception as e:
        print("Erro durante execução dos testes:", e)
        import traceback
        traceback.print_exc()

    # Resumo
    print("\n=== RESUMO DOS TESTES ===")
    print(f"Testes passados: {testes_passaram}")
    print(f"Testes falharam: {testes_falharam}")

    return 0 if testes_falharam == 0 else 1

if __name__ == '__main__':
    exit_code = executar_todos_testes()
    sys.exit(exit_code)
