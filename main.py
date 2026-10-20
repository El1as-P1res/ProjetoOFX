"""
Leitura de Arquivos OFX com Python - Atividade Prática
Aluno: José Elias Pires Jr - RA 26001935

Lê o arquivo extrato.ofx e exibe cada movimentação (data, valor e
descrição), a quantidade de movimentações e os totais de entradas,
saídas e saldo calculado.

Uso: python main.py [arquivo.ofx]
"""
import sys

from ofxparse import OfxParser


def ler_extrato(caminho):
    with open(caminho, "rb") as arquivo:
        ofx = OfxParser.parse(arquivo)
    return ofx.account.statement.transactions


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "extrato.ofx"

    transacoes = ler_extrato(caminho)

    entradas = 0
    saidas = 0

    print("=" * 40)
    print("           EXTRATO BANCÁRIO")
    print("=" * 40)

    for t in transacoes:

        print(f"Data      : {t.date.strftime('%d/%m/%Y')}")
        print(f"Valor     : R$ {t.amount:.2f}")
        print(f"Descrição : {t.memo}")
        print("-" * 40)

        if t.amount > 0:
            entradas += t.amount
        else:
            saidas += t.amount

    saldo = entradas + saidas

    print(f"Quantidade de movimentações: {len(transacoes)}")
    print("=" * 40)
    print(f"Entradas : R$ {entradas:.2f}")
    print(f"Saídas   : R$ {saidas:.2f}")
    print(f"Saldo    : R$ {saldo:.2f}")
    print("=" * 40)


if __name__ == "__main__":
    main()
