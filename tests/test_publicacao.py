import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from werkzeug.security import generate_password_hash
from app import create_app
import banco


class PublicacaoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.senha = 'senha-de-teste-comprida'
        cls.hash = generate_password_hash(cls.senha)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'teste.db'
        self.config = dict(TESTING=True, DATABASE=self.db, PUBLIC_MODE=True,
                           SECRET_KEY='segredo-apenas-para-testes', ADMIN_PASSWORD_HASH=self.hash,
                           UPLOAD_FOLDER=Path(self.tmp.name) / 'fotos')
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.id = banco.cadastrar_animal('Luna', 'Gato', 2, 'Pequeno', caminho=self.db,
                                        doador_nome='Doador teste', localizacao='São Paulo')

    def token(self):
        self.client.get('/entrar')
        with self.client.session_transaction() as sessao:
            return sessao['csrf_token']

    def entrar(self):
        r = self.client.post('/entrar?destino=cadastro', data={'csrf_token': self.token(), 'senha': self.senha})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers['Location'].endswith('#cadastro'))
        self.client.get('/')
        with self.client.session_transaction() as sessao:
            return sessao['csrf_token']

    def test_visitante_consulta_sem_alterar(self):
        r = self.client.get('/?busca=Luna')
        texto = r.get_data(as_text=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn('Luna', texto)
        self.assertIn('Doador teste', texto)
        self.assertNotIn('id="cadastro-nome"', texto)
        self.assertNotIn('form-excluir-', texto)
        self.assertIn('Área administrativa', texto)
        antes = banco.listar_animais(self.db)
        for rota in ('/cadastro', f'/adotar/{self.id}', f'/editar/{self.id}', f'/excluir/{self.id}'):
            self.assertEqual(self.client.post(rota, data={}).status_code, 403)
        self.assertEqual(banco.listar_animais(self.db), antes)

    def test_admin_csrf_sair(self):
        self.assertEqual(self.client.post('/entrar', data={'senha': self.senha}).status_code, 400)
        token = self.entrar()
        texto = self.client.get('/').get_data(as_text=True)
        self.assertIn('id="cadastro-nome"', texto)
        self.assertIn('form-excluir-', texto)
        self.assertEqual(self.client.post(f'/adotar/{self.id}').status_code, 400)
        self.assertEqual(self.client.post(f'/adotar/{self.id}', data={'csrf_token': token}).status_code, 302)
        self.assertEqual(banco.buscar_animal(self.id, self.db)['status'], 'Adotado')
        self.assertEqual(self.client.post('/sair', data={'csrf_token': token}).status_code, 302)
        self.assertEqual(self.client.post(f'/excluir/{self.id}', data={'csrf_token': token}).status_code, 403)

    def test_limite_de_tentativas(self):
        token = self.token()
        for _ in range(5):
            self.assertEqual(self.client.post('/entrar', data={'csrf_token': token, 'senha': 'errada'}).status_code, 401)
        self.assertEqual(self.client.post('/entrar', data={'csrf_token': token, 'senha': self.senha}).status_code, 429)
        import time
        futuro = time.monotonic() + 301
        with patch('acesso.time.monotonic', return_value=futuro):
            self.assertEqual(self.client.post('/entrar', data={'csrf_token': token, 'senha': self.senha}).status_code, 302)

    def test_segredos_exigidos_e_config_producao(self):
        with self.assertRaises(RuntimeError):
            create_app(self.config | {'ADMIN_PASSWORD_HASH': None})
        with self.assertRaises(RuntimeError):
            create_app(self.config | {'SECRET_KEY': 'chave-local-desenvolvimento'})
        app = create_app(self.config | {'TESTING': False})
        self.assertTrue(app.config['SESSION_COOKIE_SECURE'])
        self.assertFalse(app.debug)
        r = self.client.get('/')
        self.assertEqual(r.headers['Cache-Control'], 'no-store')
        self.assertEqual(r.headers['X-Content-Type-Options'], 'nosniff')


if __name__ == '__main__':
    unittest.main()
