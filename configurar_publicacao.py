"""Execute no servidor para definir a senha sem expô-la nos arquivos do projeto."""
import getpass
import json
import os
from pathlib import Path
import secrets

from werkzeug.security import generate_password_hash


def main():
    raiz = Path(__file__).resolve().parent
    pasta = raiz / 'instance'
    pasta.mkdir(exist_ok=True)
    arquivo = pasta / 'publicacao.json'
    senha = getpass.getpass('Crie a senha de administração (mínimo 12 caracteres): ')
    if len(senha) < 12 or len(senha) > 256:
        raise SystemExit('Use de 12 a 256 caracteres. Nenhuma alteração feita.')
    if senha != getpass.getpass('Repita a senha: '):
        raise SystemExit('As senhas não conferem. Nenhuma alteração feita.')
    atual = json.loads(arquivo.read_text()) if arquivo.exists() else {}
    config = dict(PUBLIC_MODE=True, SECRET_KEY=atual.get('SECRET_KEY') or secrets.token_urlsafe(48),
                  ADMIN_PASSWORD_HASH=generate_password_hash(senha))
    # A gravação é atômica para não deixar configuração parcial.
    temporario = pasta / 'publicacao.tmp'
    fd = os.open(temporario, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as destino:
        json.dump(config, destino)
    temporario.replace(arquivo)
    print('Administração configurada. Recarregue o aplicativo no painel Web.')


if __name__ == '__main__':
    main()
