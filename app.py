import os
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError
from flask import send_from_directory

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

import banco


def create_app(config=None):

    app = Flask(__name__)

    app.config["DATABASE"] = banco.BANCO_PADRAO

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "chave-local-desenvolvimento"
    )

    app.config["UPLOAD_FOLDER"] = Path(app.root_path) / "uploads" / "animais"
    app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024

    app.config.update(
        PUBLIC_MODE=False,
        ADMIN_PASSWORD_HASH=None,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    )

    if config:
        app.config.update(config)

    if app.config["PUBLIC_MODE"]:
        if not app.config["ADMIN_PASSWORD_HASH"] or app.config["SECRET_KEY"] == "chave-local-desenvolvimento":
            raise RuntimeError("Configure a chave secreta e a senha administrativa antes de publicar.")
        app.config["DEBUG"] = False
        app.config["SESSION_COOKIE_SECURE"] = not app.config.get("TESTING", False)

    from acesso import configurar_acesso
    configurar_acesso(app)

    banco.inicializar_banco(
        app.config["DATABASE"]
    )


    # ======================================
    # BANCO ATUAL
    # ======================================

    def banco_atual():

        return app.config["DATABASE"]


    # ======================================
    # LER FORMULÁRIO
    # ======================================

    def ler_formulario():

        return {
            campo: request.form.get(
                campo,
                ""
            ).strip()

            for campo in (
                "nome",
                "especie",
                "idade",
                "porte", "doador_nome", "doador_telefone", "localizacao"
            )
        }


    # ======================================
    # FORMULÁRIO INVÁLIDO
    # ======================================

    def formulario_invalido(mensagem=None):

        return render_template(
            "index.html",

            animais=banco.listar_animais(
                banco_atual()
            ),

            erro=mensagem or (
                "Preencha nome, espécie, "
                "idade inteira não negativa "
                "e um porte válido."
            )
        ), 400


    def salvar_foto():
        arquivo = request.files.get("foto")
        if not arquivo or not arquivo.filename:
            return None
        if Path(arquivo.filename).suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            raise ValueError("Envie uma foto JPG, PNG ou WebP de até 5 MB.")
        if arquivo.stream.seek(0, 2) > 5 * 1024 * 1024:
            raise ValueError("A foto deve ter no máximo 5 MB.")
        arquivo.stream.seek(0)
        try:
            with Image.open(arquivo.stream) as imagem:
                if imagem.format not in ("JPEG", "PNG", "WEBP") or imagem.width * imagem.height > 25_000_000:
                    raise ValueError("Foto inválida ou com resolução muito grande.")
                imagem.load()
                from PIL import ImageOps
                imagem = ImageOps.exif_transpose(imagem).convert("RGB")
                imagem.thumbnail((1600, 1600))
                pasta = Path(app.config["UPLOAD_FOLDER"])
                pasta.mkdir(parents=True, exist_ok=True)
                nome = uuid4().hex + ".jpg"
                imagem.save(pasta / nome, "JPEG", quality=88)
                return nome
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            raise ValueError("O arquivo enviado não é uma foto válida.") from None

    def remover_foto(nome):
        if nome and Path(nome).name == nome:
            (Path(app.config["UPLOAD_FOLDER"]) / nome).unlink(missing_ok=True)

    @app.route("/fotos/<nome>")
    def foto_animal(nome):
        return send_from_directory(app.config["UPLOAD_FOLDER"], nome)

    @app.errorhandler(413)
    def foto_grande(erro):
        return render_template("index.html", animais=banco.listar_animais(banco_atual()),
                               erro="Envie uma foto de até 5 MB."), 413

    # ======================================
    # EXIGIR ANIMAL
    # ======================================

    def exigir_animal(animal_id):

        animal = banco.buscar_animal(
            animal_id,
            banco_atual()
        )

        if animal is None:
            abort(404)

        return animal


    # ======================================
    # PÁGINA INICIAL + FILTROS
    # ======================================

    @app.route("/")
    def inicio():

        busca = request.args.get(
            "busca",
            ""
        ).strip()

        especie = request.args.get(
            "especie",
            ""
        ).strip()

        porte = request.args.get(
            "porte",
            ""
        ).strip()

        status = request.args.get(
            "status",
            ""
        ).strip()

        ordenar = request.args.get(
            "ordenar",
            "id"
        ).strip()


        try:

            animais = banco.filtrar_animais(
                busca=busca,
                especie=especie,
                porte=porte,
                status=status,
                ordenar=ordenar,
                caminho=banco_atual()
            )

            erro = None


        except ValueError:

            animais = banco.listar_animais(
                banco_atual()
            )

            erro = (
                "Um dos filtros informados "
                "é inválido."
            )


        filtros = {
            "busca": busca,
            "especie": especie,
            "porte": porte,
            "status": status,
            "ordenar": ordenar
        }


        return render_template(
            "index.html",
            animais=animais,
            filtros=filtros,
            erro=erro
        )


    # ======================================
    # CADASTRAR
    # ======================================

    @app.route(
        "/cadastro",
        methods=["POST"]
    )
    def cadastro():

        dados = ler_formulario()

        foto = None
        try:
            banco.validar_dados(**{k: dados[k] for k in ("nome", "especie", "idade", "porte")})
            banco.validar_contato(**{k: dados[k] for k in ("doador_nome", "doador_telefone", "localizacao")})
            foto = salvar_foto()
            banco.cadastrar_animal(
                foto=foto or "",
                **dados,
                caminho=banco_atual()
            )

        except ValueError as erro:
            remover_foto(foto)
            return formulario_invalido(str(erro))
        except Exception:
            remover_foto(foto)
            raise


        flash(
            f"{dados['nome']} foi cadastrado com sucesso!",
            "sucesso"
        )


        return redirect(
            url_for("inicio")
        )


    # ======================================
    # MARCAR COMO ADOTADO
    # ======================================

    @app.route(
        "/adotar/<int:animal_id>",
        methods=["POST"]
    )
    def adotar(animal_id):

        animal = exigir_animal(
            animal_id
        )


        banco.marcar_como_adotado(
            animal_id,
            banco_atual()
        )


        flash(
            f"{animal['nome']} foi marcado como adotado!",
            "sucesso"
        )


        return redirect(
            url_for("inicio")
        )


    # ======================================
    # EXCLUIR
    # ======================================

    @app.route(
        "/excluir/<int:animal_id>",
        methods=["POST"]
    )
    def excluir(animal_id):

        animal = exigir_animal(
            animal_id
        )


        banco.excluir_animal(
            animal_id,
            banco_atual()
        )


        remover_foto(animal.get("foto"))
        flash(
            f"{animal['nome']} foi excluído com sucesso.",
            "sucesso"
        )


        return redirect(
            url_for("inicio")
        )


    # ======================================
    # EDITAR
    # ======================================

    @app.route(
        "/editar/<int:animal_id>",
        methods=["POST"]
    )
    def editar(animal_id):

        animal = exigir_animal(animal_id)
        dados = ler_formulario()
        # Clientes antigos podem enviar apenas os campos originais.
        for campo in ("doador_nome", "doador_telefone", "localizacao"):
            if campo not in request.form:
                dados[campo] = animal[campo]


        foto = None
        try:
            banco.validar_dados(**{k: dados[k] for k in ("nome", "especie", "idade", "porte")})
            banco.validar_contato(**{k: dados[k] for k in ("doador_nome", "doador_telefone", "localizacao")})
            foto = salvar_foto()
            banco.editar_animal(
                animal_id,
                foto=foto,
                **dados,
                caminho=banco_atual()
            )

        except ValueError as erro:
            remover_foto(foto)
            return formulario_invalido(str(erro))
        except Exception:
            remover_foto(foto)
            raise
        if foto:
            remover_foto(animal.get("foto"))


        flash(
            f"Dados de {dados['nome']} atualizados com sucesso!",
            "sucesso"
        )


        return redirect(
            url_for("inicio")
        )


    # ======================================
    # ERRO 404
    # ======================================

    @app.errorhandler(404)
    def nao_encontrado(erro):

        return render_template(
            "index.html",

            animais=banco.listar_animais(
                banco_atual()
            ),

            erro=(
                "Animal ou página não encontrado. "
                "Confira a lista atualizada."
            )
        ), 404


    return app


# ======================================
# EXECUTAR APLICAÇÃO
# ======================================

if __name__ == "__main__":

    app = create_app()

    app.run(
        debug=True
    )
