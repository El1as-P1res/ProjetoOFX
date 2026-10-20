"""
Desafio Extra - Gravação das movimentações OFX no PostgreSQL (linha de comando)
Aluno: José Elias Pires Jr - RA 26001935

Processo ETL:
  Extração      -> leitor_ofx.ler_transacoes()
  Transformação -> classificador.classificar() define tipo e categoria
  Carga         -> banco.inserir() grava na tabela "movimentacoes"

Desafio bônus: o FITID de cada transação fica em uma coluna UNIQUE e o
INSERT usa "ON CONFLICT DO NOTHING", então nada é gravado em duplicidade.

Uso: python importar_postgres.py [arquivo.ofx]
"""
import sys

import banco
from classificador import classificar, tipo
from leitor_ofx import ler_transacoes


def importar(arquivo):
    transacoes = ler_transacoes(arquivo)

    con = banco.conectar()
    cur = con.cursor()
    banco.criar_tabela(cur)

    inseridas = 0
    for t in transacoes:
        t["tipo"] = tipo(t["valor"])
        t["categoria"] = classificar(t["descricao"], t["valor"])
        t["nova"] = banco.inserir(cur, t)
        inseridas += t["nova"]

    con.commit()
    resumo = banco.resumo_por_categoria(cur)
    cur.close()
    con.close()

    return transacoes, inseridas, resumo


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "extrato.ofx"

    transacoes, inseridas, resumo = importar(caminho)

    print(f"Transações no arquivo : {len(transacoes)}")
    print(f"Inseridas             : {inseridas}")
    print(f"Ignoradas (duplicadas): {len(transacoes) - inseridas}\n")

    print("Classificação (todas as movimentações do banco):")
    for categoria, qtd, total in resumo:
        print(f"  {categoria:<24} {qtd:>3} mov.   R$ {total:>12.2f}")
