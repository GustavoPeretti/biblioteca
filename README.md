# Biblioteca

## Projeto

Este trabalho foi desenvolvido durante a disciplina Programação Orientada a Objetos, com o objetivo de aprofundar os conceitos apresentados em aula e desenvolver habilidades de desenvolvimento de projetos práticos.

O sistema desenvolvido consiste em um ambiente virtual para gerenciamento de uma biblioteca, contemplando todas as funcionalidades básicas para o funcionamento adequado.

Optou-se pela implementação detalhada de regras de negócio para os processos de uma biblioteca, evitando comportamentos inesperados ao iniciar empréstimos, renovações e devoluções.

Os códigos de verificação de integridade foram documentados com linhas de comentários explicando a lógica utilizada no desenvolvimento. Essa decisão facilita a correção de erros por outros desenvolvedores, mantendo as regras de negócio do sistema evidentes no próprio código.

## Funcionamento

O sistema pode ser acessado por três atores, especificados na imagem abaixo:

![Alt text](https://raw.githubusercontent.com/GustavoPeretti/biblioteca/refs/heads/main/docs/use-case.png "Optional title")

O bibliotecário acessa o sistema pelo lugar físico da biblioteca, podendo fazer as seguintes ações: renovar o empréstimo quando solicitado pelo membro, registrar o pagamento de multas caso o membro não devolva ou renove o livro dentro do prazo estabelecido, devolver o item quando o membro faz a devolução, adicionar item quando um livro físico é adicionado na biblioteca física ou quando um ebook é adicionado no sistema, remover item caso um livro ou ebook não existe mais no sistema e emprestar item se solicitado pelo membro, desde que o livro não esteja em reserva ou empréstimo.

O administrador é o ator que faz o gerenciamento de usuários, podendo adicionar ou remover um bibliotecário ou membro.

O membro é o ator que solicita os empréstimos física ou virtualmente, podendo fazer seu cadastro ou reservar um item.

## Implementação

A figura abaixo contém as principais classes projetadas na etapa de design do sistema.

![Alt text](https://raw.githubusercontent.com/GustavoPeretti/biblioteca/refs/heads/main/docs/classes.png "Optional title")

Cada classe foi organizada em um arquivo _python_ no diretório _modelos_. As classes abstratas foram configuradas com a herança da classe `abc` e com a marcação dos métodos abstratos com o _decorator_ `@abstractmethod`.

## Utilização como _library_

Essa é uma forma de representar dados de uma biblioteca por meio da classe biblioteca.

Para utilizar como library basta importar a classe `Biblioteca` e instanciá-la:

```python
from modelos.biblioteca import Biblioteca

biblioteca = Biblioteca()

# Exemplo: adicionar um usuário
biblioteca.adicionar_usuario('Nome', 'nome@email.com', 'senha', '111.111.111-11', 'membro')
```

Os métodos públicos mais usados na instância de `Biblioteca` são:

- `adicionar_usuario(nome, email, senha, cpf, tipo)`: adiciona um usuário;
- `remover_usuario(id)`: remove um usuário pelo `id`;
- `adicionar_item(item)`: adiciona um item (recebe um objeto `Livro` ou `Ebook`);
- `remover_item(id)`: remove um item pelo `id`;
- `emprestar_item(item, membro)`: registra um empréstimo;
- `renovar_emprestimo(id_emprestimo)`: renova um empréstimo pelo `id`;
- `reservar_item(item, membro)`: cria uma reserva para um item emprestado;
- `registrar_pagamento_multa(id_emprestimo)`: registra pagamento da multa do empréstimo;
- `registrar_devolucao(id_emprestimo)`: registra a devolução do empréstimo.

## Utilização com interface gráfica

### Windows

Para executar a interface gráfica, abra o terminal na pasta do projeto e execute:

```powershell
python .\run.py
```

### Linux

**⚠️ IMPORTANTE:** No Linux, é necessário instalar o Tkinter primeiro!

Veja o guia completo de instalação: **[README_LINUX.md](README_LINUX.md)**

Resumo rápido:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk

# Depois execute:
python3 run.py
```
