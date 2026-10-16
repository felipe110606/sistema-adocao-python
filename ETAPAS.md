# Etapas do Projeto 2 — 16/10/2026

Base: “BASE PRÁTICA SQLITE - FELIPE (COLAB)”, atualizada após os exercícios de CRUD em funções.

## Etapa 1 — Camada de banco
Criado banco.py com tabela animais e funções para cadastrar, listar, buscar por ID, editar, adotar e excluir.
O arquivo adocao.db fica ao lado do código. Cada operação abre/fecha a conexão e confirma ou desfaz sua transação.
O ID substitui a busca por nome nas ações: dois animais podem ter o mesmo nome.
Validação: CRUD e reabertura do banco em arquivo temporário; código de terminal preservado.


## Etapa 2 — Flask, formulário e Jinja
A lista em memória foi substituída pelas funções de banco.py. URLs e campos de edição usam animal.id. IDs inexistentes retornam 404. O site mantém os dados entre execuções.

## Etapa 3 — Testes, documentação e GitHub
Seis testes de integração cobrem CRUD, rejeição de campos inválidos sem alteração parcial, status preservado na edição, IDs estáveis com nomes repetidos, HTML escapado, CSS, métodos HTTP e IDs inexistentes. A persistência foi conferida recriando a aplicação e lendo o banco em outro processo Python.
Os testes usam banco temporário e não alteram cadastros reais. README atualizado com execução, testes e backup. Bancos e arquivos auxiliares estão fora do Git. As três etapas foram salvas em commits separados.

## Para revisar no VS Code
1. Abra banco.py: compare SELECT/INSERT/UPDATE/DELETE com o Colab.
2. Abra app.py: acompanhe POST → banco → redirect.
3. Abra templates/index.html: veja animal.id substituir loop.index0.
4. Execute python app.py pelo ambiente .venv, cadastre um animal e reinicie o servidor para conferir a persistência.

Referência recente: https://docs.google.com/document/d/1whpyJ6jMmX54Z_cLLK9wUJytE85e5o4FtJR6XsD2dw0/edit
