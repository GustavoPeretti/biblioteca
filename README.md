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

Cada classe foi organizada em um arquivo *python* no diretório *modelos*. As classes abstratas foram configuradas com a herança da classe `abc` e com a marcação dos métodos abstratos com o *decorator* `@abstractmethod`.


## Persistência de Dados

Para garantir a integridade e a durabilidade das informações, optou-se pela utilização do banco de dados SQLite. Desta forma, todos os registros de usuários, itens, empréstimos e reservas são armazenados permanentemente no arquivo `biblioteca.db`, permitindo que o estado do sistema seja preservado entre diferentes execuções.

A camada de persistência foi integrada de forma transparente às classes de modelo, assegurando que as regras de negócio permaneçam desacopladas da lógica de armazenamento. Adicionalmente, implementou-se um mecanismo de sessão persistente via arquivo `session.json`, que armazena as credenciais do usuário logado, agilizando o acesso ao sistema em usos subsequentes.

## Utilização como *library*

Essa é uma forma de representar dados de uma biblioteca por meio da classe biblioteca.



Para utilizar como library basta abrir um novo repositório, importar moledos.biblioteca

```python

from modelos.biblioteca import Biblioteca

biblioteca = Biblioteca()

from modelos.biblioteca import Biblioteca

biblioteca = Biblioteca()

biblioteca.adicionar_usuario('Nome', 'nome@email.com', 'senha', '111.111.111-11', 'membro')

```

Os métodos que podem ser utilizados na instância de Biblioteca são:

- adicionar_usuario: possui os atributos 'nome', 'email', 'senha', 'cpf' e 'tipo';
- remover_usuario: possui o atributo 'id';
- adicionar_item: possui atributo 'id';
- remover_item: possui o atributo 'id';
- emprestar_item: possui os atributos 'membro' e 'item';
- renovar_emprestimo: possui o atributo 'id_emprestimo';
- reservar_item: possui os atributos 'item' e 'membro';
- registrar_pagamento_multa: possui o atributo 'id_emprestimo';
- registar_devolucao: possui o atributo 'id_emprestimo';

## Utilização com interface gráfica

Para utilizar com intereface gráfica basta abrir o terminal e dar o comando 'python3 run.py'
