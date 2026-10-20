"""
Acesso ao PostgreSQL: conexão, criação da tabela, gravação e consultas.
As credenciais ficam no arquivo .env (que não vai para o GitHub).
"""
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def conectar():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        database=os.getenv("PG_DATABASE", "postgres"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", ""),
        port=int(os.getenv("PG_PORT", "5432")),
        sslmode=os.getenv("PG_SSLMODE", "prefer"),  # Neon: use "require"
    )


def criar_tabela(cur):
    # Tabela pedida na atividade
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id SERIAL PRIMARY KEY,
            data_movimentacao DATE,
            valor NUMERIC(15,2),
            descricao VARCHAR(255)
        );
    """)
    # Colunas extras: FITID (evita duplicadas), tipo e categoria (classificação)
    cur.execute("ALTER TABLE movimentacoes ADD COLUMN IF NOT EXISTS fitid VARCHAR(100) UNIQUE;")
    cur.execute("ALTER TABLE movimentacoes ADD COLUMN IF NOT EXISTS tipo VARCHAR(10);")
    cur.execute("ALTER TABLE movimentacoes ADD COLUMN IF NOT EXISTS categoria VARCHAR(50);")


def inserir(cur, t):
    """Grava uma transação. Devolve True se inseriu, False se já existia."""
    cur.execute("""
        INSERT INTO movimentacoes
            (data_movimentacao, valor, descricao, fitid, tipo, categoria)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (fitid) DO NOTHING
    """, (t["data"], t["valor"], t["descricao"], t["fitid"], t["tipo"], t["categoria"]))
    return cur.rowcount == 1


def resumo_por_categoria(cur):
    cur.execute("""
        SELECT categoria, COUNT(*), SUM(valor)
        FROM movimentacoes
        GROUP BY categoria
        ORDER BY SUM(valor) DESC
    """)
    return cur.fetchall()


def listar(cur):
    cur.execute("""
        SELECT data_movimentacao, descricao, valor, tipo, categoria
        FROM movimentacoes
        ORDER BY data_movimentacao, id
    """)
    return cur.fetchall()
