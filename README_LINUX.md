# Guia de Instalação e Execução no Linux

## Pré-requisitos

### 1. Instalar Python 3

Certifique-se de ter Python 3 instalado:

```bash
python3 --version
```

Se não estiver instalado:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

### 2. Instalar Tkinter

**IMPORTANTE:** O Tkinter não vem instalado por padrão no Linux!

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

Para verificar se o Tkinter está instalado corretamente:

```bash
python3 -c "import tkinter; print('Tkinter instalado com sucesso!')"
```

## Instalação do Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/GustavoPeretti/biblioteca.git
cd biblioteca
```

### 2. Inicializar o banco de dados

**PASSO CRÍTICO:** Antes de executar o sistema pela primeira vez, você DEVE inicializar o banco de dados:

```bash
python3 database/init_db.py
```

Este comando irá:
- Criar o arquivo `biblioteca.db` na raiz do projeto
- Criar todas as tabelas necessárias
- Popular o banco com usuários de teste

Você verá uma saída similar a:

```
🗄️  Inicializando banco de dados...
📁 Caminho: /caminho/para/biblioteca.db
📋 Criando tabelas...
✅ Tabelas criadas com sucesso!

🧹 Normalizando usuários: removendo usuários existentes e criando usuários padrão...
    ✓ Administrador criado (ID: 1)
    ✓ Bibliotecário criado (ID: 2)
    ✓ Membro criado (ID: 3)
    ✓ Livro criado: O Senhor dos Anéis (ID: 1)
    ✓ Livro criado: 1984 (ID: 2)
    ✓ Ebook criado: Clean Code (ID: 3)

✅ Banco de dados inicializado com sucesso!
```

### 3. Executar o sistema

```bash
python3 run.py
```

## Credenciais de Teste

Após inicializar o banco de dados, você pode fazer login com:

- **Administrador:**
  - Email: `admin@biblioteca.com`
  - Senha: `admin123`

- **Bibliotecário:**
  - Email: `maria@biblioteca.com`
  - Senha: `biblio123`

- **Membro:**
  - Email: `joao@email.com`
  - Senha: `senha123`

## Solução de Problemas

### Erro: "Email ou senha incorretos" mesmo com credenciais corretas

**Causa:** O banco de dados não foi inicializado.

**Solução:**
```bash
python3 database/init_db.py
```

### Erro: "No module named 'tkinter'"

**Causa:** Tkinter não está instalado.

**Solução:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

### Erro: "No such file or directory: 'biblioteca.db'"

**Causa:** O banco de dados não foi criado.

**Solução:**
```bash
python3 database/init_db.py
```

### Erro de permissão ao criar o banco de dados

**Causa:** Sem permissão de escrita no diretório.

**Solução:**
```bash
chmod +w .
python3 database/init_db.py
```

## Estrutura do Projeto

```
biblioteca/
├── database/
│   ├── init_db.py          # Script de inicialização do banco
│   ├── db_manager.py       # Gerenciador de conexão
│   └── repositories/       # Repositórios de dados
├── modelos/                # Classes do domínio
├── interface/              # Interface gráfica (Tkinter)
├── biblioteca.db           # Banco de dados SQLite (criado após init_db.py)
├── run.py                  # Arquivo principal para executar
└── README.md               # Documentação principal
```

## Notas Importantes

1. **Sempre execute `python3 database/init_db.py` após clonar o repositório pela primeira vez**
2. O script `init_db.py` é idempotente - pode ser executado múltiplas vezes sem problemas
3. Se quiser resetar o banco de dados, delete `biblioteca.db` e execute `init_db.py` novamente
4. O arquivo `run.py` tenta executar `init_db.py` automaticamente, mas é recomendado executá-lo manualmente primeiro
