"""
Extração: lê um arquivo OFX e devolve as transações em uma lista de
dicionários simples, prontos para gravar no banco.
"""
from ofxparse import OfxParser


def ler_transacoes(arquivo):
    """arquivo: caminho (str) ou objeto de arquivo aberto em modo binário."""
    if isinstance(arquivo, str):
        with open(arquivo, "rb") as f:
            ofx = OfxParser.parse(f)
    else:
        ofx = OfxParser.parse(arquivo)

    transacoes = []

    for t in ofx.account.statement.transactions:
        data = t.date.date()
        valor = t.amount
        descricao = (t.memo or t.payee or "").strip()[:255]

        transacoes.append({
            "data": data,
            "valor": valor,
            "descricao": descricao,
            # FITID = identificador único da transação dado pelo banco
            "fitid": t.id or f"{data}|{valor}|{descricao}",
        })

    return transacoes
