---
title: "Crise de performance no Aurora PostgreSQL: o que aprendi apagando incêndio ao vivo"
draft: false
date: 2026-05-24T00:00:00.000Z
description: "Um incidente real no Aurora PostgreSQL: load spikes, sequential scans em tabelas grandes, índices mortos e inserts single-row em alta frequência. Como diagnosticamos em minutos e quais ações reverteram o quadro."
comments: true
keywords: [
  "Aurora PostgreSQL",
  "performance",
  "incidente",
  "sequential scan",
  "dead indexes",
  "batch insert",
  "PostgreSQL 13",
  "pg_stat_statements",
  "pg_stat_user_indexes",
  "AWS RDS",
  "como diagnosticar lentidão postgresql",
  "como remover indexes nao usados postgresql",
  "como reduzir CPU aurora"
]
tags:
  - postgresql
  - aurora
  - performance
  - incidente
  - aws
---

<img id="image-custom" src="https://i.ytimg.com/vi/l7IpsIzMa6E/maxresdefault.jpg" alt="" />
<p id="image-legend">AWS Aurora</p>

# Introdução

Ninguém planeja uma crise de performance. Ela chega numa quarta-feira de manhã, quando o dashboard fica vermelho e os alertas começam a apitar. Foi mais ou menos assim que começou uma das crises mais instrutivas que atravessei em um Aurora Cluster PostgreSQL 13.18, e o que quero contar aqui não é o "fizemos tudo certo", mas a ordem real em que apaguei o fogo, o que funcionou de primeira e o que eu não tinha mapeado direito antes.

Na Harmo, o core transacional roda em Cluster Aurora PostgreSQL, single writer numa instância **db.r8g.4xlarge** (16 vCPU, 128 GB de RAM), storage I/O-Optimized e uma reader **db.r8g.4xlarge**. A plataforma processa +10 milhões de pesquisas e +300k avaliações públicas por mês, e cada uma toca o banco mais de uma vez: avaliação registrada, pesquisa enviada, pesquisa respondida, e-mail aberto, webhook de fornecedor. Quando esse fluxo degrada, a plataforma inteira sente. Mesmo que raro, com crescimento pode acontecer.

# O sintoma

O primeiro sinal foi CPU de writer subindo de um patamar de 35–45% pra beirar 90% de forma sustentada. Commit latency acompanhou: o p95 de gravação subiu de dezenas de milissegundos pra mais de um segundo. Connections ativas também: o que costumava ficar em torno de 120 foi pra 380 em 15 minutos. Não usamos proxy na frente do banco. Estamos estudando usarmos [**prest**](https://github.com/prest/prest).

Três sintomas simultâneos quase nunca têm uma única causa. Eu sabia disso, mas o instinto inicial foi buscar a bala de prata, provavelmente uma query nova de uma feature recém-deployada. Gastei uns cinco minutos olhando a timeline de deploys antes de aceitar que não era isso e partir pra investigação sistêmica.

# Primeira hora: localizando a dor

Comecei pelo óbvio:

```sql
SELECT query, calls, total_exec_time, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

Três coisas saltaram:

1. Uma tabela grande que fazia `INSERT` em alta frequência, um registro por vez, disparado por um consumer que processava eventos vindos do SES.
2. Uma query de leitura recorrente estava em `Seq Scan` num relacionamento de centenas de milhões de linhas, índice existia, mas o planner não usava.
3. Vários índices apareciam como ativos mas com zero uso em 30 dias.

Pra confirmar a terceira hipótese:

```sql
SELECT schemaname, relname, indexrelname, idx_scan, pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

O resultado: 18 índices com `idx_scan = 0` nos últimos 30 dias, alguns com mais de 2GB cada. Índices não lidos ainda são escritos em toda operação de `INSERT`/`UPDATE`/`DELETE`. Ou seja: write amplification gratuita.

# As três causas se reforçando

Isso não era um problema, eram três problemas compostos:

- **Write amplification** por índices mortos encarecendo cada insert.
- **Inserts single-row de alta frequência** multiplicando round-trips, parse, planning e WAL por registro.
- **Sequential scan** recorrente consumindo CPU de leitura enquanto o banco já sofria com escrita.

Cada um sozinho seria digerível. Os três juntos explicavam o pico simultâneo de CPU, latência e conexões.

# A ordem das ações

Primeira questão foi conter acessos e controles de comunicação com clientes. Depois veio a tentação de uma crise: atacar tudo ao mesmo tempo. Errado. Cada ação precisa ter rollback possível e janela de verificação. Fiz assim:

**1. Terminar conexões antigas em idle-in-transaction**

Alívio imediato. Tinha dezenas de conexões penduradas há mais de 30 minutos:

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '10 minutes';
```

Isso sozinho tirou 40% das conexões ativas e deu fôlego pra investigar com mais calma.

**2. Drop dos 18 índices mortos**

Em ambiente de produção quente, `DROP INDEX CONCURRENTLY` pra evitar lock. Um de cada vez, monitorando. Cada drop reduziu write amplification das tabelas afetadas. CPU começou a ceder.

```sql
DROP INDEX CONCURRENTLY IF EXISTS idx_some_unused_composite;
```

**3. Índice cirúrgico na tabela grande**

A query de leitura fazia `Seq Scan` porque o índice existente era em uma coluna sozinha, e o planner optava por varrer. Criei o índice composto certo, também com `CONCURRENTLY`:

```sql
CREATE INDEX CONCURRENTLY idx_tablex_namey_lookup
  ON tablex_namey_flowz (tenant_id, status, created_at DESC);
```

Depois disso, `EXPLAIN ANALYZE` da query problemática caiu de 4.2 segundos pra 38 milissegundos.

**4. Refatoração do consumer SES pra batch insert com ON CONFLICT**

Essa foi a ação que não fiz ao vivo, era mudança de código. Agendamos o deploy pro fim do dia. Mas sem essa parte, o alívio das outras três seria temporário: o volume de writes single-row voltaria a pressionar o banco no próximo pico.

No próximo post dessa série vou detalhar essa refatoração. Resumindo: saímos de `INSERT` um-a-um pra lotes de 500 com `INSERT ... ON CONFLICT DO NOTHING`. O throughput subiu em ordem de grandeza.

# O que mudou depois

Na primeira hora pós-ações: CPU caiu de 90% pra 55%. Connections ativas voltaram pro patamar normal. Latência de commit caiu em torno de 3x.

Na semana seguinte, com o consumer já em batch insert, a CPU média em horário de pico estabilizou em torno de 25–30%. O mesmo hardware, a mesma carga de negócio, só que sem os três multiplicadores compostos.

# Lições

1. Índice custa no write path. Revisar `pg_stat_user_indexes` uma vez por trimestre é barato e teria evitado boa parte dessa crise. 
2. Single-row insert é inofensivo em baixa frequência e assassino em alta: consumer que processa fila deveria nascer com batch, e se nasceu single-row, é dívida técnica com data de vencimento.
3. Seq scan não é necessariamente o vilão, mas em tabela grande quase sempre é, e quando o planner ainda escolhe seq scan com índice disponível, o índice provavelmente não é o certo. 
4. Numa crise, ordem importa: matar conexões penduradas compra tempo, dropar índices reduz write amplification antes de criar novos, e mudança de código fica pro deploy calmo. 
5. E um bom alerta teria detectado tudo isso dias antes do alarme que tocou no dia. O próximo post da série destrincha a refatoração do consumer single-row para batch insert, que foi o que estabilizou o quadro definitivamente.

Numa crise como essa, qual ação você atacaria primeiro: matar conexões idle, dropar índice morto ou refatorar o consumer? A ordem que escolhi tem motivo e gostaria de ver runbooks alternativos.