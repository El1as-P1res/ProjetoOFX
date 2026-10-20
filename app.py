"""
Sistema de Upload de Extratos OFX
Aluno: José Elias Pires Jr - RA 26001935

Página web onde o usuário envia um arquivo .ofx. O sistema:
  1. lê as transações do arquivo;
  2. classifica cada uma por categoria;
  3. grava no PostgreSQL (sem duplicar);
  4. mostra a classificação do arquivo enviado e o resumo geral do banco.

Uso:  python app.py   ->  abrir http://localhost:5000
"""
import io

from flask import Flask, redirect, render_template, request, url_for

import banco
from importar_postgres import importar

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # até 5 MB


def resumir(transacoes):
    """Totais por categoria apenas do arquivo enviado."""
    categorias = {}
    for t in transacoes:
        c = categorias.setdefault(t["categoria"], {"qtd": 0, "total": 0})
        c["qtd"] += 1
        c["total"] += t["valor"]
    return sorted(categorias.items(), key=lambda item: item[1]["total"], reverse=True)


@app.route("/")
def index():
    return render_template("index.html", erro=request.args.get("erro"))


@app.route("/upload", methods=["POST"])
def upload():
    arquivo = request.files.get("arquivo")

    if not arquivo or arquivo.filename == "":
        return redirect(url_for("index", erro="Selecione um arquivo."))

    if not arquivo.filename.lower().endswith(".ofx"):
        return redirect(url_for("index", erro="O arquivo precisa ter extensão .ofx."))

    try:
        conteudo = io.BytesIO(arquivo.read())
        transacoes, inseridas, resumo_banco = importar(conteudo)
    except Exception as e:  # arquivo inválido ou falha no banco
        return redirect(url_for("index", erro=f"Não foi possível processar o arquivo: {e}"))

    entradas = sum(t["valor"] for t in transacoes if t["valor"] > 0)
    saidas = sum(t["valor"] for t in transacoes if t["valor"] <= 0)

    return render_template(
        "resultado.html",
        nome_arquivo=arquivo.filename,
        transacoes=transacoes,
        inseridas=inseridas,
        duplicadas=len(transacoes) - inseridas,
        entradas=entradas,
        saidas=saidas,
        saldo=entradas + saidas,
        resumo_arquivo=resumir(transacoes),
        resumo_banco=resumo_banco,
    )


@app.route("/classificacao")
def classificacao():
    """Tudo o que já está gravado no banco, classificado."""
    con = banco.conectar()
    cur = con.cursor()
    banco.criar_tabela(cur)
    con.commit()
    movimentacoes = banco.listar(cur)
    resumo = banco.resumo_por_categoria(cur)
    cur.close()
    con.close()
    return render_template("classificacao.html", movimentacoes=movimentacoes, resumo=resumo)


@app.template_filter("reais")
def reais(valor):
    """1234.5 -> R$ 1.234,50"""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
