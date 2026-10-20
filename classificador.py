"""
Rotina de classificação das movimentações.

Cada movimentação recebe uma CATEGORIA com base em palavras-chave da
descrição. A primeira regra que encontrar uma palavra vence. Se nenhuma
regra servir, a movimentação vira "Outras entradas" ou "Outras saídas".

Para acrescentar uma categoria, basta incluir uma linha em REGRAS.

Rodando este arquivo diretamente, ele reclassifica todas as
movimentações que já estão no PostgreSQL:
    python classificador.py
"""
import re
import unicodedata

REGRAS = [
    ("Salário",               ["SALARIO", "PROVENTOS", "FOLHA PGTO"]),
    ("Recebimentos",          ["PIX CLIENTE", "PIX RECEBIDO", "TED RECEBIDA",
                               "DOC RECEBIDO", "DEPOSITO", "RECEBIMENTO"]),
    ("Moradia",               ["ENERGIA", "LUZ", "AGUA", "SABESP", "ALUGUEL",
                               "CONDOMINIO", "GAS", "IPTU"]),
    ("Telecom e Assinaturas", ["INTERNET", "TELEFONE", "CELULAR", "VIVO", "CLARO",
                               "TIM", "NETFLIX", "SPOTIFY", "STREAMING"]),
    ("Alimentação",           ["SUPERMERCADO", "MERCADO", "PADARIA", "RESTAURANTE",
                               "IFOOD", "LANCHONETE", "ACOUGUE"]),
    ("Transporte",            ["POSTO", "COMBUSTIVEL", "UBER", "99APP", "ESTACIONAMENTO",
                               "PEDAGIO", "ONIBUS"]),
    ("Saúde",                 ["FARMACIA", "DROGARIA", "HOSPITAL", "CLINICA",
                               "PLANO DE SAUDE", "LABORATORIO"]),
    ("Educação",              ["FACULDADE", "MENSALIDADE", "ESCOLA", "CURSO", "LIVRARIA"]),
    ("Tarifas bancárias",     ["TARIFA", "JUROS", "IOF", "ANUIDADE", "CESTA"]),
    ("Impostos",              ["DARF", "IPVA", "GPS", "DAS", "IMPOSTO"]),
]


def normalizar(texto):
    """Maiúsculas e sem acentos: 'Água' -> 'AGUA'."""
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.upper()


def classificar(descricao, valor):
    desc = normalizar(descricao)

    for categoria, palavras in REGRAS:
        for palavra in palavras:
            # \b = palavra inteira ("GAS" não casa com "GASTO")
            if re.search(rf"\b{re.escape(palavra)}\b", desc):
                return categoria

    return "Outras entradas" if valor > 0 else "Outras saídas"


def tipo(valor):
    return "Entrada" if valor > 0 else "Saída"


def reclassificar_banco():
    """Rotina: aplica as regras em todas as movimentações gravadas."""
    import banco

    con = banco.conectar()
    cur = con.cursor()
    banco.criar_tabela(cur)

    cur.execute("SELECT id, descricao, valor FROM movimentacoes")
    registros = cur.fetchall()

    for id_, descricao, valor in registros:
        cur.execute(
            "UPDATE movimentacoes SET categoria = %s, tipo = %s WHERE id = %s",
            (classificar(descricao, valor), tipo(valor), id_),
        )

    con.commit()

    print(f"{len(registros)} movimentações classificadas.\n")
    for categoria, qtd, total in banco.resumo_por_categoria(cur):
        print(f"{categoria:<24} {qtd:>3} mov.   R$ {total:>12.2f}")

    cur.close()
    con.close()


if __name__ == "__main__":
    reclassificar_banco()
