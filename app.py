from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Armazenamento temporário: SQLite será a próxima etapa.
animais = []


def ler_formulario():
    nome = request.form.get("nome", "").strip()
    especie = request.form.get("especie", "").strip()
    porte = request.form.get("porte", "").strip()
    try:
        idade = int(request.form.get("idade", ""))
    except ValueError:
        return None
    if not nome or not especie or idade < 0 or porte not in ("Pequeno", "Médio", "Grande"):
        return None
    return {"nome": nome, "especie": especie, "idade": idade, "porte": porte}


def formulario_invalido():
    return render_template(
        "index.html", animais=animais,
        erro="Preencha nome, espécie, idade inteira não negativa e um porte válido."
    ), 400


@app.route("/")
def inicio():
    return render_template("index.html", animais=animais)


@app.route("/cadastro", methods=["POST"])
def cadastro():
    animal = ler_formulario()
    if animal is None:
        return formulario_invalido()
    animal["status"] = "Disponível"
    animais.append(animal)
    return redirect(url_for("inicio"))


@app.route("/adotar/<int:indice>", methods=["POST"])
def adotar(indice):
    if 0 <= indice < len(animais):
        animais[indice]["status"] = "Adotado"
    return redirect(url_for("inicio"))


@app.route("/excluir/<int:indice>", methods=["POST"])
def excluir(indice):
    if 0 <= indice < len(animais):
        animais.pop(indice)
    return redirect(url_for("inicio"))


@app.route("/editar/<int:indice>", methods=["POST"])
def editar(indice):
    if 0 <= indice < len(animais):
        dados = ler_formulario()
        if dados is None:
            return formulario_invalido()
        # Só altera o animal depois que todos os campos são válidos.
        animais[indice].update(dados)
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)
