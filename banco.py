"""Operações SQLite do Sistema de Adoção.

Cada operação abre uma conexão, confirma a transação e fecha a conexão.
Os valores são passados com ?, separados do comando SQL.
"""

import sqlite3

from contextlib import contextmanager
from pathlib import Path


BANCO_PADRAO = Path(__file__).resolve().with_name("adocao.db")


# ======================================
# CONEXÃO
# ======================================

@contextmanager
def conectar(caminho=BANCO_PADRAO):

    conexao = sqlite3.connect(caminho)

    conexao.row_factory = sqlite3.Row

    try:

        with conexao:
            yield conexao

    finally:

        conexao.close()


# ======================================
# INICIALIZAR BANCO
# ======================================

def inicializar_banco(caminho=BANCO_PADRAO):

    with conectar(caminho) as conexao:

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS animais (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                nome TEXT NOT NULL
                    CHECK(length(trim(nome)) > 0),

                especie TEXT NOT NULL
                    CHECK(length(trim(especie)) > 0),

                idade INTEGER NOT NULL
                    CHECK(
                        typeof(idade) = 'integer'
                        AND idade >= 0
                    ),

                porte TEXT NOT NULL
                    CHECK(
                        porte IN (
                            'Pequeno',
                            'Médio',
                            'Grande'
                        )
                    ),

                status TEXT NOT NULL
                    DEFAULT 'Disponível'

                    CHECK(
                        status IN (
                            'Disponível',
                            'Adotado'
                        )
                    )

            )
        """)

        # Migração aditiva: mantém IDs, status e cadastros existentes.
        colunas = {linha["name"] for linha in conexao.execute("PRAGMA table_info(animais)")}
        for coluna in ("doador_nome", "doador_telefone", "localizacao", "foto"):
            if coluna not in colunas:
                conexao.execute(f"ALTER TABLE animais ADD COLUMN {coluna} TEXT NOT NULL DEFAULT ''")


# ======================================
# VALIDAÇÃO
# ======================================

def validar_dados(
    nome,
    especie,
    idade,
    porte
):

    nome = nome.strip()

    especie = especie.strip()

    porte = porte.strip()


    if not nome or not especie:

        raise ValueError(
            "Nome e espécie são obrigatórios."
        )


    if isinstance(idade, bool) or not isinstance(
        idade,
        (int, str)
    ):

        raise ValueError(
            "Idade deve ser um número inteiro."
        )


    idade = int(idade)


    if idade < 0:

        raise ValueError(
            "Idade não pode ser negativa."
        )


    if porte not in (
        "Pequeno",
        "Médio",
        "Grande"
    ):

        raise ValueError(
            "Porte inválido."
        )


    return (
        nome,
        especie,
        idade,
        porte
    )


# ======================================
# CADASTRAR
# ======================================

def cadastrar_animal(
    nome,
    especie,
    idade,
    porte,
    caminho=BANCO_PADRAO,
    doador_nome="",
    doador_telefone="",
    localizacao="",
    foto="",
):

    dados = validar_dados(
        nome,
        especie,
        idade,
        porte
    )


    with conectar(caminho) as conexao:

        cursor = conexao.execute(
            """
            INSERT INTO animais (
                nome,
                especie,
                idade,
                porte, doador_nome, doador_telefone, localizacao, foto
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (*dados, *validar_contato(doador_nome, doador_telefone, localizacao), foto)
        )


        return cursor.lastrowid


# ======================================
# LISTAR
# ======================================

def listar_animais(
    caminho=BANCO_PADRAO
):

    with conectar(caminho) as conexao:

        linhas = conexao.execute(
            """
            SELECT *
            FROM animais
            ORDER BY id
            """
        ).fetchall()


        return [
            dict(linha)
            for linha in linhas
        ]


# ======================================
# FILTRAR / BUSCAR
# ======================================

def filtrar_animais(
    busca="",
    especie="",
    porte="",
    status="",
    ordenar="id",
    caminho=BANCO_PADRAO
):

    consulta = """
        SELECT *
        FROM animais
        WHERE 1 = 1
    """

    parametros = []


    busca = busca.strip()

    especie = especie.strip()

    porte = porte.strip()

    status = status.strip()


    # ----------------------------------
    # BUSCAR POR NOME OU ESPÉCIE
    # ----------------------------------

    if busca:

        termo = f"%{busca}%"

        consulta += """
            AND (
                nome LIKE ?
                OR especie LIKE ?
            )
        """

        parametros.extend([
            termo,
            termo
        ])


    # ----------------------------------
    # FILTRAR ESPÉCIE
    # ----------------------------------

    if especie:

        consulta += """
            AND especie = ?
        """

        parametros.append(
            especie
        )


    # ----------------------------------
    # FILTRAR PORTE
    # ----------------------------------

    if porte:

        if porte not in (
            "Pequeno",
            "Médio",
            "Grande"
        ):

            raise ValueError(
                "Porte inválido."
            )


        consulta += """
            AND porte = ?
        """

        parametros.append(
            porte
        )


    # ----------------------------------
    # FILTRAR STATUS
    # ----------------------------------

    if status:

        if status not in (
            "Disponível",
            "Adotado"
        ):

            raise ValueError(
                "Status inválido."
            )


        consulta += """
            AND status = ?
        """

        parametros.append(
            status
        )


    # ----------------------------------
    # ORDENAÇÃO
    # ----------------------------------

    ordenacoes = {

        "id":
            "id ASC",

        "nome":
            "nome COLLATE NOCASE ASC",

        "idade":
            "idade ASC",

        "idade_desc":
            "idade DESC"

    }


    ordem_sql = ordenacoes.get(
        ordenar,
        "id ASC"
    )


    consulta += f"""
        ORDER BY {ordem_sql}
    """


    with conectar(caminho) as conexao:

        linhas = conexao.execute(
            consulta,
            parametros
        ).fetchall()


        return [
            dict(linha)
            for linha in linhas
        ]


# ======================================
# BUSCAR POR ID
# ======================================

def buscar_animal(
    animal_id,
    caminho=BANCO_PADRAO
):

    with conectar(caminho) as conexao:

        linha = conexao.execute(
            """
            SELECT *
            FROM animais
            WHERE id = ?
            """,
            (animal_id,)
        ).fetchone()


        return (
            dict(linha)
            if linha
            else None
        )


# ======================================
# EDITAR
# ======================================

def editar_animal(animal_id, nome, especie, idade, porte,
                  caminho=BANCO_PADRAO, doador_nome=None, doador_telefone=None,
                  localizacao=None, foto=None):
    dados = validar_dados(nome, especie, idade, porte)
    with conectar(caminho) as conexao:
        atual = conexao.execute("SELECT * FROM animais WHERE id = ?", (animal_id,)).fetchone()
        if atual is None:
            return 0
        contato = validar_contato(
            atual["doador_nome"] if doador_nome is None else doador_nome,
            atual["doador_telefone"] if doador_telefone is None else doador_telefone,
            atual["localizacao"] if localizacao is None else localizacao,
        )
        cursor = conexao.execute(
            """UPDATE animais SET nome=?, especie=?, idade=?, porte=?,
               doador_nome=?, doador_telefone=?, localizacao=?, foto=? WHERE id=?""",
            (*dados, *contato, atual["foto"] if foto is None else foto, animal_id),
        )
        return cursor.rowcount


# ======================================
# MARCAR COMO ADOTADO
# ======================================

def marcar_como_adotado(
    animal_id,
    caminho=BANCO_PADRAO
):

    with conectar(caminho) as conexao:

        cursor = conexao.execute(
            """
            UPDATE animais

            SET status = ?

            WHERE id = ?
            """,

            (
                "Adotado",
                animal_id
            )
        )


        return cursor.rowcount


# ======================================
# EXCLUIR
# ======================================

def excluir_animal(
    animal_id,
    caminho=BANCO_PADRAO
):

    with conectar(caminho) as conexao:

        cursor = conexao.execute(
            """
            DELETE FROM animais
            WHERE id = ?
            """,

            (animal_id,)
        )


        return cursor.rowcount

def validar_contato(doador_nome="", doador_telefone="", localizacao=""):
    import re
    nome, telefone, local = doador_nome.strip(), doador_telefone.strip(), localizacao.strip()
    if len(nome) > 120 or len(local) > 160 or len(telefone) > 40:
        raise ValueError("Nome do doador, telefone ou localização muito longos.")
    if telefone and (not re.fullmatch(r"[0-9+() .-]+", telefone)
                     or not 8 <= len(re.sub(r"\D", "", telefone)) <= 15):
        raise ValueError("Informe um telefone válido, com DDD.")
    return nome, telefone, local
