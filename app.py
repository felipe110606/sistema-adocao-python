from flask import Flask, abort, render_template, request, redirect, url_for
import banco


def create_app(config=None):
    """Permite abrir a aplicação de novo e testar com um banco separado."""
    app = Flask(__name__)
    app.config["DATABASE"] = banco.BANCO_PADRAO
    if config:
        app.config.update(config)
    banco.inicializar_banco(app.config["DATABASE"])

    def banco_atual():
        return app.config["DATABASE"]

    def ler_formulario():
        return {
            campo: request.form.get(campo, "").strip()
            for campo in ("nome", "especie", "idade", "porte")
        }

    def formulario_invalido():
        return render_template(
            "index.html",
            animais=banco.listar_animais(banco_atual()),
            erro="Preencha nome, espécie, idade inteira não negativa e um porte válido."
        ), 400

    def exigir_animal(animal_id):
        if banco.buscar_animal(animal_id, banco_atual()) is None:
            abort(404)

    @app.route("/")
    def inicio():
        return render_template(
            "index.html", animais=banco.listar_animais(banco_atual())
        )

    @app.route("/cadastro", methods=["POST"])
    def cadastro():
        try:
            banco.cadastrar_animal(**ler_formulario(), caminho=banco_atual())
        except ValueError:
            return formulario_invalido()
        return redirect(url_for("inicio"))

    @app.route("/adotar/<int:animal_id>", methods=["POST"])
    def adotar(animal_id):
        exigir_animal(animal_id)
        banco.marcar_como_adotado(animal_id, banco_atual())
        return redirect(url_for("inicio"))

    @app.route("/excluir/<int:animal_id>", methods=["POST"])
    def excluir(animal_id):
        exigir_animal(animal_id)
        banco.excluir_animal(animal_id, banco_atual())
        return redirect(url_for("inicio"))

    @app.route("/editar/<int:animal_id>", methods=["POST"])
    def editar(animal_id):
        exigir_animal(animal_id)
        try:
            banco.editar_animal(animal_id, **ler_formulario(), caminho=banco_atual())
        except ValueError:
            return formulario_invalido()
        return redirect(url_for("inicio"))

    @app.errorhandler(404)
    def nao_encontrado(erro):
        return render_template(
            "index.html", animais=banco.listar_animais(banco_atual()),
            erro="Animal ou página não encontrado. Confira a lista atualizada."
        ), 404

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
