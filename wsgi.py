"""Entrada WSGI para hospedagem; nunca inicia o servidor de desenvolvimento."""
import json
from pathlib import Path
from app import create_app

arquivo = Path(__file__).resolve().parent / 'instance' / 'publicacao.json'
if not arquivo.is_file():
    raise RuntimeError('Execute configurar_publicacao.py no servidor antes de publicar.')
config = json.loads(arquivo.read_text(encoding='utf-8'))
config['PUBLIC_MODE'] = True
application = create_app(config)
