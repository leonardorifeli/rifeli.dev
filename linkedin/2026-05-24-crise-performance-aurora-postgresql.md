# Crise de performance no Aurora PostgreSQL: o que aprendi apagando incêndio ao vivo

Três variações para o LinkedIn. Mesmo título do post no blog. Link do blog no primeiro comentário.

---

## Variação 1 — war story / abertura forte

Quarta de manhã. Dashboard vermelho. Aurora PostgreSQL 90 por cento de CPU sustentada. Connections de 120 para 380 em 15 minutos. P95 de commit subindo de dezenas de milissegundos para mais de um segundo.

Três sintomas simultâneos quase nunca têm uma única causa.

Eram três se reforçando: write amplification de 18 índices mortos, inserts single-row em alta frequência num consumer SES, e seq scan que o planner não devia estar fazendo. Cada um sozinho era digerível. Juntos derrubavam a plataforma.

O que mais aprendi não foi sobre PostgreSQL. Foi sobre a ordem das ações numa crise. Matar conexões penduradas antes de tocar em índice. Dropar índice antes de criar. Mudança de código por último, no deploy calmo.

Detalhe completo, com as queries e a ordem real do troubleshooting, no rifeli.dev. Link no primeiro comentário.

#PostgreSQL #Aurora #DatabasePerformance #SRE #Engineering

---

## Variação 2 — número absoluto / leitor C-level

Na Harmo, o core transacional processa 10 milhões de pesquisas e 300 mil avaliações por mês num Aurora PostgreSQL single writer.

Quando esse fluxo degrada, a plataforma inteira sente.

Atravessei uma crise onde três problemas compostos quase nos derrubaram: índices mortos cobrando write amplification, consumer SES inserindo evento-a-evento em alta frequência, e uma query lenta ressentindo o resto. A query lenta saiu de 4,2 segundos para 38 milissegundos depois do índice composto certo.

Isso virou post no rifeli.dev. A parte mais útil não são as queries. É a ordem que eu executei o roteiro de mitigação, e o que faltava monitorar para detectar isso dias antes.

Link no primeiro comentário.

#PostgreSQL #Aurora #CTO #DataInfrastructure #Harmo

---

## Variação 3 — insight contra-intuitivo / leitor DBA / dev

Tinha 18 índices em produção com zero uso há 30 dias.

Alguns com mais de 2 GB cada. Todos sendo escritos em toda transação. Write amplification gratuita pagando o pedágio em cada INSERT, UPDATE e DELETE.

A ironia: a equipe que adicionou os índices fez isso por motivos legítimos, queries pontuais que existiam meses atrás. Ninguém revisitou. Ninguém olha pg_stat_user_indexes em ciclo regular.

Drop CONCURRENTLY, um de cada vez, monitorando. CPU começou a ceder dos 90 por cento sem precisar tocar em nenhuma query.

Detalhamento completo da crise, incluindo as três causas compostas e a ordem das ações no rifeli.dev. Link no primeiro comentário.

#PostgreSQL #DBA #DatabasePerformance #Aurora

---

## Notas operacionais

- Recomendo Variação 1 para LinkedIn primário hoje: war story curta, sintoma forte, fecha com a lição de ordem das ações.
- Variação 2 puxa pelo lado de operação Harmo (volume público + número absoluto). Boa para audiência C-level / champion.
- Variação 3 é a mais técnica, leitor DBA / dev sênior.
- Link no primeiro comentário em até 60 segundos da publicação.
