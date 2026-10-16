import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import banco
from app import create_app


class IntegracaoSQLiteTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.caminho = Path(self.pasta.name) / "teste.db"
        self.config = {"TESTING": True, "DATABASE": self.caminho}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.dados = {"nome": "Luna", "especie": "Gato", "idade": "2", "porte": "Pequeno"}

    def cadastrar(self, **mudancas):
        resposta = self.client.post("/cadastro", data=self.dados | mudancas)
        self.assertEqual(resposta.status_code, 302)
        return banco.listar_animais(self.caminho)[-1]["id"]

    def test_persistencia_ao_recriar_aplicacao(self):
        animal_id = self.cadastrar()
        nova_app = create_app(self.config)
        self.assertIn(b"Luna", nova_app.test_client().get("/").data)
        self.assertEqual(banco.buscar_animal(animal_id, self.caminho)["idade"], 2)
        self.assertEqual(len(banco.listar_animais(self.caminho)), 1)
        resultado = subprocess.run(
            [sys.executable, "-c",
             "import banco, sys; print(banco.listar_animais(sys.argv[1])[0]['nome'])",
             str(self.caminho)],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True, text=True, check=True
        )
        self.assertEqual(resultado.stdout.strip(), "Luna")

    def test_crud_e_status_preservado_na_edicao(self):
        animal_id = self.cadastrar()
        self.assertEqual(self.client.post(f"/adotar/{animal_id}").status_code, 302)
        self.assertEqual(self.client.post(
            f"/editar/{animal_id}", data=self.dados | {"idade": "3", "nome": "Luna nova"}
        ).status_code, 302)
        animal = banco.buscar_animal(animal_id, self.caminho)
        self.assertEqual((animal["idade"], animal["status"]), (3, "Adotado"))
        self.assertEqual(self.client.post(f"/excluir/{animal_id}").status_code, 302)
        self.assertIsNone(banco.buscar_animal(animal_id, self.caminho))

    def test_ids_estaveis_e_nomes_repetidos(self):
        primeiro = self.cadastrar()
        segundo = self.cadastrar()
        self.client.post(f"/excluir/{primeiro}")
        self.client.post(f"/adotar/{segundo}")
        self.assertEqual(banco.buscar_animal(segundo, self.caminho)["status"], "Adotado")
        terceiro = self.cadastrar()
        self.assertGreater(terceiro, segundo)
        self.assertEqual(banco.buscar_animal(terceiro, self.caminho)["status"], "Disponível")
        pagina = self.client.get("/").get_data(as_text=True)
        self.assertIn(f"/editar/{segundo}", pagina)
        self.assertIn(f"/editar/{terceiro}", pagina)

    def test_invalidos_nao_alteram_banco(self):
        animal_id = self.cadastrar()
        antes = banco.listar_animais(self.caminho)
        for campos in ({}, self.dados | {"idade": "-1"}, self.dados | {"idade": "2.5"},
                       self.dados | {"nome": "  "}, self.dados | {"porte": "Inválido"}):
            self.assertEqual(self.client.post("/cadastro", data=campos).status_code, 400)
            self.assertEqual(self.client.post(f"/editar/{animal_id}", data=campos).status_code, 400)
        self.assertEqual(banco.listar_animais(self.caminho), antes)

    def test_valores_sao_dados_e_html_escapado(self):
        nome = "<script>alert(1)</script> O'Brien"
        animal_id = self.cadastrar(nome=nome)
        self.assertEqual(banco.buscar_animal(animal_id, self.caminho)["nome"], nome)
        pagina = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("<script>alert(1)</script>", pagina)
        self.assertIn("&lt;script&gt;", pagina)

    def test_css_metodos_e_id_inexistente(self):
        with self.client.get("/static/style.css") as resposta:
            self.assertEqual(resposta.status_code, 200)
        for rota in ("adotar", "editar", "excluir"):
            self.assertEqual(self.client.get(f"/{rota}/999").status_code, 405)
            self.assertEqual(self.client.post(f"/{rota}/999", data=self.dados).status_code, 404)


if __name__ == "__main__":
    unittest.main()
