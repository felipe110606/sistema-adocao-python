# Publicar no PythonAnywhere gratuito

O site está preparado para Python 3.13 e uma aplicação WSGI. O servidor de desenvolvimento (`python app.py`) é apenas para uso local.

## 1. Conta e arquivos

Crie pessoalmente uma conta gratuita em https://www.pythonanywhere.com/registration/register/beginner/ e confirme o email se solicitado.

Na aba **Files**, envie `sistema-adocao-python-publicacao.zip` para sua pasta inicial. O pacote contém o código e as imagens de apresentação; não contém senhas, banco local ou fotos de cadastros.

Abra um console **Bash** e execute, uma linha por vez:

```bash
unzip -n ~/sistema-adocao-python-publicacao.zip -d ~/
cd ~/sistema-adocao-python
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python configurar_publicacao.py
```

O último comando pede uma senha de administração com pelo menos 12 caracteres e a confirmação. A senha não aparece no console. Guarde-a em seu gerenciador de senhas. O programa guarda somente o hash e cria uma chave de sessão aleatória, dentro de `instance/publicacao.json`, fora do Git e fora da pasta de arquivos públicos.

## 2. Aplicativo Web

Na aba **Web**, escolha **Add a new web app**, confirme o subdomínio gratuito, **Manual configuration**, **Python 3.13**.

Em **Virtualenv**, informe `/home/SEU_USUARIO/sistema-adocao-python/.venv`, substituindo `SEU_USUARIO` pelo nome da sua conta.

Abra o arquivo WSGI indicado nessa aba. Substitua seu conteúdo por:

```python
import sys
from pathlib import Path

projeto = Path.home() / 'sistema-adocao-python'
sys.path.insert(0, str(projeto))
from wsgi import application
```

Se o painel pedir um diretório de código, informe `/home/SEU_USUARIO/sistema-adocao-python`.

Em **Static files**, adicione:

| URL | Diretório |
| --- | --- |
| `/static/` | `/home/SEU_USUARIO/sistema-adocao-python/static/` |

Não crie um mapeamento público para a pasta do projeto, `instance/` ou o banco. As fotos são servidas pela rota `/fotos/` do aplicativo.

Ative **Force HTTPS** na seção **Security**, salve e clique em **Reload**. Acesse o endereço HTTPS mostrado no painel. No sistema dos EUA ele costuma ter o formato `https://SEU_USUARIO.pythonanywhere.com/`; no sistema europeu use o endereço informado pelo painel.

## 3. Conferir

- Visitante: vê os animais, telefone do doador, localização, fotos e filtros.
- **Área administrativa**, no rodapé: permite entrar com a senha criada no console.
- Administrador: pode cadastrar, editar, adotar, trocar fotos e excluir com confirmação.
- Faça uma atualização de teste e use **Reload** no painel; os cadastros e fotos devem permanecer.

Se o login voltar à página de entrada, confira se está acessando HTTPS e se a versão Python do virtualenv é igual à escolhida na aba Web.

## 4. Dados, manutenção e atualizações

`adocao.db` e `uploads/animais/` ficam no armazenamento da conta. O plano gratuito informa 512 MiB de espaço e expiração do aplicativo após um mês: acompanhe o prazo no painel e use a opção de extensão antes de expirar.

Faça backup do banco e das fotos juntos. Não substitua um banco existente por um arquivo vazio ao atualizar o código. O pacote de código não inclui os cadastros que você tiver criado localmente; se houver registros a importar, transfira banco e fotos antes de começar a cadastrar na versão pública.

Para trocar a senha administrativa, execute novamente `.venv/bin/python configurar_publicacao.py` e depois **Reload**. O acesso administrativo deve ser compartilhado apenas com quem pode alterar os cadastros.

## Documentação oficial

- Flask no PythonAnywhere: https://help.pythonanywhere.com/pages/Flask/
- Plano gratuito: https://help.pythonanywhere.com/pages/FreeAccountsFeatures/
- HTTPS obrigatório: https://help.pythonanywhere.com/pages/ForcingHTTPS
