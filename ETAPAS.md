# Etapas do Projeto 2 — 16/10/2026

Base: “BASE PRÁTICA SQLITE - FELIPE (COLAB)”, atualizada após os exercícios de CRUD em funções.

## Etapa 1 — Camada de banco
Criado banco.py com tabela animais e funções para cadastrar, listar, buscar por ID, editar, adotar e excluir.
O arquivo adocao.db fica ao lado do código. Cada operação abre/fecha a conexão e confirma ou desfaz sua transação.
O ID substitui a busca por nome nas ações: dois animais podem ter o mesmo nome.
Validação: CRUD e reabertura do banco em arquivo temporário; código de terminal preservado.

