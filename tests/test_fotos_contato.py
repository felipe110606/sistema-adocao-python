import io
import sqlite3
import tempfile
import unittest
from pathlib import Path

from PIL import Image
import banco
from app import create_app


class FotosContatoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'teste.db'
        self.fotos = Path(self.tmp.name) / 'fotos'
        self.app = create_app({'TESTING': True, 'DATABASE': self.db, 'UPLOAD_FOLDER': self.fotos})
        self.client = self.app.test_client()
        self.dados = dict(nome='Luna', especie='Gato', idade='2', porte='Pequeno',
                          doador_nome='Pessoa Teste', doador_telefone='(11) 99999-1234',
                          localizacao='São Paulo / SP - Centro')

    def foto(self, cor='green'):
        arquivo = io.BytesIO()
        Image.new('RGB', (30, 20), cor).save(arquivo, 'PNG')
        arquivo.seek(0)
        return arquivo, '../../foto.png'

    def test_foto_contato_persistencia_edicao_adocao_exclusao(self):
        r = self.client.post('/cadastro', data=self.dados | {'foto': self.foto()}, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn('Pessoa Teste', r.get_data(as_text=True))
        animal = banco.listar_animais(self.db)[0]
        self.assertEqual(animal['localizacao'], self.dados['localizacao'])
        antiga = animal['foto']
        self.assertTrue((self.fotos / antiga).is_file())
        with self.client.get('/fotos/' + antiga) as foto:
            self.assertEqual(foto.status_code, 200)
            self.assertEqual(foto.mimetype, 'image/jpeg')
        self.client.post(f"/adotar/{animal['id']}")
        self.client.post(f"/editar/{animal['id']}", data=self.dados)
        self.assertEqual(banco.buscar_animal(animal['id'], self.db)['foto'], antiga)
        self.assertTrue((self.fotos / antiga).is_file())
        r = self.client.post(f"/editar/{animal['id']}", data=self.dados | {'foto': self.foto('blue')})
        self.assertEqual(r.status_code, 302)
        novo = banco.buscar_animal(animal['id'], self.db)
        self.assertEqual(novo['status'], 'Adotado')
        self.assertFalse((self.fotos / antiga).exists())
        self.assertTrue((self.fotos / novo['foto']).exists())
        nova_app = create_app({'TESTING': True, 'DATABASE': self.db, 'UPLOAD_FOLDER': self.fotos})
        self.assertIn('São Paulo', nova_app.test_client().get('/').get_data(as_text=True))
        self.client.post(f"/excluir/{animal['id']}")
        self.assertEqual(list(self.fotos.iterdir()), [])

    def test_invalidos_nao_criam_fotos_ou_cadastros(self):
        for mudancas in ({'foto': (io.BytesIO(b'nao e imagem'), 'foto.png')},
                         {'foto': (io.BytesIO(b'<svg/>'), 'foto.svg')},
                         {'foto': self.foto(), 'idade': '-1'},
                         {'foto': self.foto(), 'doador_telefone': 'abc'},
                         {'foto': (io.BytesIO(b'x' * (5 * 1024 * 1024 + 1)), 'foto.png')}):
            self.assertEqual(self.client.post('/cadastro', data=self.dados | mudancas).status_code, 400)
        self.assertEqual(banco.listar_animais(self.db), [])
        self.assertFalse(self.fotos.exists())
        self.assertEqual(self.client.get('/fotos/../adocao.db').status_code, 404)

    def test_migracao_preserva_cadastro_antigo(self):
        legado = Path(self.tmp.name) / 'legado.db'
        with sqlite3.connect(legado) as c:
            c.execute('CREATE TABLE animais (id INTEGER PRIMARY KEY, nome TEXT, especie TEXT, idade INTEGER, porte TEXT, status TEXT)')
            c.execute("INSERT INTO animais VALUES (7, 'Antigo', 'Gato', 3, 'Pequeno', 'Adotado')")
        c.close()
        banco.inicializar_banco(legado)
        banco.inicializar_banco(legado)
        animal = banco.buscar_animal(7, legado)
        self.assertEqual((animal['nome'], animal['status'], animal['foto']), ('Antigo', 'Adotado', ''))
        self.assertEqual(animal['doador_nome'], '')

    def test_filtros_e_mensagens(self):
        self.client.post('/cadastro', data=self.dados)
        r = self.client.get('/?busca=Luna&especie=Gato&porte=Pequeno&status=Disponível&ordenar=nome')
        self.assertEqual(r.status_code, 200)
        self.assertIn('foi cadastrado com sucesso', r.get_data(as_text=True))
        self.assertIn('Pessoa Teste', r.get_data(as_text=True))
        self.assertEqual(len(banco.filtrar_animais(busca='Luna', caminho=self.db)), 1)

    def test_edicao_invalida_preserva_foto_e_contato(self):
        self.client.post('/cadastro', data=self.dados | {'foto': self.foto()})
        antes = banco.listar_animais(self.db)[0]
        r = self.client.post(f"/editar/{antes['id']}", data=self.dados | {
            'foto': (io.BytesIO(b'invalido'), 'nova.jpg'), 'doador_nome': 'Outro'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(banco.buscar_animal(antes['id'], self.db), antes)
        self.assertEqual([p.name for p in self.fotos.iterdir()], [antes['foto']])
        self.client.post(f"/editar/{antes['id']}", data={
            k: self.dados[k] for k in ('nome', 'especie', 'idade', 'porte')})
        self.assertEqual(banco.buscar_animal(antes['id'], self.db), antes)

    def test_requisicao_grande_e_falha_no_banco(self):
        r = self.client.post('/cadastro', data=self.dados | {
            'foto': (io.BytesIO(b'x' * (6 * 1024 * 1024 + 1)), 'foto.jpg')})
        self.assertEqual(r.status_code, 413)
        from unittest.mock import patch
        with patch('banco.cadastrar_animal', side_effect=sqlite3.OperationalError('falha simulada')):
            with self.assertRaises(sqlite3.OperationalError):
                self.client.post('/cadastro', data=self.dados | {'foto': self.foto()})
        self.assertEqual(list(self.fotos.iterdir()), [])
        self.assertEqual(banco.listar_animais(self.db), [])


if __name__ == '__main__':
    unittest.main()
