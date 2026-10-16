# Sistema de Adoção de Animais

Projeto 2 dos estudos de Python do Felipe: terminal → HTML/CSS → Flask/Jinja → SQLite.

## Funcionalidades
Cadastro, listagem, edição, adoção e exclusão por ID, com validação no servidor e persistência após reiniciar a aplicação.

## Executar no Windows / VS Code
Abra esta pasta e use o terminal:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```
Se .venv já existe, pule sua criação. Abra http://127.0.0.1:5000/.
Ctrl+C encerra o servidor; execute novamente o último comando para reiniciar.

A tabela é criada automaticamente. adocao.db fica ao lado de banco.py, independentemente do diretório do terminal. Um clone novo começa vazio.

## Arquivos
- app.py: rotas Flask e formulários.
- banco.py: conexão, tabela e CRUD SQL.
- sistema_adocao.py: terminal original preservado.
- templates/index.html: Jinja com animal.id.
- static/style.css: estilos.
- tests/test_sqlite.py: testes com banco temporário isolado.
- ETAPAS.md: registro de cada etapa.
- referencias/: material histórico.
- requirements.txt: Flask.

## Fluxo
Formulário → POST → validação → INSERT/UPDATE/DELETE → redirect → SELECT → Jinja.
As ações usam o ID: nomes podem se repetir. Excluir um animal não muda o ID dos demais.
A edição valida todos os campos antes de alterar e preserva o status.
ID inexistente retorna 404. Cada operação abre/fecha sua conexão, usa parâmetros ? e transações.
CREATE TABLE IF NOT EXISTS conserva dados; não migra automaticamente esquemas antigos.

## Testar
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
Testa CRUD, validações, IDs, nomes repetidos, HTML escapado e persistência numa nova aplicação e em outro processo Python. Os testes não usam seu banco de cadastros.

## Dados e backup
adocao.db e arquivos auxiliares ficam fora do Git. GitHub guarda o código e não faz backup dos cadastros.
Para copiar o banco, encerre o servidor e guarde uma cópia do arquivo em local separado.
O banco do Colab e os antigos cadastros da lista em memória não são importados automaticamente.
Projeto para estudo local.

## Referências
- [Prática SQLite recente](https://docs.google.com/document/d/1whpyJ6jMmX54Z_cLLK9wUJytE85e5o4FtJR6XsD2dw0/edit)
- [Resumo Flask](https://docs.google.com/document/d/1J6_kcEnOr8cgVy6HMpSIIyyL76fFtWugvgvBUirro6I/edit)
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [Banco no Flask](https://flask.palletsprojects.com/en/stable/tutorial/database/)
