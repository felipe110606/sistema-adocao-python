"""Operações SQLite do Sistema de Adoção.

Cada operação abre uma conexão, confirma a transação e fecha a conexão.
Os valores são passados com ?, separados do comando SQL.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

BANCO_PADRAO = Path(__file__).resolve().with_name("adocao.db")


@contextmanager
def conectar(caminho=BANCO_PADRAO):
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    try:
        with conexao:
            yield conexao
    finally:
        conexao.close()


def inicializar_banco(caminho=BANCO_PADRAO):
    with conectar(caminho) as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS animais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL CHECK(length(trim(nome)) > 0),
                especie TEXT NOT NULL CHECK(length(trim(especie)) > 0),
                idade INTEGER NOT NULL CHECK(typeof(idade) = 'integer' AND idade >= 0),
                porte TEXT NOT NULL CHECK(porte IN ('Pequeno', 'Médio', 'Grande')),
                status TEXT NOT NULL DEFAULT 'Disponível'
                    CHECK(status IN ('Disponível', 'Adotado'))
            )
        """)


def validar_dados(nome, especie, idade, porte):
    nome, especie, porte = nome.strip(), especie.strip(), porte.strip()
    if not nome or not especie:
        raise ValueError("Nome e espécie são obrigatórios.")
    if isinstance(idade, bool) or not isinstance(idade, (int, str)):
        raise ValueError("Idade deve ser um número inteiro.")
    idade = int(idade)
    if idade < 0 or porte not in ("Pequeno", "Médio", "Grande"):
        raise ValueError("Informe idade não negativa e porte válido.")
    return nome, especie, idade, porte


def cadastrar_animal(nome, especie, idade, porte, caminho=BANCO_PADRAO):
    dados = validar_dados(nome, especie, idade, porte)
    with conectar(caminho) as conexao:
        cursor = conexao.execute(
            "INSERT INTO animais (nome, especie, idade, porte) VALUES (?, ?, ?, ?)",
            dados
        )
        return cursor.lastrowid


def listar_animais(caminho=BANCO_PADRAO):
    with conectar(caminho) as conexao:
        linhas = conexao.execute("SELECT * FROM animais ORDER BY id").fetchall()
        return [dict(linha) for linha in linhas]


def buscar_animal(animal_id, caminho=BANCO_PADRAO):
    with conectar(caminho) as conexao:
        linha = conexao.execute(
            "SELECT * FROM animais WHERE id = ?", (animal_id,)
        ).fetchone()
        return dict(linha) if linha else None


def editar_animal(animal_id, nome, especie, idade, porte, caminho=BANCO_PADRAO):
    dados = validar_dados(nome, especie, idade, porte)
    with conectar(caminho) as conexao:
        cursor = conexao.execute(
            "UPDATE animais SET nome = ?, especie = ?, idade = ?, porte = ? WHERE id = ?",
            (*dados, animal_id)
        )
        return cursor.rowcount


def marcar_como_adotado(animal_id, caminho=BANCO_PADRAO):
    with conectar(caminho) as conexao:
        cursor = conexao.execute(
            "UPDATE animais SET status = ? WHERE id = ?", ("Adotado", animal_id)
        )
        return cursor.rowcount


def excluir_animal(animal_id, caminho=BANCO_PADRAO):
    with conectar(caminho) as conexao:
        cursor = conexao.execute("DELETE FROM animais WHERE id = ?", (animal_id,))
        return cursor.rowcount
