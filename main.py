import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import unicodedata
import re

# Ajuste do path para importar módulos que usam import sem pacote
sys.path.append(os.path.join(os.path.dirname(__file__), 'modelos'))

from biblioteca import Biblioteca
from livro import Livro
from ebook import Ebook
from emprestimo import Emprestimo
from multa import Multa
from config import MULTA_POR_DIA
from membro import Membro


class App(tk.Tk):
    """GUI simples para a biblioteca usando Tkinter puro.

    Comentários em português; identificadores em inglês.
    """

    def __init__(self):
        super().__init__()
        self.title('Biblioteca - GUI')
        self.geometry('1000x600')
        # Fonte e estilo base - usar tupla para evitar parsing incorreto do Tk
        try:
            self.option_add('*Font', ('Segoe UI', 10))
        except Exception:
            try:
                self.option_add('*Font', ('Arial', 10))
            except Exception:
                pass

        self.library = Biblioteca()

        # dados de exemplo para facilitar testes
        self.library.adicionar_usuario('João', 'joao@example.com', '123', '12345678900', 'membro')
        self.library.adicionar_usuario('Maria', 'maria@example.com', '123', '98765432100', 'bibliotecario')
        self.library.adicionar_item(Livro('Aprendendo Python', '', '', 'Luciano', 300, '111', 'Programação'))

        # mapeamento de objetos para Treeview
        self.items_map = {}
        self.users_map = {}
        self.loans_map = {}
        self.reservations_map = {}
        # empréstimo pendente iniciado pela aba usuários
        self.pending_loan_member = None

        self.create_widgets()
        self.refresh_all()

    def setup_style(self):
        # configura tema e estilos do ttk para um visual mais limpo
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Treeview: linha maior e cabeçalho em negrito
        style.configure('Treeview', rowheight=26, font=('Segoe UI', 10), fieldbackground='#FFFFFF')
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        style.configure('TButton', padding=(6, 3))
        style.configure('TEntry', padding=(3, 3))


    def create_widgets(self):
        notebook = ttk.Notebook(self)
        self.notebook = notebook
        notebook.pack(fill='both', expand=True)

        self.frame_items = ttk.Frame(notebook)
        self.frame_users = ttk.Frame(notebook)
        self.frame_loans = ttk.Frame(notebook)
        self.frame_reservations = ttk.Frame(notebook)

        notebook.add(self.frame_items, text='Catálogo')
        notebook.add(self.frame_users, text='Usuários')
        # aba para registrar empréstimo em layout amplo com duas tabelas lado-a-lado
        self.frame_register = ttk.Frame(notebook)
        notebook.add(self.frame_register, text='Registrar Empréstimo')
        notebook.add(self.frame_loans, text='Empréstimos')
        notebook.add(self.frame_reservations, text='Reservas')

        self.build_items_tab()
        self.build_users_tab()
        self.build_register_tab()
        self.build_loans_tab()
        self.build_reservations_tab()
        # aplicar estilo e configurações finais
        self.setup_style()
        # status bar
        self.status_var = tk.StringVar(value='Pronto')
        self.status_label = ttk.Label(self, textvariable=self.status_var, anchor='w', relief='sunken')
        self.status_label.pack(fill='x', side='bottom')

    def build_items_tab(self):
        frame = self.frame_items
        # busca
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill='x', padx=8, pady=4)

        tk.Label(search_frame, text='Buscar:').pack(side='left')
        self.entry_item_search = ttk.Entry(search_frame)
        self.entry_item_search.pack(side='left', padx=4)
        self.entry_item_search.bind('<KeyRelease>', lambda e: self.search_items())
        ttk.Button(search_frame, text='Pesquisar', command=self.search_items).pack(side='left', padx=4)

        # treeview
        cols = ('id', 'nome', 'autor', 'isbn', 'categoria', 'paginas', 'emprestavel')
        self.tree_items = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols:
            self.tree_items.heading(c, text=c.title())
        self.tree_items.pack(fill='both', expand=True, padx=8, pady=4)
        # detalhes do item selecionado
        self.details_item_label = ttk.Label(frame, text='', anchor='w')
        self.details_item_label.pack(fill='x', padx=8)

        # ações
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', padx=8, pady=4)
        self.btn_add_item = ttk.Button(action_frame, text='Adicionar Item', command=self.add_item_window)
        self.btn_add_item.pack(side='left')
        self.btn_edit_item = ttk.Button(action_frame, text='Editar Item', command=self.edit_item_window, state='disabled')
        self.btn_edit_item.pack(side='left')
        self.btn_remove_item = ttk.Button(action_frame, text='Remover Item', command=self.remove_item, state='disabled')
        self.btn_remove_item.pack(side='left')
        self.btn_confirm_loan = ttk.Button(action_frame, text='Emprestar Selecionado', command=self.confirm_loan_for_pending, state='disabled')
        self.btn_confirm_loan.pack(side='left')
        self.btn_cancel_pending = ttk.Button(action_frame, text='Cancelar Empréstimo', command=self.cancel_pending_loan, state='disabled')
        self.btn_cancel_pending.pack(side='left')
        # label mostrando usuário pendente para emprestar
        self.pending_loan_label = ttk.Label(action_frame, text='')
        self.pending_loan_label.pack(side='right', padx=8)
        # seleção
        self.tree_items.bind('<<TreeviewSelect>>', self.on_item_select)

    def build_users_tab(self):
        frame = self.frame_users
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill='x', padx=8, pady=4)
        tk.Label(search_frame, text='Buscar:').pack(side='left')
        self.entry_user_search = ttk.Entry(search_frame)
        self.entry_user_search.pack(side='left', padx=4)
        self.entry_user_search.bind('<KeyRelease>', lambda e: self.search_users())
        ttk.Button(search_frame, text='Pesquisar', command=self.search_users).pack(side='left', padx=4)

        cols = ('id', 'nome', 'email', 'cpf', 'tipo')
        self.tree_users = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols:
            self.tree_users.heading(c, text=c.title())
        self.tree_users.pack(fill='both', expand=True, padx=8, pady=4)
        self.details_user_label = ttk.Label(frame, text='', anchor='w')
        self.details_user_label.pack(fill='x', padx=8)

        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', padx=8, pady=4)
        ttk.Button(action_frame, text='Adicionar Usuário', command=self.add_user_window).pack(side='left')
        self.btn_edit_user = ttk.Button(action_frame, text='Editar Usuário', command=self.edit_user_window, state='disabled')
        self.btn_edit_user.pack(side='left')
        self.btn_remove_user = ttk.Button(action_frame, text='Remover Usuário', command=self.remove_user, state='disabled')
        self.btn_remove_user.pack(side='left')
        self.btn_emprestar_user = ttk.Button(action_frame, text='Emprestar', command=self.start_loan_for_user, state='disabled')
        self.btn_emprestar_user.pack(side='left')
        self.tree_users.bind('<<TreeviewSelect>>', self.on_user_select)

    def build_loans_tab(self):
        frame = self.frame_loans
        cols = ('id', 'item', 'membro', 'data_emp', 'data_prev', 'renovacoes', 'status', 'multa')
        self.tree_loans = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols:
            self.tree_loans.heading(c, text=c.title())
        self.tree_loans.pack(fill='both', expand=True, padx=8, pady=4)
        # configurar tags para destacar linhas (ex.: multado) e alternância de cores
        self.tree_loans.tag_configure('multado', background='#ffe6e6')
        self.tree_loans.tag_configure('odd', background='#ffffff')
        self.tree_loans.tag_configure('even', background='#f6f6f6')

        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', padx=8, pady=4)
        self.btn_renew = ttk.Button(action_frame, text='Renovar', command=self.renew_loan, state='disabled')
        self.btn_renew.pack(side='left')
        self.btn_return = ttk.Button(action_frame, text='Devolver', command=self.return_loan, state='disabled')
        self.btn_return.pack(side='left')
        self.btn_payfine = ttk.Button(action_frame, text='Quitar Multa', command=self.pay_fine, state='disabled')
        self.btn_payfine.pack(side='left')
        self.btn_imposefine = ttk.Button(action_frame, text='Multar', command=self.impose_fine, state='disabled')
        self.btn_imposefine.pack(side='left')
        self.tree_loans.bind('<<TreeviewSelect>>', self.on_loan_select)

    def build_reservations_tab(self):
        frame = self.frame_reservations
        cols = ('id', 'item', 'membro', 'data_res', 'status', 'posicao')
        self.tree_res = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols:
            self.tree_res.heading(c, text=c.title())
        self.tree_res.pack(fill='both', expand=True, padx=8, pady=4)

        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', padx=8, pady=4)
        ttk.Button(action_frame, text='Reservar Item', command=self.reserve_item_window).pack(side='left')
        ttk.Button(action_frame, text='Cancelar Reserva', command=self.cancel_reservation).pack(side='left')
        ttk.Button(action_frame, text='Finalizar Reserva', command=self.finish_reservation).pack(side='left')

    # ---------- aba Registrar Empréstimo (duas tabelas lado-a-lado) ----------
    def strip_accents(self, s: str) -> str:
        if not s:
            return ''
        nk = unicodedata.normalize('NFKD', s)
        return ''.join(c for c in nk if not unicodedata.combining(c)).lower()

    def build_register_tab(self):
        f = self.frame_register
        # usar PanedWindow horizontal para dividir espaço igualmente
        paned = ttk.PanedWindow(f, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=6, pady=6)

        # painel esquerdo: usuários (apenas membros)
        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        search_u = ttk.Frame(left)
        search_u.pack(fill='x', padx=6, pady=4)
        ttk.Label(search_u, text='Buscar usuário:').pack(side='left')
        self.entry_reg_user_search = ttk.Entry(search_u)
        self.entry_reg_user_search.pack(side='left', padx=4, fill='x', expand=True)
        self.entry_reg_user_search.bind('<KeyRelease>', lambda e: self.refresh_register_users())

        cols_u = ('id', 'nome', 'email', 'cpf')
        self.tree_reg_users = ttk.Treeview(left, columns=cols_u, show='headings')
        for c in cols_u:
            self.tree_reg_users.heading(c, text=c.title())
        self.tree_reg_users.pack(fill='both', expand=True, padx=6, pady=4)
        self.tree_reg_users.bind('<<TreeviewSelect>>', self.on_register_user_select)

        # painel direito: catálogo
        right = ttk.Frame(paned)
        paned.add(right, weight=1)
        search_i = ttk.Frame(right)
        search_i.pack(fill='x', padx=6, pady=4)
        ttk.Label(search_i, text='Buscar item:').pack(side='left')
        self.entry_reg_item_search = ttk.Entry(search_i)
        self.entry_reg_item_search.pack(side='left', padx=4, fill='x', expand=True)
        self.entry_reg_item_search.bind('<KeyRelease>', lambda e: self.refresh_register_items())

        cols_i = ('id', 'nome', 'autor', 'categoria', 'emprestavel')
        self.tree_reg_items = ttk.Treeview(right, columns=cols_i, show='headings')
        for c in cols_i:
            self.tree_reg_items.heading(c, text=c.title())
        self.tree_reg_items.pack(fill='both', expand=True, padx=6, pady=4)
        self.tree_reg_items.bind('<<TreeviewSelect>>', self.on_register_item_select)

        # rodapé com confirmação
        footer = ttk.Frame(f)
        footer.pack(fill='x', padx=6, pady=6)
        self.lbl_reg_selected = ttk.Label(footer, text='Nenhum usuário/item selecionado')
        self.lbl_reg_selected.pack(side='left')
        self.btn_confirm_register = ttk.Button(footer, text='Confirmar Empréstimo', command=self.confirm_register_loan, state='disabled')
        self.btn_confirm_register.pack(side='right')

        # inicializar conteúdos
        self.refresh_register_users()
        self.refresh_register_items()

    def refresh_register_users(self):
        q = self.entry_reg_user_search.get() if hasattr(self, 'entry_reg_user_search') else ''
        qn = self.strip_accents(q)
        for r in self.tree_reg_users.get_children():
            self.tree_reg_users.delete(r)
        users = [u for u in self.library.usuarios if u.__class__.__name__ == 'Membro']
        for u in users:
            txt = f"{u.nome} {u.email} {u.cpf}"
            if qn and qn not in self.strip_accents(txt):
                continue
            uid = str(u.id)
            self.tree_reg_users.insert('', 'end', uid, values=(uid, u.nome, u.email, u.cpf))

    def refresh_register_items(self):
        q = self.entry_reg_item_search.get() if hasattr(self, 'entry_reg_item_search') else ''
        qn = self.strip_accents(q)
        for r in self.tree_reg_items.get_children():
            self.tree_reg_items.delete(r)
        for it in self.library.itens:
            txt = f"{it.nome} {getattr(it, 'autor', '')} {getattr(it, 'categoria', '')}"
            if qn and qn not in self.strip_accents(txt):
                continue
            iid = str(it.id)
            emprest = 'Sim' if getattr(it, 'emprestavel', True) else 'Não'
            self.tree_reg_items.insert('', 'end', iid, values=(iid, it.nome, getattr(it, 'autor', ''), getattr(it, 'categoria', ''), emprest))

    def on_register_user_select(self, event=None):
        sel = self.tree_reg_users.selection()
        self.update_register_footer()

    def on_register_item_select(self, event=None):
        sel = self.tree_reg_items.selection()
        self.update_register_footer()

    def update_register_footer(self):
        u_sel = self.tree_reg_users.selection()
        i_sel = self.tree_reg_items.selection()
        if u_sel and i_sel:
            u = self.library.usuarios[int(u_sel[0]) - 1] if False else None
        # safer: read from items/users maps by id from trees
        user_text = '---'
        item_text = '---'
        if u_sel:
            try:
                uid = u_sel[0]
                user = next((x for x in self.library.usuarios if str(x.id) == uid), None)
                if user:
                    user_text = user.nome
            except Exception:
                pass
        if i_sel:
            try:
                iid = i_sel[0]
                item = next((x for x in self.library.itens if str(x.id) == iid), None)
                if item:
                    item_text = item.nome
            except Exception:
                pass
        self.lbl_reg_selected.config(text=f'Usuário: {user_text}  |  Item: {item_text}')
        # habilitar confirmar somente se ambos selecionados e item emprestavel
        enabled = False
        if u_sel and i_sel:
            uid = u_sel[0]; iid = i_sel[0]
            user = next((x for x in self.library.usuarios if str(x.id) == uid), None)
            item = next((x for x in self.library.itens if str(x.id) == iid), None)
            if user and item and getattr(item, 'emprestavel', True) and user.__class__.__name__ == 'Membro':
                enabled = True
        self.btn_confirm_register.config(state='normal' if enabled else 'disabled')

    def confirm_register_loan(self):
        u_sel = self.tree_reg_users.selection()
        i_sel = self.tree_reg_items.selection()
        if not (u_sel and i_sel):
            messagebox.showinfo('Info', 'Selecione usuário e item para registrar o empréstimo')
            return
        uid = u_sel[0]; iid = i_sel[0]
        user = next((x for x in self.library.usuarios if str(x.id) == uid), None)
        item = next((x for x in self.library.itens if str(x.id) == iid), None)
        if not user or not item:
            messagebox.showerror('Erro', 'Seleção inválida')
            return
        try:
            self.library.emprestar_item(item, user)
        except Exception as ex:
            messagebox.showerror('Erro', str(ex))
            return
        self.set_status(f'Empréstimo registrado: {user.nome} → {item.nome}', 4000)
        self.refresh_all()

    # ---------- operações leitura/refresh ----------
    def refresh_items(self, filter_text=''):
        for row in self.tree_items.get_children():
            self.tree_items.delete(row)
        self.items_map.clear()
        for it in self.library.itens:
            if filter_text and filter_text.lower() not in it.nome.lower():
                continue
            iid = str(it.id)
            self.items_map[iid] = it
            self.tree_items.insert('', 'end', iid, values=(iid, it.nome, it.autor, it.isbn, it.categoria, it.num_paginas, 'Sim' if it.emprestavel else 'Não'))
        # atualizar seleção/estado dos botões
        self.on_item_select()

    def refresh_users(self, filter_text=''):
        for row in self.tree_users.get_children():
            self.tree_users.delete(row)
        self.users_map.clear()
        for u in self.library.usuarios:
            if filter_text and filter_text.lower() not in u.nome.lower():
                continue
            uid = str(u.id)
            self.users_map[uid] = u
            tipo = u.__class__.__name__
            self.tree_users.insert('', 'end', uid, values=(uid, u.nome, u.email, u.cpf, tipo))
        self.on_user_select()

    def refresh_loans(self):
        for row in self.tree_loans.get_children():
            self.tree_loans.delete(row)
        self.loans_map.clear()
        i = 0
        for e in self.library.emprestimos:
            iid = str(e.id)
            self.loans_map[iid] = e
            multa = f"{e.multa.valor:.2f}" if e.multa else ''
            # tags: multado tem prioridade; senão alternar odd/even
            tags = []
            if e.status == 'multado':
                tags.append('multado')
            else:
                tags.append('even' if i % 2 == 0 else 'odd')

            self.tree_loans.insert('', 'end', iid, values=(iid, e.item.nome, e.membro.nome, e.data_emprestimo.strftime('%d/%m/%Y'), e.data_prevista_devolucao.strftime('%d/%m/%Y'), getattr(e, '_quantidade_renovacoes', 0), e.status, multa), tags=tags)
            i += 1
        self.on_loan_select()

    def refresh_reservations(self):
        for row in self.tree_res.get_children():
            self.tree_res.delete(row)
        self.reservations_map.clear()
        # ordenar por data
        reservas = sorted(self.library.reservas, key=lambda r: r.data_reserva)
        for idx, r in enumerate(reservas):
            iid = str(r.id)
            self.reservations_map[iid] = r
            pos = idx + 1
            self.tree_res.insert('', 'end', iid, values=(iid, r.item.nome, r.membro.nome, r.data_reserva.strftime('%d/%m/%Y'), r.status, pos))

    def refresh_all(self):
        self.refresh_items()
        self.refresh_users()
        self.refresh_loans()
        self.refresh_reservations()
        self.update_pending_loan_ui()

    # ---------- utilitários de UI ----------
    def set_status(self, msg, timeout=3000):
        try:
            self.status_var.set(msg)
            if timeout:
                if hasattr(self, '_clear_status_after') and self._clear_status_after:
                    try:
                        self.after_cancel(self._clear_status_after)
                    except Exception:
                        pass
                self._clear_status_after = self.after(timeout, lambda: self.status_var.set('Pronto'))
        except Exception:
            pass

    def on_item_select(self, event=None):
        sel = self.tree_items.selection()
        if not sel:
            self.details_item_label.config(text='')
            self.btn_edit_item.config(state='disabled')
            self.btn_remove_item.config(state='disabled')
            # confirmar emprestimo só se houver pending member
            if not self.pending_loan_member:
                self.btn_confirm_loan.config(state='disabled')
            return
        obj = self.items_map[sel[0]]
        txt = f"{obj.nome} — {obj.autor} | {obj.categoria} | Páginas: {getattr(obj, 'num_paginas', '')}"
        self.details_item_label.config(text=txt)
        self.btn_edit_item.config(state='normal')
        self.btn_remove_item.config(state='normal')
        # permitir emprestar se houver membro pendente e item emprestavel
        if self.pending_loan_member and getattr(obj, 'emprestavel', True):
            self.btn_confirm_loan.config(state='normal')
        else:
            self.btn_confirm_loan.config(state='disabled')

    def on_user_select(self, event=None):
        sel = self.tree_users.selection()
        if not sel:
            self.details_user_label.config(text='')
            self.btn_edit_user.config(state='disabled')
            self.btn_remove_user.config(state='disabled')
            self.btn_emprestar_user.config(state='disabled')
            return
        u = self.users_map[sel[0]]
        tipo = u.__class__.__name__
        txt = f"{u.nome} — {u.email} | CPF: {u.cpf} | Tipo: {tipo}"
        self.details_user_label.config(text=txt)
        self.btn_edit_user.config(state='normal')
        self.btn_remove_user.config(state='normal')
        # emprestar habilitado apenas para membros
        if isinstance(u, Membro):
            self.btn_emprestar_user.config(state='normal')
        else:
            self.btn_emprestar_user.config(state='disabled')

    def on_loan_select(self, event=None):
        sel = self.tree_loans.selection()
        if not sel:
            self.btn_renew.config(state='disabled')
            self.btn_return.config(state='disabled')
            self.btn_payfine.config(state='disabled')
            self.btn_imposefine.config(state='disabled')
            return
        e = self.loans_map[sel[0]]
        # status-driven enabling
        if e.status in ('ativo', 'emprestado'):
            self.btn_renew.config(state='normal')
            self.btn_return.config(state='normal')
        else:
            self.btn_renew.config(state='disabled')
            self.btn_return.config(state='disabled')
        if e.multa and not getattr(e.multa, 'paga', False):
            self.btn_payfine.config(state='normal')
        else:
            self.btn_payfine.config(state='disabled')
        # sempre permitir multar manualmente para ajuste
        self.btn_imposefine.config(state='normal')

    # ---------- ações de formulários ----------
    def search_items(self):
        self.refresh_items(self.entry_item_search.get())

    def add_item_window(self):
        def save():
            nome = en_nome.get()
            autor = en_autor.get()
            isbn = en_isbn.get()
            categoria = en_categoria.get()
            try:
                paginas = int(en_paginas.get())
            except ValueError:
                paginas = 0
            # validações
            if not self.is_valid_name(nome):
                messagebox.showerror('Erro', 'Nome do livro inválido. Não utilize números ou símbolos estranhos.')
                return
            if autor and not self.is_valid_name(autor):
                messagebox.showerror('Erro', 'Nome do autor inválido.')
                return
            if isbn and not self.is_valid_isbn(isbn):
                messagebox.showerror('Erro', 'ISBN inválido. Informe 10 ou 13 dígitos (apenas números).')
                return
            if paginas <= 0:
                messagebox.showerror('Erro', 'Número de páginas deve ser maior que zero.')
                return
            tipo = tipo_var.get()
            if tipo == 'Livro':
                obj = Livro(nome, '', '', autor, paginas, isbn, categoria)
            else:
                url = en_url.get()
                obj = Ebook(nome, '', '', autor, paginas, isbn, categoria, '', url)
            self.library.adicionar_item(obj)
            top.destroy()
            self.refresh_items()

        top = tk.Toplevel(self)
        top.title('Adicionar Item')
        tk.Label(top, text='Nome').pack(); en_nome = ttk.Entry(top); en_nome.pack()
        tk.Label(top, text='Autor').pack(); en_autor = ttk.Entry(top); en_autor.pack()
        tk.Label(top, text='ISBN').pack(); en_isbn = ttk.Entry(top); en_isbn.pack()
        tk.Label(top, text='Categoria').pack(); en_categoria = ttk.Entry(top); en_categoria.pack()
        tk.Label(top, text='Páginas').pack(); en_paginas = ttk.Entry(top); en_paginas.pack()
        tipo_var = tk.StringVar(value='Livro')
        ttk.Radiobutton(top, text='Livro', variable=tipo_var, value='Livro').pack()
        ttk.Radiobutton(top, text='Ebook', variable=tipo_var, value='Ebook').pack()
        tk.Label(top, text='URL (Ebook)').pack(); en_url = ttk.Entry(top); en_url.pack()
        ttk.Button(top, text='Salvar', command=save).pack()

    def edit_item_window(self):
        sel = self.tree_items.selection()
        if not sel:
            messagebox.showinfo('Info', 'Selecione um item para editar')
            return
        obj = self.items_map[sel[0]]

        def save():
            obj.nome = en_nome.get()
            obj.autor = en_autor.get()
            obj.isbn = en_isbn.get()
            obj.categoria = en_categoria.get()
            try:
                obj.num_paginas = int(en_paginas.get())
            except ValueError:
                pass
            # validações
            if not self.is_valid_name(obj.nome):
                messagebox.showerror('Erro', 'Nome do livro inválido. Não utilize números ou símbolos estranhos.')
                return
            if obj.autor and not self.is_valid_name(obj.autor):
                messagebox.showerror('Erro', 'Nome do autor inválido.')
                return
            if obj.isbn and not self.is_valid_isbn(obj.isbn):
                messagebox.showerror('Erro', 'ISBN inválido. Informe 10 ou 13 dígitos (apenas números).')
                return
            top.destroy(); self.refresh_items()

        top = tk.Toplevel(self)
        top.title('Editar Item')
        tk.Label(top, text='Nome').pack(); en_nome = ttk.Entry(top); en_nome.insert(0, obj.nome); en_nome.pack()
        tk.Label(top, text='Autor').pack(); en_autor = ttk.Entry(top); en_autor.insert(0, obj.autor); en_autor.pack()
        tk.Label(top, text='ISBN').pack(); en_isbn = ttk.Entry(top); en_isbn.insert(0, obj.isbn); en_isbn.pack()
        tk.Label(top, text='Categoria').pack(); en_categoria = ttk.Entry(top); en_categoria.insert(0, obj.categoria); en_categoria.pack()
        tk.Label(top, text='Páginas').pack(); en_paginas = ttk.Entry(top); en_paginas.insert(0, obj.num_paginas); en_paginas.pack()
        ttk.Button(top, text='Salvar', command=save).pack()

    # ---------- validação de campos ----------
    def clean_digits(self, s: str) -> str:
        return ''.join(ch for ch in s if ch.isdigit())

    def is_valid_cpf(self, s: str) -> bool:
        if not s:
            return False
        nums = self.clean_digits(s)
        return len(nums) == 11

    def is_valid_name(self, s: str) -> bool:
        if not s:
            return False
        # permitir letras (incluindo acentos), espaços, hífens e apóstrofo
        for ch in s:
            if ch.isalpha() or ch.isspace() or ch in "-'":
                continue
            return False
        return True

    def is_valid_email(self, s: str) -> bool:
        if not s:
            return False
        # validação simples
        pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        return re.match(pattern, s) is not None

    def is_valid_isbn(self, s: str) -> bool:
        if not s:
            return False
        nums = self.clean_digits(s)
        return len(nums) in (10, 13)

    def remove_item(self):
        sel = self.tree_items.selection()
        if not sel:
            messagebox.showinfo('Info', 'Selecione um item para remover')
            return
        iid = sel[0]
        try:
            self.library.remover_item(self.items_map[iid].id)
        except Exception as e:
            messagebox.showerror('Erro', str(e)); return
        self.refresh_items()
        self.set_status('Item removido', 3000)

    # ---------- usuários ----------
    def search_users(self):
        self.refresh_users(self.entry_user_search.get())

    def start_loan_for_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo('Info', 'Selecione um usuário para iniciar empréstimo'); return
        user = self.users_map[sel[0]]
        # Apenas membros podem emprestar
        if not isinstance(user, Membro):
            messagebox.showerror('Erro', 'Apenas membros podem emprestar itens'); return

        self.pending_loan_member = user
        # ir para aba catálogo
        try:
            self.notebook.select(self.frame_items)
        except Exception:
            pass
        self.update_pending_loan_ui()

    def confirm_loan_for_pending(self):
        if not self.pending_loan_member:
            messagebox.showinfo('Info', 'Nenhum empréstimo pendente'); return
        sel = self.tree_items.selection()
        if not sel:
            messagebox.showinfo('Info', 'Selecione um item para emprestar'); return
        item = self.items_map[sel[0]]
        try:
            self.library.emprestar_item(item, self.pending_loan_member)
        except Exception as ex:
            messagebox.showerror('Erro', str(ex)); return
        messagebox.showinfo('OK', f'Empréstimo registrado para {self.pending_loan_member.nome}')
        self.set_status(f'Empréstimo registrado para {self.pending_loan_member.nome}', 4000)
        self.pending_loan_member = None
        self.refresh_all()

    def cancel_pending_loan(self):
        if not self.pending_loan_member:
            return
        self.pending_loan_member = None
        self.update_pending_loan_ui()

    def update_pending_loan_ui(self):
        if self.pending_loan_member:
            self.pending_loan_label.config(text=f'Emprestando para: {self.pending_loan_member.nome}')
            self.btn_confirm_loan.config(state='normal')
            self.btn_cancel_pending.config(state='normal')
        else:
            self.pending_loan_label.config(text='')
            self.btn_confirm_loan.config(state='disabled')
            self.btn_cancel_pending.config(state='disabled')

    def add_user_window(self):
        def save():
            nome = en_nome.get(); email = en_email.get(); senha = en_senha.get(); cpf = en_cpf.get(); tipo = tipo_cb.get()
            # campos obrigatórios
            if not nome or not email or not cpf:
                messagebox.showerror('Erro', 'Nome, Email e CPF são obrigatórios'); return
            # validações
            if not self.is_valid_name(nome):
                messagebox.showerror('Erro', 'Nome inválido. Não utilize números ou símbolos.')
                return
            if not self.is_valid_email(email):
                messagebox.showerror('Erro', 'Email inválido.')
                return
            if not self.is_valid_cpf(cpf):
                messagebox.showerror('Erro', 'CPF inválido. Deve conter 11 dígitos numéricos.')
                return
            self.library.adicionar_usuario(nome, email, senha, cpf, tipo)
            top.destroy(); self.refresh_users()
            self.set_status('Usuário adicionado', 3000)
            self.set_status('Usuário adicionado', 3000)

        top = tk.Toplevel(self)
        top.title('Adicionar Usuário')
        tk.Label(top, text='Nome').pack(); en_nome = ttk.Entry(top); en_nome.pack()
        tk.Label(top, text='Email').pack(); en_email = ttk.Entry(top); en_email.pack()
        tk.Label(top, text='Senha').pack(); en_senha = ttk.Entry(top, show='*'); en_senha.pack()
        tk.Label(top, text='CPF').pack(); en_cpf = ttk.Entry(top); en_cpf.pack()
        tk.Label(top, text='Tipo').pack(); tipo_cb = ttk.Combobox(top, values=['membro', 'bibliotecario', 'administrador']); tipo_cb.set('membro'); tipo_cb.pack()
        ttk.Button(top, text='Salvar', command=save).pack()

    def edit_user_window(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo('Info', 'Selecione um usuário para editar'); return
        obj = self.users_map[sel[0]]

        def save():
            nome = en_nome.get(); email = en_email.get(); cpf = en_cpf.get()
            # validações
            if not self.is_valid_name(nome):
                messagebox.showerror('Erro', 'Nome inválido. Não utilize números ou símbolos.')
                return
            if not self.is_valid_email(email):
                messagebox.showerror('Erro', 'Email inválido.')
                return
            if not self.is_valid_cpf(cpf):
                messagebox.showerror('Erro', 'CPF inválido. Deve conter 11 dígitos numéricos.')
                return
            obj.nome = nome; obj.email = email; obj.cpf = cpf
            top.destroy(); self.refresh_users()

        top = tk.Toplevel(self)
        top.title('Editar Usuário')
        tk.Label(top, text='Nome').pack(); en_nome = ttk.Entry(top); en_nome.insert(0, obj.nome); en_nome.pack()
        tk.Label(top, text='Email').pack(); en_email = ttk.Entry(top); en_email.insert(0, obj.email); en_email.pack()
        tk.Label(top, text='CPF').pack(); en_cpf = ttk.Entry(top); en_cpf.insert(0, obj.cpf); en_cpf.pack()
        ttk.Button(top, text='Salvar', command=save).pack()

    def remove_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo('Info', 'Selecione um usuário para remover'); return
        try:
            self.library.remover_usuario(self.users_map[sel[0]].id)
        except Exception as e:
            messagebox.showerror('Erro', str(e)); return
        self.refresh_users()
        self.set_status('Usuário removido', 3000)

    # ---------- empréstimos ----------
    def register_loan_window(self):
        def save():
            item = available_items[item_var.get()]
            membro = members[mem_var.get()]
            try:
                self.library.emprestar_item(item, membro)
            except Exception as e:
                messagebox.showerror('Erro', str(e)); return
            top.destroy(); self.refresh_all()

        # construir lista simples
        available_items = {f'{i.nome} ({i.id})': i for i in self.library.itens}
        members = {f'{u.nome} ({u.id})': u for u in self.library.usuarios if u.__class__.__name__ == 'Membro'}
        top = tk.Toplevel(self)
        top.title('Registrar Empréstimo')
        tk.Label(top, text='Item').pack(); item_var = tk.StringVar(); ttk.Combobox(top, values=list(available_items.keys()), textvariable=item_var).pack()
        tk.Label(top, text='Membro').pack(); mem_var = tk.StringVar(); ttk.Combobox(top, values=list(members.keys()), textvariable=mem_var).pack()
        ttk.Button(top, text='Confirmar', command=save).pack()

    def renew_loan(self):
        sel = self.tree_loans.selection();
        if not sel: messagebox.showinfo('Info', 'Selecione um empréstimo'); return
        e = self.loans_map[sel[0]]
        try:
            e.renovar(); self.refresh_loans(); messagebox.showinfo('OK', 'Empréstimo renovado')
        except Exception as ex:
            messagebox.showerror('Erro', str(ex))

    def return_loan(self):
        sel = self.tree_loans.selection()
        if not sel: messagebox.showinfo('Info', 'Selecione um empréstimo'); return
        e = self.loans_map[sel[0]]
        try:
            e.devolver(); self.refresh_loans(); self.refresh_reservations(); messagebox.showinfo('OK', 'Devolução processada')
        except Exception as ex:
            messagebox.showerror('Erro', str(ex))

    def pay_fine(self):
        sel = self.tree_loans.selection()
        if not sel: messagebox.showinfo('Info', 'Selecione um empréstimo'); return
        e = self.loans_map[sel[0]]
        try:
            e.quitar_divida(); self.refresh_loans(); messagebox.showinfo('OK', 'Multa quitada')
        except Exception as ex:
            messagebox.showerror('Erro', str(ex))
        else:
            self.set_status('Multa quitada', 3000)

    def impose_fine(self):
        sel = self.tree_loans.selection()
        if not sel:
            messagebox.showinfo('Info', 'Selecione um empréstimo para multar')
            return
        e = self.loans_map[sel[0]]

        # Confirmar se já existe multa
        if e.multa and not messagebox.askyesno('Confirmar', 'Empréstimo já possui multa. Deseja sobrescrever?'):
            return

        # Pergunta dias de atraso (calcula multa por dia)
        dias = simpledialog.askinteger('Dias de atraso', 'Informe o número de dias de atraso (aprox.)', minvalue=1)
        if dias is None:
            return

        valor = MULTA_POR_DIA * dias

        # Criar multa manualmente
        e._multa = Multa(valor, False)
        e._status = 'multado'
        messagebox.showinfo('OK', f'Multa aplicada: R$ {valor:.2f}')
        self.refresh_loans()
        self.set_status(f'Multa aplicada: R$ {valor:.2f}', 4000)

    # ---------- reservas ----------
    def reserve_item_window(self):
        def save():
            item = items_map[item_var.get()]
            membro = members[mem_var.get()]
            try:
                self.library.reservar_item(item, membro)
            except Exception as e:
                messagebox.showerror('Erro', str(e)); return
            top.destroy(); self.refresh_reservations()
            self.set_status('Reserva criada', 3000)

        items_map = {f'{i.nome} ({i.id})': i for i in self.library.itens}
        members = {f'{u.nome} ({u.id})': u for u in self.library.usuarios if u.__class__.__name__ == 'Membro'}
        top = tk.Toplevel(self)
        top.title('Reservar Item')
        tk.Label(top, text='Item').pack(); item_var = tk.StringVar(); ttk.Combobox(top, values=list(items_map.keys()), textvariable=item_var).pack()
        tk.Label(top, text='Membro').pack(); mem_var = tk.StringVar(); ttk.Combobox(top, values=list(members.keys()), textvariable=mem_var).pack()
        ttk.Button(top, text='Confirmar', command=save).pack()

    def cancel_reservation(self):
        sel = self.tree_res.selection()
        if not sel: messagebox.showinfo('Info', 'Selecione uma reserva'); return
        r = self.reservations_map[sel[0]]
        try:
            r.cancelar(); self.refresh_reservations(); messagebox.showinfo('OK', 'Reserva cancelada')
        except Exception as ex:
            messagebox.showerror('Erro', str(ex))
        else:
            self.set_status('Reserva cancelada', 3000)

    def finish_reservation(self):
        sel = self.tree_res.selection()
        if not sel: messagebox.showinfo('Info', 'Selecione uma reserva'); return
        r = self.reservations_map[sel[0]]
        try:
            # marcar como finalizada e criar empréstimo a partir da reserva
            r.marcar_como_finalizada()
            # Nota: biblioteca.Emprestimo.de_reserva permite criar empréstimo
            # cria o empréstimo a partir da reserva
            novo = Emprestimo.de_reserva(r)
            self.library.emprestimos.append(novo)
        except Exception as ex:
            # fallback simples: apenas finalizar
            messagebox.showerror('Erro', str(ex))
        finally:
            self.refresh_reservations(); self.refresh_loans()
            self.set_status('Reserva finalizada e empréstimo criado', 4000)


if __name__ == '__main__':
    app = App()
    app.mainloop()