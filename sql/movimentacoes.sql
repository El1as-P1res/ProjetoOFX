-- Tabela pedida na atividade
CREATE TABLE IF NOT EXISTS movimentacoes (
    id SERIAL PRIMARY KEY,
    data_movimentacao DATE,
    valor NUMERIC(15,2),
    descricao VARCHAR(255)
);

-- Desafio bônus: identificador único da transação no OFX (FITID)
ALTER TABLE movimentacoes ADD COLUMN IF NOT EXISTS fitid VARCHAR(100) UNIQUE;

-- Classificação
ALTER TABLE movimentacoes ADD COLUMN IF NOT EXISTS tipo VARCHAR(10);
ALTER TABLE movimentacoes ADD COLUMN IF NOT EXISTS categoria VARCHAR(50);

-- Consultas para validar no DBeaver
SELECT * FROM movimentacoes ORDER BY data_movimentacao;

SELECT categoria, COUNT(*) AS quantidade, SUM(valor) AS total
FROM movimentacoes
GROUP BY categoria
ORDER BY total DESC;
