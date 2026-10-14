# Sistema de Adoção de Animais

Projeto 2 dos estudos de Python do Felipe: terminal → HTML/CSS → Flask/Jinja → SQLite (próxima etapa).

## Funcionalidades
- Cadastrar e listar animais.
- Marcar como adotado.
- Editar dados e excluir.
- Validar campos e idade no servidor.

Os dados ficam em uma lista Python em memória e desaparecem ao reiniciar o servidor. Este é um projeto local de aprendizado.

## Executar no Windows / VS Code
Abra esta pasta no VS Code e use o terminal:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```
Abra http://127.0.0.1:5000/ no navegador. Para encerrar, use Ctrl+C no terminal.

## Estrutura
- app.py: rotas Flask e lógica web.
- sistema_adocao.py: código original de terminal preservado.
- templates/index.html: interface com Jinja.
- static/style.css: estilos.
- referencias/: material original de estudo.
- requirements.txt: dependência da aplicação.

## O que acontece ao cadastrar
O formulário faz POST para /cadastro; Python valida os campos, adiciona o dicionário à lista e redireciona para /. Jinja transforma a lista em cartões HTML. As ações de edição, adoção e exclusão também usam POST.

## Referências
- [Resumo Geral Flask](https://docs.google.com/document/d/1J6_kcEnOr8cgVy6HMpSIIyyL76fFtWugvgvBUirro6I/edit)
- [Esqueleto de terminal](https://docs.google.com/document/d/1Iva6bip2B_Y-Ub3HXZffjzCiCtrHCmLcXJxYBpYwcrI/edit)
- [Documentação Flask](https://flask.palletsprojects.com/en/stable/quickstart/)
