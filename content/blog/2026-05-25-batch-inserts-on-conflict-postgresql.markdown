---
title: "Batch inserts e ON CONFLICT no PostgreSQL: saindo do single-row em consumers de alta frequência"
draft: true
date: 2026-05-25T00:00:00.000Z
description: "Por que single-row inserts matam performance em alta frequência, como estruturar batch inserts corretamente, e a semântica do ON CONFLICT DO NOTHING vs DO UPDATE — com benchmarks reais."
comments: true
keywords: [
  "PostgreSQL",
  "batch insert",
  "ON CONFLICT",
  "upsert",
  "INSERT ON CONFLICT DO NOTHING",
  "INSERT ON CONFLICT DO UPDATE",
  "performance PostgreSQL",
  "bulk insert",
  "UNNEST",
  "consumer alta frequência",
  "como fazer batch insert postgresql",
  "como fazer upsert postgresql",
  "diferença DO NOTHING DO UPDATE"
]
tags:
  - postgresql
  - performance
  - batch
  - sql
---

# Introdução

Um consumer que lê de fila e grava um registro por vez no PostgreSQL é um erro que só aparece quando dá errado. Em baixa frequência funciona bem: é código simples, é fácil de entender, cada evento é atômico. Em alta frequência, vira o gargalo do banco inteiro.

No post anterior da série, contei de um incidente no Aurora onde um consumer que escrevia no banco evento-a-evento estava multiplicando a carga de escrita. Aqui vou descer ao nível de implementação: por que isso dói, como refatorar pra batch com `INSERT ... ON CONFLICT`, e onde moram as armadilhas.

# Por que single-row inserts matam em alta frequência

Toda vez que você faz um `INSERT` único, o PostgreSQL paga um pedágio fixo:

- **Round-trip de rede** entre app e banco
- **Parse e planning** da query (aliviado por `pg_prepare` se você usar, mas ainda assim um custo)
- **Adquirir e liberar lock** no heap e no índice
- **WAL write** separado pra aquele registro
- **Commit** individual se você não agrupou em transação

Em baixa frequência (dezenas por segundo) esse pedágio é invisível. Em alta frequência (milhares por segundo), esses custos viram a maior parte do trabalho. O banco passa mais tempo na cerimônia do insert do que gravando os dados.

Um lote de 500 registros em um único `INSERT` paga esse pedágio **uma vez**. O `INSERT` em si fica maior, claro, mas a razão custo-fixo/trabalho-útil melhora drasticamente.

# Estruturando o batch insert

Duas formas de montar um batch no PostgreSQL:

**Forma 1: VALUES com múltiplas linhas**

```sql
INSERT INTO events (tenant_id, event_type, payload, received_at)
VALUES
  ($1, $2, $3, $4),
  ($5, $6, $7, $8),
  ($9, $10, $11, $12);
```

Simples, legível, funciona. Desvantagem: se você precisa parametrizar 500 linhas com 4 colunas cada, são 2000 placeholders. O driver do cliente começa a reclamar, e o limite máximo de parâmetros do PostgreSQL é 65.535. Viável pra batches médios, mas não é a forma mais limpa.

**Forma 2: UNNEST de arrays**

```sql
INSERT INTO events (tenant_id, event_type, payload, received_at)
SELECT * FROM unnest(
  $1::uuid[],
  $2::text[],
  $3::jsonb[],
  $4::timestamptz[]
);
```

Aqui você passa 4 parâmetros, independente do tamanho do batch — cada um é um array. O driver serializa tudo em uma única chamada. É mais eficiente pra batches grandes e é a forma que a gente preferiu na refatoração.

Em Node.js, com `pg`, fica mais ou menos assim:

```javascript
const tenantIds = events.map(e => e.tenantId);
const types = events.map(e => e.type);
const payloads = events.map(e => JSON.stringify(e.payload));
const receivedAts = events.map(e => e.receivedAt);

await client.query(
  `INSERT INTO events (tenant_id, event_type, payload, received_at)
   SELECT * FROM unnest($1::uuid[], $2::text[], $3::jsonb[], $4::timestamptz[])`,
  [tenantIds, types, payloads, receivedAts]
);
```

# ON CONFLICT: DO NOTHING vs DO UPDATE

Quando o consumer pode receber eventos duplicados (e numa fila à-la-SQS com at-least-once, sempre pode), você precisa decidir o que fazer em colisão de chave única.

**DO NOTHING** — ignora silenciosamente:

```sql
INSERT INTO events (event_id, tenant_id, payload)
VALUES ($1, $2, $3)
ON CONFLICT (event_id) DO NOTHING;
```

Uso: quando o dado mais novo não vale mais que o mais velho. Eventos imutáveis, logs append-only, eventos idempotentes. **Na maioria dos consumers de fila, é isso que você quer.**

**DO UPDATE** — faz upsert:

```sql
INSERT INTO contacts (email, name, updated_at)
VALUES ($1, $2, now())
ON CONFLICT (email) DO UPDATE
  SET name = EXCLUDED.name,
      updated_at = EXCLUDED.updated_at
  WHERE contacts.updated_at < EXCLUDED.updated_at;
```

Uso: quando o registro mais novo sobrepõe o antigo. Note a cláusula `WHERE` na ponta — é o que garante que um evento atrasado não sobrescreva um evento mais recente que já chegou antes. Sem isso, você cria inconsistência temporal.

O `EXCLUDED` é uma pseudo-tabela que representa a linha que tentou entrar no `INSERT`. Fundamental pra diferenciar "o que está no banco" de "o que eu estou tentando gravar".

# Armadilha: ON CONFLICT em batch com duplicatas dentro do próprio batch

Essa pegou a gente de surpresa. Em um batch de 500 eventos, o consumer pode ter 2 ou 3 com a mesma chave (a fila entregou duplicatas no mesmo pull). O `ON CONFLICT` só age contra o que já está no heap — dentro do batch, ele não ajuda. O resultado é um erro:

```
ERROR: ON CONFLICT DO UPDATE command cannot affect row a second time
```

Solução: deduplicate no cliente antes de mandar pro banco.

```javascript
const seen = new Set();
const deduped = events.filter(e => {
  if (seen.has(e.eventId)) return false;
  seen.add(e.eventId);
  return true;
});
```

Barato, defensivo, resolve.

# Benchmarks

Teste sintético, mesma carga total de 10.000 eventos, mesmo schema, mesma tabela com 50M registros, Aurora PostgreSQL 13.18. Três cenários:

| Estratégia                            | Tempo total | Inserts/seg | CPU writer |
| ------------------------------------- | ----------- | ----------- | ---------- |
| Single-row INSERT                     | 47s         | ~213        | 78%        |
| Batch de 100 (UNNEST + ON CONFLICT)   | 3.1s        | ~3.225      | 41%        |
| Batch de 500 (UNNEST + ON CONFLICT)   | 1.4s        | ~7.143      | 34%        |

O salto de single-row pra batch de 100 é o que mais pesa. De 100 pra 500 o retorno é decrescente: você ganha throughput, mas aumenta o tamanho de lock e o custo de erro (se o batch falhar, 500 eventos precisam ser reprocessados).

# Qual batch size escolher

Sem regra universal, mas orientação prática:

- **50–100** — conservador, bom pra tabelas com muita contenção de lock.
- **200–500** — o sweet spot pra a maioria dos consumers. Usamos 500.
- **1000+** — só se você tem tabela dedicada, sem contenção, e tolera latência de processamento maior.

Lembra que batch size é troca entre throughput e latência. Um consumer que junta 500 eventos antes de gravar tem latência p99 pior que um que grava de 50 em 50. Se seu caso é realtime, isso importa.

# Lições aprendidas

- **Nunca nasça em single-row.** Qualquer consumer de fila deveria ter batch desde o dia um. É mais código, mas é o código certo.
- **Dedup no cliente antes do batch.** `ON CONFLICT` não ajuda contra duplicatas internas ao batch.
- **Escolha conscientemente DO NOTHING vs DO UPDATE.** Os dois são corretos, mas pra problemas diferentes. Se você está em dúvida, `DO NOTHING` é o default mais seguro.
- **Na cláusula de UPDATE, proteja contra out-of-order.** Inclua um `WHERE` que compara timestamp. Sem isso, evento atrasado sobrescreve evento recente — e você vai descobrir isso da pior forma.
- **Benchmark no seu ambiente.** Os números acima servem pra ordem de grandeza. Tempo absoluto depende de schema, índices, concorrência e instância.

**💬 Qual batch size você usa nos seus consumers?**

Já teve problema com duplicata dentro do batch? Conta aí — esse tipo de aprendizado no setor raramente é documentado.
