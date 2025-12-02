import os
import sys
import json
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta


from modelos.biblioteca import Biblioteca
from modelos.livro import Livro
from modelos.ebook import Ebook
from utils.helpers import format_cpf, format_isbn

class SistemaBiblioteca(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Biblioteca - Python Tkinter")
        self.geometry("1400x800")
        self.configure(bg="#ecf0f1")

        # Inicializar biblioteca
        self.biblioteca = Biblioteca()
        self.usuario_logado = None

        # Configurações
        self.config = {
            'PRAZO_DEVOLUCAO': 0.000023148,
            'LIMITE_EMPRESTIMOS': 3,
            'LIMITE_RENOVACOES': 2,
            'MULTA_POR_DIA':1
        }

        # Cores
        self.cores = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'light': '#ecf0f1',
            'dark': '#34495e'
        }

        # Tela de login
        if os.path.exists("session.json"):
            try:
                with open("session.json", "r") as f:
                    data = json.load(f)
                    user_id = data.get("user_id")
                    
                    # Tentar encontrar usuário pelo ID
                    usuario = next((u for u in self.biblioteca.usuarios if str(u.id) == str(user_id)), None)
                    
                    if usuario:
                        self.usuario_logado = usuario
                        self.criar_interface_principal()
                    else:
                        self.criar_tela_login()
            except Exception:
                self.criar_tela_login()
        else:
            self.criar_tela_login()

    def _dig(self, obj, *keys):
        """Acessa valores aninhados de dicts ou atributos de objetos de forma segura.

        Ex: _dig(e, 'membro', 'id') retorna e['membro']['id'] ou e.membro.id se existir.
        """
        cur = obj
        for k in keys:
            if cur is None:
                return None
            if isinstance(cur, dict):
                cur = cur.get(k)
            else:
                val = getattr(cur, k, None)
                if val is None and not hasattr(cur, k):
                     # Tentar atributo protegido/privado se o público falhar
                     val = getattr(cur, f"_{k}", None)
                cur = val
        return cur

    def criar_tela_login(self):
        """Tela de login do sistema"""
        self.limpar_tela()

        # Frame principal centralizado
        login_frame = tk.Frame(self, bg=self.cores['light'])
        login_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Título
        tk.Label(
            login_frame,
            text="🏛️ Sistema de Biblioteca",
            font=("Arial", 28, "bold"),
            bg=self.cores['light'],
            fg=self.cores['primary']
        ).pack(pady=20)

        # Card de login
        card = tk.Frame(login_frame, bg='white', relief='raised', bd=2)
        card.pack(padx=40, pady=20)

        tk.Label(
            card,
            text="Fazer Login",
            font=("Arial", 18, "bold"),
            bg='white',
            fg=self.cores['dark']
        ).pack(pady=20, padx=60)

        # Email
        tk.Label(card, text="Email:", font=("Arial", 12), bg='white').pack(anchor='w', padx=30)
        self.login_email = tk.Entry(card, font=("Arial", 12), width=30)
        self.login_email.pack(pady=5, padx=30)

        # Senha
        tk.Label(card, text="Senha:", font=("Arial", 12), bg='white').pack(anchor='w', padx=30, pady=(10,0))
        self.login_senha = tk.Entry(card, font=("Arial", 12), width=30, show="*")
        self.login_senha.pack(pady=5, padx=30)

        # Botão login
        tk.Button(
            card,
            text="Entrar",
            font=("Arial", 12, "bold"),
            bg=self.cores['secondary'],
            fg='white',
            width=25,
            cursor='hand2',
            command=self.fazer_login
        ).pack(pady=20, padx=30)

        # Informações de teste
        info_frame = tk.Frame(card, bg='#f8f9fa')
        info_frame.pack(fill='x', pady=(0, 20), padx=30)

        tk.Label(
            info_frame,
            text="🔑 Credenciais de teste:",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa'
        ).pack(pady=5)

        tk.Label(
            info_frame,
            text="Admin: admin@biblioteca.com / admin123",
            font=("Arial", 9),
            bg='#f8f9fa'
        ).pack()

        tk.Label(
            info_frame,
            text="Bibliotecário: maria@biblioteca.com / biblio123",
            font=("Arial", 9),
            bg='#f8f9fa'
        ).pack()

        tk.Label(
            info_frame,
            text="Membro: joao@email.com / senha123",
            font=("Arial", 9),
            bg='#f8f9fa'
        ).pack()

        self.login_senha.bind('<Return>', lambda e: self.fazer_login())

    def fazer_login(self):
        """Autenticar usuário"""
        email = self.login_email.get()
        senha = self.login_senha.get()

        usuario = next((u for u in self.biblioteca.usuarios if u.email == email and u.senha == senha), None)

        if usuario:
            self.usuario_logado = usuario
            
            # Salvar sessão
            try:
                with open("session.json", "w") as f:
                    json.dump({"user_id": str(usuario.id)}, f)
            except Exception as e:
                print(f"Erro ao salvar sessão: {e}")
                
            self.criar_interface_principal()
        else:
            messagebox.showerror("Erro", "Email ou senha incorretos!")

    def criar_interface_principal(self):
        """Interface principal do sistema"""
        self.limpar_tela()

        # Header
        self.criar_header()

        # Container principal
        main_container = tk.Frame(self, bg='white')
        main_container.pack(fill='both', expand=True, padx=0, pady=0)

        # Sidebar
        self.criar_sidebar(main_container)

        # Área de conteúdo
        self.content_frame = tk.Frame(main_container, bg='#f8f9fa')
        self.content_frame.pack(side='left', fill='both', expand=True)

        # Mostrar dashboard
        self.mostrar_dashboard()

    def criar_header(self):
        """Criar cabeçalho do sistema"""
        header = tk.Frame(self, bg=self.cores['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        # Título
        tk.Label(
            header,
            text="📚 Sistema de Biblioteca",
            font=("Arial", 20, "bold"),
            bg=self.cores['primary'],
            fg='white'
        ).pack(side='left', padx=30, pady=20)

        # Informações do usuário
        user_frame = tk.Frame(header, bg=self.cores['primary'])
        user_frame.pack(side='right', padx=30)

        tk.Label(
            user_frame,
            text=self.usuario_logado.nome,
            font=("Arial", 12),
            bg=self.cores['primary'],
            fg='white'
        ).pack(side='left', padx=10)

        # Badge do tipo de usuário
        badge_colors = {
            'administrador': self.cores['danger'],
            'bibliotecario': self.cores['secondary'],
            'membro': self.cores['success']
        }

        tk.Label(
            user_frame,
            text=self.usuario_logado.tipo.upper(),
            font=("Arial", 9, "bold"),
            bg=badge_colors.get(self.usuario_logado.tipo, self.cores['dark']),
            fg='white',
            padx=12,
            pady=4
        ).pack(side='left', padx=5)

        # Botão sair
        tk.Button(
            user_frame,
            text="Sair",
            font=("Arial", 10),
            bg=self.cores['danger'],
            fg='white',
            cursor='hand2',
            command=self.logout
        ).pack(side='left', padx=10)

    def criar_sidebar(self, parent):
        """Criar menu lateral"""
        sidebar = tk.Frame(parent, bg=self.cores['light'], width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        tipo = self.usuario_logado.tipo

        # Definir menu por tipo de usuário
        if tipo == 'administrador':
            menus = [
                ('📊', 'Dashboard', self.mostrar_dashboard),
                ('👥', 'Usuários', self.mostrar_usuarios),
                ('📚', 'Acervo', self.mostrar_itens),
                ('📖', 'Empréstimos', self.mostrar_emprestimos),
                ('📌', 'Reservas', self.mostrar_reservas),
                ('💰', 'Multas', self.mostrar_multas)
            ]
        elif tipo == 'bibliotecario':
            menus = [
                ('📊', 'Dashboard', self.mostrar_dashboard),
                ('📚', 'Acervo', self.mostrar_itens),
                ('📖', 'Empréstimos', self.mostrar_emprestimos),
                ('📌', 'Reservas', self.mostrar_reservas),
                ('💰', 'Multas', self.mostrar_multas)
            ]
        else:  # membro
            menus = [
                ('📊', 'Dashboard', self.mostrar_dashboard),
                ('📚', 'Catálogo', self.mostrar_itens),
                ('📖', 'Meus Empréstimos', self.mostrar_meus_emprestimos),
                ('📌', 'Minhas Reservas', self.mostrar_reservas)
            ]

        for icon, text, command in menus:
            self.criar_menu_item(sidebar, icon, text, command)

    def criar_menu_item(self, parent, icon, text, command):
        """Criar item de menu"""
        btn = tk.Button(
            parent,
            text=f"{icon}  {text}",
            font=("Arial", 12),
            bg=self.cores['light'],
            fg=self.cores['dark'],
            relief='flat',
            anchor='w',
            padx=20,
            pady=15,
            cursor='hand2',
            command=command
        )
        btn.pack(fill='x')

        btn.bind('<Enter>', lambda e: btn.config(bg=self.cores['secondary'], fg='white'))
        btn.bind('<Leave>', lambda e: btn.config(bg=self.cores['light'], fg=self.cores['dark']))

    def mostrar_dashboard(self):
        """Mostrar dashboard com estatísticas"""
        self.limpar_content()

        # Título
        tk.Label(
            self.content_frame,
            text="Dashboard",
            font=("Arial", 24, "bold"),
            bg='#f8f9fa',
            fg=self.cores['primary']
        ).pack(pady=20, padx=30, anchor='w')

        # Cards de estatísticas
        stats_frame = tk.Frame(self.content_frame, bg='#f8f9fa')
        stats_frame.pack(fill='x', padx=30, pady=10)

        tipo = self.usuario_logado.tipo

        if tipo in ['administrador', 'bibliotecario']:
            stats = [
                ('Total de Usuários', len(self.biblioteca.usuarios), self.cores['primary']),
                ('Itens no Acervo', len(self.biblioteca.itens), self.cores['secondary']),
                ('Empréstimos Ativos', len([e for e in self.biblioteca.emprestimos if self._dig(e, 'status') == 'ativo']), self.cores['success']),
                ('Reservas Ativas', len([r for r in self.biblioteca.reservas if self._dig(r, 'status') == 'aguardando']), self.cores['warning'])
            ]
        else:
            stats = [
                ('Meus Empréstimos', len([e for e in self.biblioteca.emprestimos if self._dig(e, 'membro', 'id') == self.usuario_logado.id and self._dig(e, 'status') == 'ativo']), self.cores['primary']),
                ('Minhas Reservas', len([r for r in self.biblioteca.reservas if self._dig(r, 'membro', 'id') == self.usuario_logado.id]), self.cores['secondary']),
                ('Itens Disponíveis', len([i for i in self.biblioteca.itens if self._dig(i, 'status') == 'disponivel']), self.cores['success'])
            ]

        for i, (label, value, color) in enumerate(stats):
            self.criar_stat_card(stats_frame, label, value, color, i)

    def criar_stat_card(self, parent, label, value, color, position):
        """Criar card de estatística"""
        card = tk.Frame(parent, bg='white', relief='raised', bd=1)
        card.grid(row=0, column=position, padx=10, pady=10, sticky='ew')
        parent.columnconfigure(position, weight=1)

        # Barra colorida
        tk.Frame(card, bg=color, height=4).pack(fill='x')

        # Valor
        tk.Label(
            card,
            text=str(value),
            font=("Arial", 32, "bold"),
            bg='white',
            fg=self.cores['primary']
        ).pack(pady=(20, 5))

        # Label
        tk.Label(
            card,
            text=label,
            font=("Arial", 11),
            bg='white',
            fg='#7f8c8d'
        ).pack(pady=(0, 20))

    def mostrar_usuarios(self):
        """Gerenciar usuários"""
        self.limpar_content()

        tk.Label(
            self.content_frame,
            text="Gerenciar Usuários",
            font=("Arial", 24, "bold"),
            bg='#f8f9fa',
            fg=self.cores['primary']
        ).pack(pady=20, padx=30, anchor='w')

        # Card de cadastro
        card_cadastro = self.criar_card(self.content_frame, "Cadastrar Novo Usuário")

        # Formulário
        form_frame = tk.Frame(card_cadastro, bg='white')
        form_frame.pack(fill='x', padx=20, pady=10)

        # Nome
        tk.Label(form_frame, text="Nome Completo:", font=("Arial", 10), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        nome_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
        nome_entry.grid(row=0, column=1, padx=10, pady=5)

        # Email
        tk.Label(form_frame, text="Email:", font=("Arial", 10), bg='white').grid(row=0, column=2, sticky='w', pady=5)
        email_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
        email_entry.grid(row=0, column=3, padx=10, pady=5)

        # CPF
        tk.Label(form_frame, text="CPF:", font=("Arial", 10), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        cpf_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
        cpf_entry.grid(row=1, column=1, padx=10, pady=5)

        # Tipo
        tk.Label(form_frame, text="Tipo:", font=("Arial", 10), bg='white').grid(row=1, column=2, sticky='w', pady=5)
        tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(form_frame, textvariable=tipo_var, values=['membro', 'bibliotecario', 'administrador'], state='readonly', width=27)
        tipo_combo.grid(row=1, column=3, padx=10, pady=5)

        # Senha
        tk.Label(form_frame, text="Senha:", font=("Arial", 10), bg='white').grid(row=2, column=0, sticky='w', pady=5)
        senha_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, show='*')
        senha_entry.grid(row=2, column=1, padx=10, pady=5)

        # Botão cadastrar
        def cadastrar():
            if all([nome_entry.get(), email_entry.get(), cpf_entry.get(), tipo_var.get(), senha_entry.get()]):
                try:
                    # use o método do modelo para criar o usuário correto (membro/bibliotecario/administrador)
                    self.biblioteca.adicionar_usuario(
                        nome_entry.get(),
                        email_entry.get(),
                        senha_entry.get(),
                        cpf_entry.get().strip(),
                        tipo_var.get()
                    )
                    messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                    self.mostrar_usuarios()
                except Exception as e:
                    messagebox.showerror("Erro", str(e))
            else:
                messagebox.showerror("Erro", "Preencha todos os campos!")

        tk.Button(
            form_frame,
            text="➕ Cadastrar Usuário",
            font=("Arial", 11, "bold"),
            bg=self.cores['success'],
            fg='white',
            cursor='hand2',
            command=cadastrar
        ).grid(row=3, column=0, columnspan=4, pady=15)

        # Card de lista
        card_lista = self.criar_card(self.content_frame, "Lista de Usuários")

        # Tabela
        self.criar_tabela_usuarios(card_lista)

    def criar_tabela_usuarios(self, parent):
        """Criar tabela de usuários"""
        # Frame para tabela
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')

        # Treeview
        tree = ttk.Treeview(
            table_frame,
            columns=('Nome', 'Email', 'CPF', 'Tipo'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=10
        )

        tree.heading('Nome', text='Nome')
        tree.heading('Email', text='Email')
        tree.heading('CPF', text='CPF')
        tree.heading('Tipo', text='Tipo')

        tree.column('Nome', width=200)
        tree.column('Email', width=200)
        tree.column('CPF', width=150)
        tree.column('Tipo', width=150)

        # Preencher dados
        for usuario in self.biblioteca.usuarios:
            tree.insert('', 'end', iid=str(usuario.id), values=(
                usuario.nome,
                usuario.email,
                format_cpf(usuario.cpf),
                usuario.tipo.upper()
            ))

        tree.pack(fill='both', expand=True)
        scrollbar.config(command=tree.yview)

        def remover_usuario_selecionado():
            sel = tree.selection()
            if not sel:
                messagebox.showerror('Erro', 'Selecione um usuário para remover')
                return
            
            user_id = sel[0]
            
            # Evitar remover a si mesmo
            if str(user_id) == str(self.usuario_logado.id):
                 messagebox.showerror('Erro', 'Você não pode remover a si mesmo!')
                 return

            if messagebox.askyesno('Confirmar', 'Deseja realmente remover este usuário?'):
                try:
                    self.biblioteca.remover_usuario(user_id)
                    messagebox.showinfo('Sucesso', 'Usuário removido com sucesso')
                    self.mostrar_usuarios()
                except Exception as e:
                    messagebox.showerror('Erro', str(e))

        tk.Button(
            table_frame, 
            text="🗑️ Remover Usuário Selecionado", 
            bg=self.cores['danger'], 
            fg='white',
            command=remover_usuario_selecionado
        ).pack(pady=10)

    def mostrar_itens(self):
        """Gerenciar acervo"""
        self.limpar_content()

        titulo = "Gerenciar Acervo" if self.usuario_logado.tipo != 'membro' else "Catálogo de Itens"

        tk.Label(
            self.content_frame,
            text=titulo,
            font=("Arial", 24, "bold"),
            bg='#f8f9fa',
            fg=self.cores['primary']
        ).pack(pady=20, padx=30, anchor='w')

        # Card de cadastro (só para admin e bibliotecário)
        if self.usuario_logado.tipo in ['administrador', 'bibliotecario']:
            card_cadastro = self.criar_card(self.content_frame, "Cadastrar Novo Item")

            form_frame = tk.Frame(card_cadastro, bg='white')
            form_frame.pack(fill='x', padx=20, pady=10)

            # Tipo
            tk.Label(form_frame, text="Tipo:", font=("Arial", 10), bg='white').grid(row=0, column=0, sticky='w', pady=5)
            tipo_var = tk.StringVar()
            tipo_combo = ttk.Combobox(form_frame, textvariable=tipo_var, values=['livro', 'ebook'], state='readonly', width=27)
            tipo_combo.grid(row=0, column=1, padx=10, pady=5)

            # Título
            tk.Label(form_frame, text="Título:", font=("Arial", 10), bg='white').grid(row=0, column=2, sticky='w', pady=5)
            titulo_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
            titulo_entry.grid(row=0, column=3, padx=10, pady=5)

            # Autor
            tk.Label(form_frame, text="Autor:", font=("Arial", 10), bg='white').grid(row=1, column=0, sticky='w', pady=5)
            autor_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
            autor_entry.grid(row=1, column=1, padx=10, pady=5)

            # ISBN
            tk.Label(form_frame, text="ISBN:", font=("Arial", 10), bg='white').grid(row=1, column=2, sticky='w', pady=5)
            isbn_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
            isbn_entry.grid(row=1, column=3, padx=10, pady=5)

            # Categoria
            tk.Label(form_frame, text="Categoria:", font=("Arial", 10), bg='white').grid(row=2, column=0, sticky='w', pady=5)
            categoria_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
            categoria_entry.grid(row=2, column=1, padx=10, pady=5)

            # Páginas
            tk.Label(form_frame, text="Páginas:", font=("Arial", 10), bg='white').grid(row=2, column=2, sticky='w', pady=5)
            paginas_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
            paginas_entry.grid(row=2, column=3, padx=10, pady=5)

            def cadastrar_item():
                if all([tipo_var.get(), titulo_entry.get(), autor_entry.get(), isbn_entry.get(), paginas_entry.get()]):
                    try:
                        # Converter páginas para inteiro
                        num_paginas = int(paginas_entry.get())
                        
                        if tipo_var.get() == 'livro':
                            # Livro(nome, imagem_url, imagem_arquivo, autor, num_paginas, isbn, categoria)
                            # Passando None para imagens pois foram removidas
                            novo_item = Livro(
                                titulo_entry.get(), 
                                None, 
                                None, 
                                autor_entry.get(), 
                                num_paginas, 
                                isbn_entry.get(), 
                                categoria_entry.get() or 'Sem categoria'
                            )
                        else:
                            # Ebook(nome, imagem_url, imagem_arquivo, autor, num_paginas, isbn, categoria, arquivo, url)
                            novo_item = Ebook(
                                titulo_entry.get(), 
                                None, 
                                None, 
                                autor_entry.get(), 
                                num_paginas, 
                                isbn_entry.get(), 
                                categoria_entry.get() or 'Sem categoria',
                                None, # arquivo
                                None  # url
                            )
                        
                        self.biblioteca.adicionar_item(novo_item)
                        messagebox.showinfo("Sucesso", "Item cadastrado com sucesso!")
                        self.mostrar_itens()
                    except ValueError as e:
                        messagebox.showerror("Erro", str(e))
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao cadastrar item: {str(e)}")
                else:
                    messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")

            tk.Button(
                form_frame,
                text="➕ Cadastrar Item",
                font=("Arial", 11, "bold"),
                bg=self.cores['success'],
                fg='white',
                cursor='hand2',
                command=cadastrar_item
            ).grid(row=3, column=0, columnspan=4, pady=15)

        # Card de lista
        card_lista = self.criar_card(self.content_frame, "Acervo da Biblioteca")

        # Grid de itens
        self.criar_grid_itens(card_lista)

    def criar_grid_itens(self, parent):
        """Criar grid de itens"""
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Frame interno que conterá os itens
        scrollable_frame = tk.Frame(canvas, bg='white')

        # Configurar colunas para expandir (3 colunas)
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        scrollable_frame.grid_columnconfigure(2, weight=1)

        # Window no canvas
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            # Atualiza a largura do frame para igualar a do canvas
            canvas.itemconfig(window_id, width=event.width)

        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Criar cards de itens
        for i, item in enumerate(self.biblioteca.itens):
            row = i // 3
            col = i % 3

            item_card = tk.Frame(scrollable_frame, bg='white', relief='raised', bd=1)
            item_card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

            # Título
            tk.Label(
                item_card,
                text=self._dig(item, 'nome') or str(self._dig(item, 'titulo') or ''),
                font=("Arial", 12, "bold"),
                bg='white',
                fg=self.cores['primary'],
                wraplength=200
            ).pack(pady=10, padx=10)

            # Detalhes
            detalhes = [
                f"Autor: {self._dig(item, 'autor')}",
                f"Categoria: {self._dig(item, 'categoria')}",
                f"Páginas: {self._dig(item, 'num_paginas')}",
                f"ISBN: {format_isbn(self._dig(item, 'isbn'))}",
                f"Tipo: {'📕 Livro' if self._dig(item, 'tipo') == 'livro' else '💻 E-book'}"
            ]

            for detalhe in detalhes:
                tk.Label(
                    item_card,
                    text=detalhe,
                    font=("Arial", 9),
                    bg='white',
                    fg='#7f8c8d'
                ).pack(anchor='w', padx=10, pady=2)

            # Status
            status_colors = {
                'disponivel': '#d4edda',
                'emprestado': '#fff3cd',
                'reservado': '#cce5ff'
            }

            status_val = self._dig(item, 'status') or 'desconhecido'
            tk.Label(
                item_card,
                text=str(status_val).upper(),
                font=("Arial", 9, "bold"),
                bg=status_colors.get(status_val, '#f8f9fa'),
                fg='#000',
                padx=10,
                pady=3
            ).pack(pady=10)

            # Botão de remover (apenas admin/bibliotecario)
            if self.usuario_logado.tipo in ['administrador', 'bibliotecario']:
                def remover_item_click(id_item=self._dig(item, 'id')):
                    if messagebox.askyesno('Confirmar', 'Deseja realmente remover este item?'):
                        try:
                            self.biblioteca.remover_item(id_item)
                            messagebox.showinfo('Sucesso', 'Item removido com sucesso')
                            self.mostrar_itens()
                        except Exception as e:
                            messagebox.showerror('Erro', str(e))

                tk.Button(
                    item_card,
                    text="🗑️ Remover",
                    font=("Arial", 9),
                    bg=self.cores['danger'],
                    fg='white',
                    cursor='hand2',
                    command=remover_item_click
                ).pack(pady=5)

        # Configurar grid
        for i in range(3):
            scrollable_frame.columnconfigure(i, weight=1)

        canvas.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y')

    def mostrar_emprestimos(self):
        """Gerenciar empréstimos"""
        self.limpar_content()

        tk.Label(
            self.content_frame,
            text="Gerenciar Empréstimos",
            font=("Arial", 24, "bold"),
            bg='#f8f9fa',
            fg=self.cores['primary']
        ).pack(pady=20, padx=30, anchor='w')

        # Card de novo empréstimo
        card_novo = self.criar_card(self.content_frame, "Novo Empréstimo")

        form_frame = tk.Frame(card_novo, bg='white')
        form_frame.pack(fill='x', padx=20, pady=10)

        # Selecionar membro
        tk.Label(form_frame, text="Membro:", font=("Arial", 10), bg='white').grid(row=0, column=0, sticky='w', pady=10)
        membro_var = tk.StringVar()
        membros = [u for u in self.biblioteca.usuarios if u.tipo == 'membro']
        membro_combo = ttk.Combobox(
            form_frame,
            textvariable=membro_var,
            values=[f"{m.nome} ({m.email})" for m in membros],
            state='readonly',
            width=40
        )
        membro_combo.grid(row=0, column=1, padx=10, pady=10)

        # Selecionar item
        tk.Label(form_frame, text="Item:", font=("Arial", 10), bg='white').grid(row=0, column=2, sticky='w', pady=10)
        item_var = tk.StringVar()
        itens_disponiveis = [i for i in self.biblioteca.itens if self._dig(i, 'status') == 'disponivel' and self._dig(i, 'tipo') == 'livro']
        item_combo = ttk.Combobox(
            form_frame,
            textvariable=item_var,
            values=[f"{self._dig(i, 'nome')} - {self._dig(i, 'autor')}" for i in itens_disponiveis],
            state='readonly',
            width=40
        )
        item_combo.grid(row=0, column=3, padx=10, pady=10)

        def realizar_emprestimo():
            if membro_var.get() and item_var.get():
                membro_idx = membro_combo.current()
                item_idx = item_combo.current()

                if membro_idx >= 0 and item_idx >= 0:
                    membro = membros[membro_idx]
                    item = itens_disponiveis[item_idx]
                    try:
                        # usar método do modelo para criar um Emprestimo (objeto)
                        self.biblioteca.emprestar_item(item, membro)
                        # garantir que o item (dicionário) registre status
                        if isinstance(item, dict):
                            item['status'] = 'emprestado'
                        messagebox.showinfo("Sucesso", "Empréstimo realizado com sucesso!")
                        self.mostrar_emprestimos()
                    except Exception as e:
                        messagebox.showerror('Erro', str(e))
            else:
                messagebox.showerror("Erro", "Selecione membro e item!")

        tk.Button(
            form_frame,
            text="📖 Realizar Empréstimo",
            font=("Arial", 11, "bold"),
            bg=self.cores['primary'],
            fg='white',
            cursor='hand2',
            command=realizar_emprestimo
        ).grid(row=1, column=0, columnspan=4, pady=15)

        # Card de lista
        card_lista = self.criar_card(self.content_frame, "Empréstimos Ativos")
        self.criar_tabela_emprestimos(card_lista)

    def criar_tabela_emprestimos(self, parent):
        """Criar tabela de empréstimos"""
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')

        tree = ttk.Treeview(
            table_frame,
            columns=('Membro', 'Item', 'Data Empréstimo', 'Data Prevista', 'Status', 'Renovações'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=10
        )

        for col in ['Membro', 'Item', 'Data Empréstimo', 'Data Prevista', 'Status', 'Renovações']:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        # obter empréstimos ativos (suportar objetos Emprestimo ou dicts antigos)
        emprestimos_ativos = []
        for e in self.biblioteca.emprestimos:
            status_val = None
            if isinstance(e, dict):
                status_val = e.get('status')
            else:
                status_val = getattr(e, 'status', None)
            if status_val == 'ativo':
                emprestimos_ativos.append(e)

        # Inserir empréstimos com iid = índice para facilitar mapeamento
        for idx, emp in enumerate(emprestimos_ativos):
            if isinstance(emp, dict):
                membro_nome = emp.get('membro', {}).get('nome', '')
                item_nome = emp.get('item', {}).get('nome', '')
                data_emp = emp.get('dataEmprestimo')
                data_prev = emp.get('dataPrevista')
                renov = emp.get('renovacoes', 0)
                status_text = str(emp.get('status', '')).upper()
                # formatos de data
                data_emp_str = data_emp.strftime('%d/%m/%Y') if hasattr(data_emp, 'strftime') else str(data_emp)
                data_prev_str = data_prev.strftime('%d/%m/%Y') if hasattr(data_prev, 'strftime') else str(data_prev)
            else:
                membro_nome = getattr(emp.membro, 'nome', '') if getattr(emp, 'membro', None) is not None else ''
                # item pode ser dict ou objeto
                item_val = getattr(emp, 'item', None)
                item_nome = item_val.get('nome') if isinstance(item_val, dict) else getattr(item_val, 'nome', '')
                data_emp_str = getattr(emp, 'data_emprestimo', getattr(emp, 'dataEmprestimo', None))
                if hasattr(data_emp_str, 'strftime'):
                    data_emp_str = data_emp_str.strftime('%d/%m/%Y')
                else:
                    data_emp_str = str(data_emp_str)
                # data prevista
                try:
                    data_prev = getattr(emp, 'data_prevista_devolucao', getattr(emp, 'dataPrevista', None))
                    data_prev_str = data_prev.strftime('%d/%m/%Y') if hasattr(data_prev, 'strftime') else str(data_prev)
                except Exception:
                    data_prev_str = ''
                renov = getattr(emp, '_quantidade_renovacoes', getattr(emp, 'renovacoes', 0))
                status_text = str(getattr(emp, 'status', '')).upper()

            tree.insert('', 'end', iid=str(idx), values=(
                membro_nome,
                item_nome,
                data_emp_str,
                data_prev_str,
                status_text,
                f"{renov}/{self.config['LIMITE_RENOVACOES']}"
            ))

        tree.pack(fill='both', expand=True)
        scrollbar.config(command=tree.yview)

        # Botão para processar devolução do empréstimo selecionado
        def processar_devolucao():
            sel = tree.selection()
            if not sel:
                messagebox.showerror('Erro', 'Selecione um empréstimo para processar a devolução.')
                return

            iid = sel[0]
            try:
                idx = int(iid)
            except ValueError:
                messagebox.showerror('Erro', 'Seleção inválida.')
                return

            # Map index no array de empréstimos ativos para o empréstimo real
            emp = emprestimos_ativos[idx]

            # Se for um objeto Emprestimo, usar API do modelo
            if not isinstance(emp, dict):
                try:
                    emprestimo = self.biblioteca.registrar_devolucao(emp.id)
                except Exception as e:
                    messagebox.showerror('Erro', str(e))
                    return

                # Se multado, perguntar sobre quitação
                if getattr(emprestimo, 'status', '') == 'multado' and getattr(emprestimo, 'multa', None) is not None:
                    valor = getattr(emprestimo.multa, 'valor', None)
                    resp = messagebox.askyesno('Multa gerada', f'Valor da multa: {valor:.2f}. Deseja quitar agora?')
                    if resp:
                        try:
                            self.biblioteca.registrar_pagamento_multa(emprestimo.id)
                            messagebox.showinfo('Pago', 'Multa quitada e empréstimo finalizado.')
                        except Exception as e:
                            messagebox.showerror('Erro', str(e))
                else:
                    messagebox.showinfo('Devolução', 'Empréstimo processado com sucesso.')

            else:
                # fallback para dict-based emprestimos
                try:
                    data_prevista = emp['dataPrevista'] if hasattr(emp.get('dataPrevista'), 'strftime') else datetime.strptime(emp['dataPrevista'], '%d/%m/%Y')
                except Exception:
                    data_prevista = emp.get('dataPrevista')
                agora = datetime.now()
                atraso = (agora.date() - data_prevista.date()).days if hasattr(data_prevista, 'date') else 0

                if atraso > 0:
                    valor_multa = atraso * self.config['MULTA_POR_DIA']
                    emp['status'] = 'multado'
                    emp['multa'] = {'valor': valor_multa, 'paga': False}
                    emp['dataDevolucao'] = agora
                    if isinstance(emp.get('item'), dict):
                        emp['item']['status'] = 'disponivel'
                    resp = messagebox.askyesno('Multa gerada', f'Em atraso por {atraso} dias. Multa = {valor_multa:.2f}. Deseja quitar agora?')
                    if resp:
                        emp['multa']['paga'] = True
                        emp['status'] = 'finalizado'
                        messagebox.showinfo('Pago', 'Multa quitada e empréstimo finalizado.')
                    else:
                        messagebox.showinfo('Registrado', f'Multa registrada: {valor_multa:.2f}')
                else:
                    emp['status'] = 'finalizado'
                    emp['dataDevolucao'] = agora
                    if isinstance(emp.get('item'), dict):
                        emp['item']['status'] = 'disponivel'
                    messagebox.showinfo('Devolução', 'Empréstimo devolvido sem multa.')

            # Atualizar visual da tabela (simplesmente recarregar a tela)
            self.mostrar_emprestimos()

        tk.Button(parent, text='📥 Processar Devolução', font=('Arial', 11), bg=self.cores['secondary'], fg='white', cursor='hand2', command=processar_devolucao).pack(pady=8)

    def mostrar_reservas(self):
        """Gerenciar reservas: listar, criar e cancelar reservas"""
        self.limpar_content()

        titulo = "Gerenciar Reservas" if self.usuario_logado.tipo != 'membro' else "Minhas Reservas"

        tk.Label(
            self.content_frame,
            text=titulo,
            font=("Arial", 24, "bold"),
            bg='#f8f9fa',
            fg=self.cores['primary']
        ).pack(pady=20, padx=30, anchor='w')

        # Card superior: criar reserva
        card_cadastro = self.criar_card(self.content_frame, "Reservar Item")

        form_frame = tk.Frame(card_cadastro, bg='white')
        form_frame.pack(fill='x', padx=20, pady=10)

        # Membro (se admin/bibliotecario pode escolher, se membro usa o próprio)
        tk.Label(form_frame, text="Membro:", font=("Arial", 10), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        membro_var = tk.StringVar()
        if self.usuario_logado.tipo in ['administrador', 'bibliotecario']:
            membros = [u for u in self.biblioteca.usuarios if getattr(u, 'tipo', None) == 'membro']
            membro_combo = ttk.Combobox(form_frame, textvariable=membro_var, values=[f"{m.nome} ({m.email})" for m in membros], state='readonly', width=50)
            membro_combo.grid(row=0, column=1, padx=10, pady=5)
        else:
            membro_combo = tk.Label(form_frame, text=self.usuario_logado.nome, bg='white')
            membro_combo.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        # Item (mostrar apenas itens que não estão disponíveis -> emprestados)
        tk.Label(form_frame, text="Item:", font=("Arial", 10), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        item_var = tk.StringVar()
        itens_para_reserva = [i for i in self.biblioteca.itens if self._dig(i, 'status') != 'disponivel']
        item_combo = ttk.Combobox(form_frame, textvariable=item_var, values=[f"{self._dig(i, 'nome')} - {self._dig(i, 'autor')} (ID:{self._dig(i, 'id')})" for i in itens_para_reserva], state='readonly', width=50)
        item_combo.grid(row=1, column=1, padx=10, pady=5)

        def criar_reserva():
            # determinar membro
            if self.usuario_logado.tipo in ['administrador', 'bibliotecario']:
                sel = membro_combo.current()
                if sel < 0:
                    messagebox.showerror('Erro', 'Selecione um membro')
                    return
                membro = membros[sel]
            else:
                membro = self.usuario_logado

            item_idx = item_combo.current()
            if item_idx < 0:
                messagebox.showerror('Erro', 'Selecione um item para reservar')
                return

            item = itens_para_reserva[item_idx]

            try:
                # usar método do modelo
                self.biblioteca.reservar_item(item, membro)
                messagebox.showinfo('Sucesso', 'Reserva criada com sucesso')
                self.mostrar_reservas()
            except Exception as e:
                messagebox.showerror('Erro', str(e))

        tk.Button(form_frame, text="➕ Criar Reserva", font=("Arial", 11, "bold"), bg=self.cores['success'], fg='white', cursor='hand2', command=criar_reserva).grid(row=2, column=0, columnspan=2, pady=12)

        # Card lista: mostrar reservas
        card_lista = self.criar_card(self.content_frame, "Lista de Reservas")

        table_frame = tk.Frame(card_lista, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        cols = ('Membro', 'Item', 'Data Reserva', 'Status')
        tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=10)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=200)

        # Filtrar reservas: se membro, mostrar apenas as do próprio membro
        reservas = self.biblioteca.reservas
        # Mostrar reservas com status 'aguardando' ou 'finalizada' (manter histórico)
        reservas = [r for r in reservas if (getattr(r, 'status', None) or r.get('status')) in ('aguardando', 'finalizada')]

        if self.usuario_logado.tipo == 'membro':
            reservas = [r for r in reservas if getattr(r.membro, 'id', None) == self.usuario_logado.id]

        for idx, r in enumerate(reservas):
            # suportar objetos Reserva ou dicts (robusto para dados mistos)
            if isinstance(r, dict):
                item_nome = r.get('item', {}).get('nome', str(r.get('item')))
                membro_nome = r.get('membro', {}).get('nome', str(r.get('membro')))
                data_val = r.get('data_reserva') or r.get('dataReserva') or r.get('data')
                data_str = data_val.strftime('%d/%m/%Y %H:%M') if hasattr(data_val, 'strftime') else str(data_val)
                status_val = r.get('status', '')
            else:
                item_nome = r.item['nome'] if isinstance(r.item, dict) else getattr(r.item, 'nome', str(r.item))
                membro_nome = getattr(r.membro, 'nome', str(r.membro))
                data_str = r.data_reserva.strftime('%d/%m/%Y %H:%M') if hasattr(r, 'data_reserva') else str(r.data_reserva)
                status_val = getattr(r, 'status', '')

            tree.insert('', 'end', iid=str(idx), values=(membro_nome, item_nome, data_str, str(status_val).upper()))

        tree.pack(fill='both', expand=True)

        # Ação cancelar reserva
        def cancelar_reserva():
            sel = tree.selection()
            if not sel:
                messagebox.showerror('Erro', 'Selecione uma reserva para cancelar')
                return
            idx = int(sel[0])
            reserva = reservas[idx]
            # obter status de forma segura
            status_val = getattr(reserva, 'status', None) if not isinstance(reserva, dict) else reserva.get('status')
            if status_val != 'aguardando':
                messagebox.showinfo('Info', 'Reserva não está em estado aguardando')
                return
            # cancelar dependendo do tipo
            # cancelar dependendo do tipo
            try:
                if isinstance(reserva, dict):
                    # Se for dict, não temos como chamar o método da biblioteca facilmente sem ID
                    # Mas o código original assumia que 'reserva' vinha de self.biblioteca.reservas
                    # Vamos tentar achar o ID
                    res_id = reserva.get('id')
                    self.biblioteca.cancelar_reserva(res_id)
                else:
                    self.biblioteca.cancelar_reserva(reserva.id)
            except Exception as e:
                messagebox.showerror('Erro', str(e))
                return
            messagebox.showinfo('Cancelada', 'Reserva cancelada com sucesso')
            self.mostrar_reservas()

        tk.Button(card_lista, text='✖ Cancelar Reserva', font=('Arial', 11), bg=self.cores['danger'], fg='white', cursor='hand2', command=cancelar_reserva).pack(pady=8)

    def mostrar_meus_emprestimos(self):
        """Mostrar empréstimos do membro logado"""
        self.limpar_content()

        tk.Label(
            self.content_frame,
            text="Meus Empréstimos",
            font=("Arial", 24, "bold"),
            bg='#f8f9fa',
            fg=self.cores['primary']
        ).pack(pady=20, padx=30, anchor='w')

        card_lista = self.criar_card(self.content_frame, "Empréstimos Ativos")

        table_frame = tk.Frame(card_lista, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tree = ttk.Treeview(
            table_frame,
            columns=('Item', 'Data Empréstimo', 'Data Prevista', 'Status', 'Renovações'),
            show='headings',
            height=10
        )

        for col in ['Item', 'Data Empréstimo', 'Data Prevista', 'Status', 'Renovações']:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        meus_emprestimos = [e for e in self.biblioteca.emprestimos if self._dig(e, 'membro', 'id') == self.usuario_logado.id and self._dig(e, 'status') == 'ativo']

        for emp in meus_emprestimos:
            if isinstance(emp, dict):
                item_nome = emp.get('item', {}).get('nome', '')
                data_emp = emp.get('dataEmprestimo')
                data_prev = emp.get('dataPrevista')
                status_text = str(emp.get('status', '')).upper()
                renov = emp.get('renovacoes', 0)
                data_emp_str = data_emp.strftime('%d/%m/%Y') if hasattr(data_emp, 'strftime') else str(data_emp)
                data_prev_str = data_prev.strftime('%d/%m/%Y') if hasattr(data_prev, 'strftime') else str(data_prev)
            else:
                item_val = getattr(emp, 'item', None)
                item_nome = item_val.get('nome') if isinstance(item_val, dict) else getattr(item_val, 'nome', '')
                data_emp = getattr(emp, 'data_emprestimo', getattr(emp, 'dataEmprestimo', None))
                data_prev = getattr(emp, 'data_prevista_devolucao', getattr(emp, 'dataPrevista', None))
                data_emp_str = data_emp.strftime('%d/%m/%Y') if hasattr(data_emp, 'strftime') else str(data_emp)
                data_prev_str = data_prev.strftime('%d/%m/%Y') if hasattr(data_prev, 'strftime') else str(data_prev)
                status_text = str(getattr(emp, 'status', '')).upper()
                renov = getattr(emp, '_quantidade_renovacoes', getattr(emp, 'renovacoes', 0))

            tree.insert('', 'end', values=(
                item_nome,
                data_emp_str,
                data_prev_str,
                status_text,
                f"{renov}/{self.config['LIMITE_RENOVACOES']}"
            ))

        tree.pack(fill='both', expand=True)

    def mostrar_multas(self):
        """Gerenciar multas"""
        self.limpar_content()

        tk.Label(
            self.content_frame,
            text="Multas",
            font=("Arial", 24, "bold"),
            bg='#f8f9fa',
            fg=self.cores['primary']
        ).pack(pady=20, padx=30, anchor='w')
        card_lista = self.criar_card(self.content_frame, "Multas Pendentes")

        # Filtrar empréstimos com multas (status 'multado')
        emprestimos_multados = []
        for e in self.biblioteca.emprestimos:
            status_val = self._dig(e, 'status')
            if status_val == 'multado':
                # se for membro, mostrar apenas suas multas
                if getattr(self.usuario_logado, 'tipo', None) == 'membro':
                    if self._dig(e, 'membro', 'id') == self.usuario_logado.id:
                        emprestimos_multados.append(e)
                else:
                    emprestimos_multados.append(e)

        if not emprestimos_multados:
            tk.Label(
                card_lista,
                text="Nenhuma multa registrada no momento",
                font=("Arial", 12),
                bg='white',
                fg='#7f8c8d'
            ).pack(pady=50)
        else:
            # criar tabela de multas
            self.criar_tabela_multas(card_lista, emprestimos_multados)

    def criar_tabela_multas(self, parent, emprestimos_multados):
        """Criar tabela de multas pendentes"""
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')

        tree = ttk.Treeview(
            table_frame,
            columns=('Membro', 'Item', 'Data Empréstimo', 'Data Prevista', 'Valor da Multa', 'Status'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=12
        )

        widths = {'Membro': 150, 'Item': 200, 'Data Empréstimo': 120, 'Data Prevista': 120, 'Valor da Multa': 140, 'Status': 100}
        for col in tree['columns']:
            tree.heading(col, text=col)
            tree.column(col, width=widths.get(col, 100))

        scrollbar.config(command=tree.yview)

        for idx, emp in enumerate(emprestimos_multados):
            membro_nome = self._dig(emp, 'membro', 'nome') or 'N/A'
            item_nome = self._dig(emp, 'item', 'nome') or 'N/A'

            data_emp = self._dig(emp, 'data_emprestimo')
            data_prev = self._dig(emp, 'data_prevista_devolucao')

            data_emp_str = data_emp.strftime('%d/%m/%Y') if hasattr(data_emp, 'strftime') else (str(data_emp) if data_emp is not None else '')
            data_prev_str = data_prev.strftime('%d/%m/%Y') if hasattr(data_prev, 'strftime') else (str(data_prev) if data_prev is not None else '')

            multa_obj = self._dig(emp, 'multa')
            if multa_obj:
                valor_multa = self._dig(multa_obj, 'valor') or 0.0
                paga = self._dig(multa_obj, 'paga')
                status_multa = 'Paga' if paga else 'Pendente'
                valor_str = f"R$ {valor_multa:.2f}"
            else:
                valor_str = 'R$ 0.00'
                status_multa = 'Pendente'

            tree.insert('', 'end', iid=str(idx), values=(membro_nome, item_nome, data_emp_str, data_prev_str, valor_str, status_multa))

        tree.pack(fill='both', expand=True)

        # ações: pagar multa selecionada
        botoes_frame = tk.Frame(parent, bg='white')
        botoes_frame.pack(fill='x', padx=20, pady=12)

        def pagar_multa_selecionada():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning('Aviso', 'Selecione uma multa para pagar!')
                return
            try:
                idx = int(sel[0])
                emp = emprestimos_multados[idx]
                valor = self._dig(emp, 'multa', 'valor') or 0.0
                if messagebox.askyesno('Confirmar Pagamento', f'Deseja quitar a multa de R$ {valor:.2f}?'):
                    # usa método do modelo
                    self.biblioteca.registrar_pagamento_multa(self._dig(emp, 'id'))
                    messagebox.showinfo('Sucesso', 'Multa quitada com sucesso!')
                    self.mostrar_multas()
            except Exception as e:
                messagebox.showerror('Erro', str(e))

        tk.Button(
            botoes_frame,
            text='💳 Pagar Multa Selecionada',
            font=('Arial', 11, 'bold'),
            bg=self.cores['success'],
            fg='white',
            cursor='hand2',
            command=pagar_multa_selecionada
        ).pack(side='left', padx=8)

    def criar_card(self, parent, titulo):
        """Criar card com título"""
        card = tk.Frame(parent, bg='white', relief='raised', bd=1)
        card.pack(fill='both', expand=True, padx=30, pady=10)

        # Título do card
        tk.Label(
            card,
            text=titulo,
            font=("Arial", 14, "bold"),
            bg='white',
            fg=self.cores['dark']
        ).pack(pady=15, padx=20, anchor='w')

        return card

    def limpar_content(self):
        """Limpar área de conteúdo"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def limpar_tela(self):
        """Limpar toda a tela"""
        for widget in self.winfo_children():
            widget.destroy()

    def logout(self):
        """Fazer logout"""
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.usuario_logado = None
            
            # Remover sessão
            if os.path.exists("session.json"):
                try:
                    os.remove("session.json")
                except Exception:
                    pass
                    
            self.criar_tela_login()

if __name__ == "__main__":
    app = SistemaBiblioteca()
    app.mainloop()
