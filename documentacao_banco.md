# Documentação do Banco de Dados - Sistema de Biblioteca

## Visão Geral

O sistema utiliza um banco de dados **SQLite** (`biblioteca.db`) para persistência de dados. O banco é relacional e normalizado, garantindo integridade e eficiência.

## Diagrama ER (Conceitual)

- **Usuarios** (1) <--- (N) **Emprestimos** (N) ---> (1) **Itens**
- **Usuarios** (1) <--- (N) **Reservas** (N) ---> (1) **Itens**
- **Emprestimos** (1) <--- (1) **Multas**

## Tabelas

### 1. `usuarios`

Armazena os dados de todos os usuários do sistema (Membros, Bibliotecários, Administradores).

| Coluna  | Tipo        | Descrição                                                   |
| :------ | :---------- | :---------------------------------------------------------- |
| `id`    | INTEGER PK  | Identificador único (Auto-incremento)                       |
| `nome`  | TEXT        | Nome completo do usuário                                    |
| `email` | TEXT UNIQUE | Email para login (deve ser único)                           |
| `senha` | TEXT        | Senha do usuário                                            |
| `cpf`   | TEXT UNIQUE | CPF do usuário (deve ser único)                             |
| `tipo`  | TEXT        | Tipo de usuário: 'membro', 'bibliotecario', 'administrador' |

### 2. `itens`

Armazena o acervo da biblioteca (Livros e Ebooks).

| Coluna           | Tipo       | Descrição                                  |
| :--------------- | :--------- | :----------------------------------------- |
| `id`             | INTEGER PK | Identificador único                        |
| `tipo`           | TEXT       | Tipo do item: 'livro' ou 'ebook'           |
| `nome`           | TEXT       | Título da obra                             |
| `autor`          | TEXT       | Autor da obra                              |
| `num_paginas`    | INTEGER    | Número de páginas                          |
| `isbn`           | TEXT       | Código ISBN                                |
| `categoria`      | TEXT       | Gênero ou categoria                        |
| `emprestavel`    | BOOLEAN    | Se o item pode ser emprestado (Default: 1) |
| `imagem_url`     | TEXT       | URL da capa (opcional)                     |
| `imagem_arquivo` | TEXT       | Caminho local da capa (opcional)           |
| `arquivo`        | TEXT       | Caminho do arquivo PDF (apenas Ebooks)     |
| `url`            | TEXT       | URL de acesso (apenas Ebooks)              |
| `data_cadastro`  | TEXT       | Data de registro no sistema (ISO 8601)     |

### 3. `emprestimos`

Registra os empréstimos realizados.

| Coluna                  | Tipo       | Descrição                                                    |
| :---------------------- | :--------- | :----------------------------------------------------------- |
| `id`                    | INTEGER PK | Identificador único                                          |
| `item_id`               | INTEGER FK | Referência à tabela `itens`                                  |
| `membro_id`             | INTEGER FK | Referência à tabela `usuarios`                               |
| `data_emprestimo`       | TEXT       | Data de retirada (ISO 8601)                                  |
| `data_devolucao`        | TEXT       | Data real da devolução (ISO 8601)                            |
| `data_quitacao`         | TEXT       | Data de pagamento de multa (se houver)                       |
| `status`                | TEXT       | 'ativo', 'multado', 'finalizado' (valores válidos no schema) |
| `quantidade_renovacoes` | INTEGER    | Contador de renovações (limite configurável em `config.py`)  |

### 4. `reservas`

Gerencia a fila de espera por itens emprestados.

| Coluna              | Tipo       | Descrição                                           |
| :------------------ | :--------- | :-------------------------------------------------- |
| `id`                | INTEGER PK | Identificador único                                 |
| `item_id`           | INTEGER FK | Referência à tabela `itens`                         |
| `membro_id`         | INTEGER FK | Referência à tabela `usuarios`                      |
| `data_reserva`      | TEXT       | Data da solicitação (ISO 8601)                      |
| `data_cancelamento` | TEXT       | Data de cancelamento (se houver)                    |
| `data_finalizacao`  | TEXT       | Data de conclusão (se houver)                       |
| `status`            | TEXT       | 'aguardando', 'cancelada', 'expirada', 'finalizada' |

### 5. `multas`

Registra multas geradas por atraso na devolução.

| Coluna          | Tipo       | Descrição                         |
| :-------------- | :--------- | :-------------------------------- |
| `id`            | INTEGER PK | Identificador único               |
| `emprestimo_id` | INTEGER FK | Referência à tabela `emprestimos` |
| `valor`         | REAL       | Valor monetário da multa          |
| `paga`          | BOOLEAN    | Status de pagamento (0 ou 1)      |

## Notas Técnicas

- **Datas**: Armazenadas como strings no formato ISO 8601 (`YYYY-MM-DD HH:MM:SS.ssssss`) para compatibilidade com SQLite.
- **IDs**: Utiliza `INTEGER AUTOINCREMENT` do SQLite, mapeado internamente para os objetos do sistema.
- **Integridade**: Foreign Keys ativadas para garantir consistência entre tabelas.
