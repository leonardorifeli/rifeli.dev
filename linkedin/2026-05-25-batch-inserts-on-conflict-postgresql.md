# Batch inserts e ON CONFLICT no PostgreSQL: saindo do single-row em consumers de alta frequência

Três variações para o LinkedIn. Mesmo título do post no blog. Link do blog no primeiro comentário.

---

## Variação 1 — número absoluto / antes e depois

47 segundos para gravar 10 mil eventos com INSERT single-row no Aurora PostgreSQL.

1,4 segundo para gravar os mesmos 10 mil eventos em batch de 500 com ON CONFLICT.

Mesma carga útil. Mesmo schema. Mesma instância. O que mudou foi o pedágio fixo do PostgreSQL por INSERT: round-trip de rede, parse, planning, lock, WAL write, commit. Em baixa frequência esse pedágio é invisível. Em alta frequência ele é a maior parte do trabalho do banco.

Qualquer consumer que processa fila deveria nascer em batch. Single-row em alta frequência não é erro de iniciante. É erro de quem ainda não levou banco ao limite.

Como estruturar o batch (UNNEST de arrays funciona melhor que VALUES múltiplo), as armadilhas de ON CONFLICT e o sweet spot de batch size no rifeli.dev. Link no primeiro comentário.

#PostgreSQL #Performance #BackendEngineering #SRE

---

## Variação 2 — armadilha técnica / dev sênior

ON CONFLICT no PostgreSQL não te salva de duplicata DENTRO do mesmo batch.

Você manda 500 eventos num INSERT, dois deles têm a mesma chave única, e o banco devolve:

ERROR: ON CONFLICT DO UPDATE command cannot affect row a second time

A regra é simples: ON CONFLICT age contra o que já está no heap. Linhas que estão no INSERT atual, não. Solução também é simples: deduplicate no cliente antes de mandar o batch. Cinco linhas de código, custa nada.

Aprendi quebrando produção. Documento aqui pra ninguém precisar aprender do mesmo jeito.

Análise completa, com benchmark de single-row vs batch de 100 vs batch de 500, no rifeli.dev. Link no primeiro comentário.

#PostgreSQL #Engineering #BackendDev #Database

---

## Variação 3 — decisão semântica / líder técnico

DO NOTHING vs DO UPDATE no PostgreSQL não é decisão de performance. É decisão de semântica.

DO NOTHING: o evento mais novo não vale mais que o velho. Eventos imutáveis, logs append-only, idempotência. Na maioria dos consumers de fila, é isso que você quer.

DO UPDATE: o registro novo sobrepõe o antigo. E aqui mora uma armadilha que vejo demais: sem cláusula WHERE comparando timestamp, um evento atrasado pode sobrescrever um evento mais recente que já chegou antes. Você cria inconsistência temporal e descobre só quando o customer reclama.

Escreva o WHERE. Sempre.

Detalhamento técnico, benchmarks e armadilhas operacionais no rifeli.dev. Link no primeiro comentário.

#PostgreSQL #DataEngineering #BackendEngineering #SystemDesign

---

## Notas operacionais

- Recomendo Variação 1 para LinkedIn primário amanhã: número absoluto cedo (47s → 1,4s), fala com qualquer audiência técnica.
- Variação 2 é a mais cirúrgica, vai bem com dev sênior e SRE.
- Variação 3 é tom de líder técnico / decisão de arquitetura.
- Link no primeiro comentário em até 60 segundos.
