# ProjetoOFX — Leitura, Classificação e Upload de Extratos OFX

**Aluno:** José Elias Pires Jr  
**RA:** 26001935

Aplicação em Python que lê extratos bancários no formato **OFX** (Open Financial Exchange), grava as movimentações no **PostgreSQL**, **classifica** cada uma por categoria e oferece um **sistema web de upload** que mostra a classificação.

É um processo ETL completo:

| Etapa | O que acontece | Arquivo |
|---|---|---|
| Extração | lê as transações do arquivo OFX | `leitor_ofx.py` |
| Transformação | define tipo (Entrada/Saída) e categoria | `classificador.py` |
| Carga | grava no PostgreSQL sem duplicar | `banco.py` |

## Estrutura

```
ProjetoOFX/
├── main.py                  # atividade prática: exibe o extrato e os totais
├── leitor_ofx.py            # extração: lê o OFX
├── classificador.py         # rotina de classificação (regras por palavra-chave)
├── banco.py                 # conexão e consultas no PostgreSQL
├── importar_postgres.py     # grava um OFX no banco pela linha de comando
├── app.py                   # sistema web de upload (Flask)
├── templates/               # páginas HTML do sistema
├── extrato.ofx              # extrato de exemplo (janeiro)
├── extrato_fevereiro.ofx    # extrato de exemplo (fevereiro)
├── sql/movimentacoes.sql    # script da tabela e consultas para o DBeaver
├── requirements.txt
├── .env.example             # modelo das credenciais do banco
└── .gitignore
```

## Instalação

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha com os dados do seu PostgreSQL (local ou Neon; no Neon use `PG_SSLMODE=require`). A tabela é criada automaticamente.

## 1. Atividade prática — exibir o extrato

```bash
python main.py
```

```
Data      : 05/01/2026
Valor     : R$ 1500.00
Descrição : PIX CLIENTE
----------------------------------------
...
Quantidade de movimentações: 5
Entradas : R$ 4700.00
Saídas   : R$ -746.40
Saldo    : R$ 3953.60
```

## 2. Jogar os dados no PostgreSQL

```bash
python importar_postgres.py extrato.ofx
```

```
Transações no arquivo : 5
Inseridas             : 5
Ignoradas (duplicadas): 0

Classificação (todas as movimentações do banco):
  Salário                    1 mov.   R$      3200.00
  Recebimentos               1 mov.   R$      1500.00
  Telecom e Assinaturas      1 mov.   R$       -75.50
  Moradia                    1 mov.   R$      -250.00
  Alimentação                1 mov.   R$      -420.90
```

**Sem duplicadas:** cada transação do OFX tem um código único dado pelo banco (FITID). Ele fica numa coluna `UNIQUE` e o `INSERT` usa `ON CONFLICT (fitid) DO NOTHING`. Rodando de novo o mesmo arquivo: `Inseridas: 0 / Ignoradas (duplicadas): 5`.

Validação no **DBeaver**: consultas prontas em `sql/movimentacoes.sql`.

## 3. Rotina de classificação

`classificador.py` procura palavras-chave na descrição (sem diferenciar maiúsculas e acentos, e só palavras inteiras) e define a categoria:

| Categoria | Exemplos de palavras-chave |
|---|---|
| Salário | SALARIO, PROVENTOS |
| Recebimentos | PIX CLIENTE, PIX RECEBIDO, TED RECEBIDA, DEPOSITO |
| Moradia | ENERGIA, AGUA, ALUGUEL, CONDOMINIO |
| Telecom e Assinaturas | INTERNET, CELULAR, NETFLIX, SPOTIFY |
| Alimentação | SUPERMERCADO, PADARIA, RESTAURANTE, IFOOD |
| Transporte | POSTO, COMBUSTIVEL, UBER, PEDAGIO |
| Saúde | FARMACIA, DROGARIA, HOSPITAL |
| Educação | FACULDADE, MENSALIDADE, CURSO |
| Tarifas bancárias | TARIFA, JUROS, IOF, ANUIDADE |
| Impostos | DARF, IPVA, DAS |
| Outras entradas / Outras saídas | quando nenhuma regra se aplica |

A classificação é feita automaticamente na importação. Para reclassificar tudo o que já está no banco (por exemplo, depois de acrescentar uma regra):

```bash
python classificador.py
```

## 4. Sistema de upload

```bash
python app.py
```

Abra **http://localhost:5000**, escolha um arquivo `.ofx` e clique em **Enviar e classificar**. O sistema:

1. valida o arquivo (só aceita `.ofx`);
2. lê e classifica as movimentações;
3. grava no PostgreSQL, ignorando as que já existem;
4. mostra os totais (entradas, saídas, saldo), a classificação por categoria do arquivo enviado, a lista de movimentações e o resumo geral do banco.

A página **Ver banco** (`/classificacao`) mostra todas as movimentações já gravadas, com o resumo por categoria.

Exemplo com `extrato_fevereiro.ofx`:

| Descrição | Categoria |
|---|---|
| PIX RECEBIDO CLIENTE ABC | Recebimentos |
| ALUGUEL FEVEREIRO | Moradia |
| DROGARIA SAO PAULO | Saúde |
| POSTO SHELL COMBUSTIVEL | Transporte |
| NETFLIX.COM | Telecom e Assinaturas |
| MENSALIDADE FACULDADE | Educação |
| SALARIO | Salário |
| UBER DO BRASIL | Transporte |
| TARIFA PACOTE SERVICOS | Tarifas bancárias |
| TRANSFERENCIA ENVIADA | Outras saídas |
