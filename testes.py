"""
Suite de testes completa para a aplicação de Biblioteca
Testa todas as funcionalidades: usuários, itens, empréstimos, reservas e renovações
"""

import sys
import datetime
from modelos.biblioteca import Biblioteca
from modelos.livro import Livro
from modelos.ebook import Ebook
from modelos.membro import Membro
from modelos.administrador import Administrador
from modelos.bibliotecario import Bibliotecario
from config import PRAZO_DEVOLUCAO, LIMITE_RENOVACOES, LIMITE_EMPRESTIMOS_SIMULTANEOS

# Cores para output
VERDE = '\033[92m'
VERMELHO = '\033[91m'
AMARELO = '\033[93m'
RESET = '\033[0m'
NEGRITO = '\033[1m'

# Contadores
testes_passaram = 0
testes_falharam = 0

def teste_passou(nome_teste):
    global testes_passaram
    testes_passaram += 1
    print(f"{VERDE}✓ PASSOU{RESET}: {nome_teste}")

def teste_falhou(nome_teste, erro):
    global testes_falharam
    testes_falharam += 1
    print(f"{VERMELHO}✗ FALHOU{RESET}: {nome_teste}")
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
        teste_falhou(nome_teste, f"Esperava {tipo_excecao.__name__}, mas recebeu {type(e).__name__}: {e}")

# ============ TESTES DE USUÁRIOS ============
def testes_usuarios():
    print(f"\n{NEGRITO}=== TESTES DE USUÁRIOS ==={RESET}\n")
    
    bib = Biblioteca()
    
    # Teste 1: Adicionar usuário tipo Membro
    try:
        bib.adicionar_usuario('João Silva', 'joao@email.com', 'senha123', '123.456.789-10', 'membro')
        teste_assert(len(bib.usuarios) == 1, "Adicionar usuário Membro")
    except Exception as e:
        teste_falhou("Adicionar usuário Membro", str(e))
    
    # Teste 2: Adicionar usuário tipo Administrador
    try:
        bib.adicionar_usuario('Admin User', 'admin@email.com', 'senha123', '987.654.321-00', 'administrador')
        teste_assert(len(bib.usuarios) == 2, "Adicionar usuário Administrador")
    except Exception as e:
        teste_falhou("Adicionar usuário Administrador", str(e))
    
    # Teste 3: Adicionar usuário tipo Bibliotecário
    try:
        bib.adicionar_usuario('Bibliotecário User', 'biblio@email.com', 'senha123', '111.222.333-44', 'bibliotecario')
        teste_assert(len(bib.usuarios) == 3, "Adicionar usuário Bibliotecário")
    except Exception as e:
        teste_falhou("Adicionar usuário Bibliotecário", str(e))
    
    # Teste 4: Remover usuário existente (remover um Bibliotecário, mantendo Membro e Administrador)
    try:
        biblio_user = next((u for u in bib.usuarios if isinstance(u, Bibliotecario)), None)
        if not biblio_user:
            raise RuntimeError('Bibliotecário não encontrado para remoção')
        bib.remover_usuario(biblio_user.id)
        teste_assert(len(bib.usuarios) == 2, "Remover usuário existente")
    except Exception as e:
        teste_falhou("Remover usuário existente", str(e))
    
    # Teste 5: Tentar remover usuário inexistente
    teste_exception(
        bib.remover_usuario,
        ValueError,
        "Remover usuário inexistente lança ValueError",
        id="id_inexistente"
    )
    
    # Teste 6: Verificar presença de tipos de usuário (independente da ordem)
    try:
        existe_membro = any(isinstance(u, Membro) for u in bib.usuarios)
        existe_admin = any(isinstance(u, Administrador) for u in bib.usuarios)
        teste_assert(existe_membro, "Existe um usuário do tipo Membro")
        teste_assert(existe_admin, "Existe um usuário do tipo Administrador")
    except Exception as e:
        teste_falhou("Verificar tipos de usuário", str(e))

# ============ TESTES DE ITENS (LIVROS E EBOOKS) ============
def testes_itens():
    print(f"\n{NEGRITO}=== TESTES DE ITENS (LIVROS E EBOOKS) ==={RESET}\n")
    
    bib = Biblioteca()
    
    # Teste 1: Adicionar Livro
    try:
        livro = Livro('Python Avançado', None, None, 'Gustavo Peretti', 450, '978-3-16-148410-0', 'Programação')
        bib.adicionar_item(livro)
        teste_assert(len(bib.itens) == 1, "Adicionar Livro à biblioteca")
    except Exception as e:
        teste_falhou("Adicionar Livro", str(e))
    
    # Teste 2: Adicionar Ebook
    try:
        ebook = Ebook('Clean Code', None, None, 'Robert Martin', 400, '978-0-13-235088-4', 'Programação', 'clean_code.pdf', 'https://example.com/clean-code')
        bib.adicionar_item(ebook)
        teste_assert(len(bib.itens) == 2, "Adicionar Ebook à biblioteca")
    except Exception as e:
        teste_falhou("Adicionar Ebook", str(e))
    
    # Teste 3: Remover item existente
    try:
        item_id = bib.itens[0].id
        bib.remover_item(item_id)
        teste_assert(len(bib.itens) == 1, "Remover item existente")
    except Exception as e:
        teste_falhou("Remover item existente", str(e))
    
    # Teste 4: Tentar remover item inexistente
    teste_exception(
        bib.remover_item,
        ValueError,
        "Remover item inexistente lança ValueError",
        id="id_inexistente"
    )
    
    # Teste 5: Verificar propriedades do item
    ebook = bib.itens[0]
    teste_assert(ebook.nome == 'Clean Code', "Nome do item está correto")
    teste_assert(ebook.autor == 'Robert Martin', "Autor do item está correto")
    teste_assert(ebook.isbn == '978-0-13-235088-4', "ISBN do item está correto")

# ============ TESTES DE EMPRÉSTIMOS ============
def testes_emprestimos():
    print(f"\n{NEGRITO}=== TESTES DE EMPRÉSTIMOS ==={RESET}\n")
    
    bib = Biblioteca()
    
    # Setup
    membro = Membro('João Silva', 'joao@email.com', 'senha123', '123.456.789-10')
    bib.usuarios.append(membro)
    
    livro = Livro('Python Avançado', None, None, 'Gustavo Peretti', 450, '978-3-16-148410-0', 'Programação')
    bib.adicionar_item(livro)
    
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
    admin = Administrador('Admin', 'admin@email.com', 'senha123', '987.654.321-00')
    livro2 = Livro('Design Patterns', None, None, 'Gang of Four', 416, '978-0-201-63361-0', 'Programação')
    bib.adicionar_item(livro2)
    
    teste_exception(
        bib.emprestar_item,
        TypeError,
        "Emprestar para não-membro lança TypeError",
        item=livro2,
        membro=admin
    )
    
    # Teste 4: Ultrapassar limite de empréstimos
    # Criar múltiplos empréstimos até o limite
    membro2 = Membro('Maria', 'maria@email.com', 'senha123', '111.222.333-44')
    bib.usuarios.append(membro2)
    
    # Criar e emprestar muitos livros
    for i in range(LIMITE_EMPRESTIMOS_SIMULTANEOS):
        livro_temp = Livro(f'Livro {i}', None, None, f'Autor {i}', 300, f'978-0-00000-{i:04d}', 'Teste')
        bib.adicionar_item(livro_temp)
        bib.emprestar_item(livro_temp, membro2)
    
    # Agora tentar emprestar mais um deve falhar
    livro_extra = Livro('Livro Extra', None, None, 'Autor Extra', 300, '978-9-99999-9999', 'Teste')
    bib.adicionar_item(livro_extra)
    
    teste_exception(
        bib.emprestar_item,
        ValueError,
        "Ultrapassar limite de empréstimos lança ValueError",
        item=livro_extra,
        membro=membro2
    )

# ============ TESTES DE RESERVAS ============
def testes_reservas():
    print(f"\n{NEGRITO}=== TESTES DE RESERVAS ==={RESET}\n")
    
    bib = Biblioteca()
    
    # Setup
    membro1 = Membro('João', 'joao@email.com', 'senha123', '123.456.789-10')
    membro2 = Membro('Maria', 'maria@email.com', 'senha123', '111.222.333-44')
    bib.usuarios.extend([membro1, membro2])
    
    livro = Livro('Python Avançado', None, None, 'Gustavo Peretti', 450, '978-3-16-148410-0', 'Programação')
    bib.adicionar_item(livro)
    
    # Teste 1: Não é possível reservar item disponível
    teste_exception(
        bib.reservar_item,
        ValueError,
        "Reservar item disponível lança ValueError",
        item=livro,
        membro=membro1
    )
    
    # Teste 2: Emprestar para que o item fique indisponível
    bib.emprestar_item(livro, membro1)
    
    # Teste 3: Reservar item emprestado
    try:
        bib.reservar_item(livro, membro2)
        teste_assert(len(bib.reservas) == 1, "Reservar item indisponível")
    except Exception as e:
        teste_falhou("Reservar item indisponível", str(e))
    
    # Teste 4: Verificar status da reserva
    reserva = bib.reservas[0]
    teste_assert(reserva.status == 'aguardando', "Status da reserva é 'aguardando'")
    
    # Teste 5: Não é possível reservar item duas vezes pelo mesmo membro
    teste_exception(
        bib.reservar_item,
        ValueError,
        "Reservar item duas vezes lança ValueError",
        item=livro,
        membro=membro2
    )
    
    # Teste 6: Tentar reservar para não-membro
    admin = Administrador('Admin', 'admin@email.com', 'senha123', '987.654.321-00')
    livro2 = Livro('Design Patterns', None, None, 'Gang of Four', 416, '978-0-201-63361-0', 'Programação')
    bib.adicionar_item(livro2)
    bib.emprestar_item(livro2, membro1)
    
    teste_exception(
        bib.reservar_item,
        TypeError,
        "Reservar para não-membro lança TypeError",
        item=livro2,
        membro=admin
    )

# ============ TESTES DE RENOVAÇÃO ============
def testes_renovacoes():
    print(f"\n{NEGRITO}=== TESTES DE RENOVAÇÕES ==={RESET}\n")
    
    bib = Biblioteca()
    
    # Setup
    membro = Membro('João Silva', 'joao@email.com', 'senha123', '123.456.789-10')
    bib.usuarios.append(membro)
    
    livro = Livro('Python Avançado', None, None, 'Gustavo Peretti', 450, '978-3-16-148410-0', 'Programação')
    bib.adicionar_item(livro)
    
    # Emprestar
    bib.emprestar_item(livro, membro)
    emprestimo = bib.emprestimos[0]
    
    # Teste 1: Não é possível renovar logo após emprestar (precisa esperar 2 dias antes da devolução)
    teste_exception(
        bib.renovar_emprestimo,
        ValueError,
        "Renovar logo após emprestar lança ValueError",
        id_emprestimo=emprestimo.id
    )
    
    # Teste 2: Tentativa de renovar empréstimo inexistente
    teste_exception(
        bib.renovar_emprestimo,
        ValueError,
        "Renovar empréstimo inexistente lança ValueError",
        id_emprestimo="id_inexistente"
    )
    
    # Teste 3: Simular data futura para permitir renovação (alterando o objeto diretamente para teste)
    # Ajustar data de empréstimo para permitir renovação
    dias_atraso = PRAZO_DEVOLUCAO - 1  # 1 dia antes do prazo
    emprestimo._data_emprestimo = datetime.datetime.now() - datetime.timedelta(days=dias_atraso)
    
    try:
        emprestimo_renovado = bib.renovar_emprestimo(emprestimo.id)
        teste_assert(emprestimo_renovado._quantidade_renovacoes == 1, "Renovação incrementa contador")
    except Exception as e:
        teste_falhou("Renovar empréstimo válido", str(e))
    
    # Teste 4: Renovar múltiplas vezes até o limite
    for i in range(LIMITE_RENOVACOES - 1):
        emprestimo._data_emprestimo = datetime.datetime.now() - datetime.timedelta(days=(i+2)*PRAZO_DEVOLUCAO - 1)
        try:
            bib.renovar_emprestimo(emprestimo.id)
        except ValueError:
            break
    
    teste_assert(
        emprestimo._quantidade_renovacoes <= LIMITE_RENOVACOES,
        "Número de renovações não ultrapassa limite"
    )
    
    # Teste 5: Tentar renovar além do limite
    teste_exception(
        bib.renovar_emprestimo,
        ValueError,
        "Renovar além do limite lança ValueError",
        id_emprestimo=emprestimo.id
    )

# ============ TESTES DE DEVOLUÇÕES E MULTAS ============
def testes_devolucoes_multas():
    print(f"\n{NEGRITO}=== TESTES DE DEVOLUÇÕES E MULTAS ==={RESET}\n")
    
    bib = Biblioteca()
    
    # Setup
    membro = Membro('João Silva', 'joao@email.com', 'senha123', '123.456.789-10')
    bib.usuarios.append(membro)
    
    livro = Livro('Python Avançado', None, None, 'Gustavo Peretti', 450, '978-3-16-148410-0', 'Programação')
    bib.adicionar_item(livro)
    
    # Emprestar
    bib.emprestar_item(livro, membro)
    emprestimo = bib.emprestimos[0]
    
    # Teste 1: Devolução no prazo
    try:
        emprestimo_devolvido = bib.registrar_devolucao(emprestimo.id)
        teste_assert(emprestimo_devolvido.status == 'finalizado', "Devolução no prazo finaliza empréstimo")
        teste_assert(emprestimo_devolvido.multa is None, "Devolução no prazo não gera multa")
    except Exception as e:
        teste_falhou("Devolução no prazo", str(e))
    
    # Teste 2: Devolução com atraso (gera multa)
    livro2 = Livro('Design Patterns', None, None, 'Gang of Four', 416, '978-0-201-63361-0', 'Programação')
    bib.adicionar_item(livro2)
    bib.emprestar_item(livro2, membro)
    emprestimo2 = bib.emprestimos[1]
    
    # Simular atraso: alterar data de empréstimo para passado
    emprestimo2._data_emprestimo = datetime.datetime.now() - datetime.timedelta(days=PRAZO_DEVOLUCAO + 5)
    
    try:
        emprestimo_atrasado = bib.registrar_devolucao(emprestimo2.id)
        teste_assert(emprestimo_atrasado.status == 'multado', "Devolução atrasada gera multa")
        teste_assert(emprestimo_atrasado.multa is not None, "Multa foi criada")
        teste_assert(emprestimo_atrasado.multa.paga == False, "Multa está não paga inicialmente")
    except Exception as e:
        teste_falhou("Devolução com atraso", str(e))
    
    # Teste 3: Pagar multa
    try:
        emprestimo_quitado = bib.registrar_pagamento_multa(emprestimo2.id)
        teste_assert(emprestimo_quitado.status == 'finalizado', "Pagamento de multa finaliza empréstimo")
        teste_assert(emprestimo_quitado.multa.paga == True, "Multa marcada como paga")
    except Exception as e:
        teste_falhou("Pagar multa", str(e))

# ============ TESTES DE FILA DE RESERVA ============
def testes_fila_reserva():
    print(f"\n{NEGRITO}=== TESTES DE FILA DE RESERVA ==={RESET}\n")
    
    bib = Biblioteca()
    
    # Setup
    membro1 = Membro('João', 'joao@email.com', 'senha123', '123.456.789-10')
    membro2 = Membro('Maria', 'maria@email.com', 'senha123', '111.222.333-44')
    membro3 = Membro('Pedro', 'pedro@email.com', 'senha123', '222.333.444-55')
    bib.usuarios.extend([membro1, membro2, membro3])
    
    livro = Livro('Python Avançado', None, None, 'Gustavo Peretti', 450, '978-3-16-148410-0', 'Programação')
    bib.adicionar_item(livro)
    
    # Emprestar para membro1
    bib.emprestar_item(livro, membro1)
    emprestimo = bib.emprestimos[0]
    
    # Reservar para membro2 e membro3
    bib.reservar_item(livro, membro2)
    bib.reservar_item(livro, membro3)
    
    teste_assert(len(bib.reservas) == 2, "Duas reservas criadas")
    
    # Teste 1: Apenas primeiro da fila pode emprestar
    teste_exception(
        bib.emprestar_item,
        ValueError,
        "Apenas primeiro da fila pode emprestar",
        item=livro,
        membro=membro3
    )
    
    # Teste 2: Primeiro da fila consegue emprestar após devolução
    bib.registrar_devolucao(emprestimo.id)
    
    try:
        bib.emprestar_item(livro, membro3)
        teste_assert(len(bib.emprestimos) == 2, "Primeiro da fila consegue emprestar")
    except Exception as e:
        teste_falhou("Primeiro da fila consegue emprestar", str(e))
    
    # Teste 3: Reserva foi marcada como finalizada
    primeira_reserva = bib.reservas[0]
    teste_assert(primeira_reserva.status == 'finalizada', "Primeira reserva marcada como finalizada")

# ============ FUNÇÃO PRINCIPAL ============
def executar_todos_testes():
    print(f"\n{NEGRITO}{'='*60}")
    print("EXECUTANDO SUITE COMPLETA DE TESTES - SISTEMA DE BIBLIOTECA")
    print(f"{'='*60}{RESET}\n")
    
    try:
        testes_usuarios()
        testes_itens()
        testes_emprestimos()
        testes_reservas()
        testes_renovacoes()
        testes_devolucoes_multas()
        testes_fila_reserva()
    except Exception as e:
        print(f"\n{VERMELHO}ERRO CRÍTICO NA SUITE DE TESTES:{RESET}")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # Resumo final
    total_testes = testes_passaram + testes_falharam
    percentual = (testes_passaram / total_testes * 100) if total_testes > 0 else 0
    
    print(f"\n{NEGRITO}{'='*60}")
    print("RESUMO DOS TESTES")
    print(f"{'='*60}{RESET}")
    print(f"Total de testes: {total_testes}")
    print(f"{VERDE}Testes que passaram: {testes_passaram}{RESET}")
    print(f"{VERMELHO}Testes que falharam: {testes_falharam}{RESET}")
    print(f"Taxa de sucesso: {percentual:.1f}%\n")
    
    if testes_falharam == 0:
        print(f"{VERDE}{NEGRITO}✓ TODOS OS TESTES PASSARAM!{RESET}\n")
        return 0
    else:
        print(f"{VERMELHO}{NEGRITO}✗ ALGUNS TESTES FALHARAM!{RESET}\n")
        return 1

if __name__ == '__main__':
    exit_code = executar_todos_testes()
    sys.exit(exit_code)
