"""Consulta pública e administração protegida na versão hospedada."""
import hmac
import secrets
import time
from threading import Lock

from flask import abort, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash


def configurar_acesso(app):
    tentativas = {}
    trava = Lock()

    def csrf_token():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)
        return session['csrf_token']

    @app.context_processor
    def contexto_acesso():
        publico = app.config['PUBLIC_MODE']
        return dict(modo_publico=publico,
                    pode_gerenciar=not publico or session.get('admin') is True,
                    csrf_token=csrf_token)

    @app.before_request
    def proteger_alteracoes():
        if not app.config['PUBLIC_MODE']:
            return
        if request.method == 'POST':
            if request.endpoint != 'entrar' and session.get('admin') is not True:
                abort(403)
            token = request.form.get('csrf_token', '')
            esperado = session.get('csrf_token', '')
            if not token or not esperado or not hmac.compare_digest(token.encode(), esperado.encode()):
                abort(400)

    @app.after_request
    def cabecalhos(resposta):
        if app.config['PUBLIC_MODE']:
            resposta.headers['X-Content-Type-Options'] = 'nosniff'
            resposta.headers['X-Frame-Options'] = 'DENY'
            resposta.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            resposta.headers['Content-Security-Policy'] = "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
            if request.endpoint not in ('static', 'foto_animal'):
                resposta.headers['Cache-Control'] = 'no-store'
        return resposta

    @app.route('/entrar', methods=['GET', 'POST'])
    def entrar():
        ancora = '#cadastro' if request.args.get('destino') == 'cadastro' else '#lista'
        if not app.config['PUBLIC_MODE'] or session.get('admin') is True:
            return redirect(url_for('inicio') + ancora)
        erro = None
        if request.method == 'POST':
            ip = request.remote_addr or 'desconhecido'
            agora = time.monotonic()
            with trava:
                for chave in list(tentativas):
                    if tentativas[chave][1] <= agora:
                        del tentativas[chave]
                total, prazo = tentativas.get(ip, (0, agora + 300))
                if total >= 5 or len(tentativas) >= 1024:
                    return render_template('entrar.html', erro='Muitas tentativas. Aguarde cinco minutos.'), 429
                tentativas[ip] = (total + 1, prazo)
            senha = request.form.get('senha', '')
            if len(senha) <= 256 and check_password_hash(app.config['ADMIN_PASSWORD_HASH'], senha):
                session.clear()
                session['admin'] = True
                session.permanent = True
                with trava:
                    tentativas.pop(ip, None)
                return redirect(url_for('inicio') + ancora)
            erro = 'Senha incorreta.'
        return render_template('entrar.html', erro=erro), 401 if erro else 200

    @app.route('/sair', methods=['POST'])
    def sair():
        session.clear()
        return redirect(url_for('inicio'))
