---
title: "Agendando cronjobs nativos no RDS Aurora PostgreSQL com pg_cron"
draft: false
date: 2025-07-01T00:00:00.000Z
description: "Em muitas aplicações, é comum a necessidade de executar tarefas recorrentes: limpar dados antigos, atualizar tabelas derivadas ou enviar notificações. Em servidores tradicionais, usamos o cron, um agendador de tarefas do sistema operacional, para executar esses processos de forma automática."
comments: true
keywords: [
  "Software",
  "Develop",
  "Setup DEV",
  "rifeli",
  "Software Developer",
  "Data Science",
  "CTO Harmo",
  "scalable architectures",
  "data engineering",
  "cloud solutions",
  "cronjob",
  "RDS Aurora Cluster",
  "RDS Aurora Cluster Postgres with Cronjob",
  "RDS Aurora Cluster Postgres com Cronjob"
]
tags:
  - cronjob
  - aws-rds
  - postgresql
---

# Introdução

As pessoas que gostam do meio tecnológico, acabam esbarrando neste assunto, um conceito que existe antes dos anos 1970 - como deixar agendado a execução de taferas com SQL em minha base de dados?

A ideia aqui, é trazer informações sobre agendamento de tarefas no AWS RDS Aurora Cluster com PostgreSQL.

Em muitas aplicações, é comum a necessidade de executar tarefas recorrentes: limpar dados antigos, atualizar tabelas derivadas ou enviar notificações. Em servidores tradicionais, usamos o cron, um agendador de tarefas do sistema operacional, para executar esses processos de forma automática.

Desde 2021, conseguimos fazer isso de forma nativa, sem precisar criar nenhuma estrutura adicional, como Lambdas, EC2 e/ou EventBridge.

Neste artigo, mostro como ativar o **pg_cron**, criar tarefas agendadas e compartilhar dicas práticas para usar cronjobs diretamente no RDS Aurora PostgreSQL.

# O que é cronjob

Um cronjob é uma tarefa que roda automaticamente em horários definidos. É muito usado para tarefas recorrentes como backup, limpeza de dados e/ou geração de relatórios.

Em ambientes Linux, cron é um agendador de processos do sistema. Mas em bancos PostgreSQL com pg_cron, conseguimos usar sintaxe semelhante ao crontab, com agendamento diretamente via comandos SQL, o que possibilita deixarmos queries agendadas, sem a necessidade do uso de máquinas+triggers.

# Como funciona

Desde a versão 12.5 é possível fazer de forma nativa no RDS Aurora PostgreSQL (antes a gente contornava com evento e lambda). Ou seja, é nativo e permite definir jobs que executam comandos SQL com agendamento cron (ex: todo dia às 2h). Um detalhe importante é que no RDS Aurora, ele roda no mesmo nó primário da instância, então não exige infraestrutura adicional.

# Cenários

O recurso de cron pode ser utilizado em diversos cenários, principalmente com rotinas na base.

- Limpeza de dados antigos (data retention);
- Geração de relatórios periódicos;
- Atualização de dados derivativos ou caches (ex REFRESH MATERIALIZED VIEW);
- Detecção de anomalias ou padrões incomuns (agendar análise estatística e salvar alertas);
- Manutenção preventiva (como REINDEX e VACUUM).

# Como habilitar

Pra usar o recurso cron em seu cluster RDS Aurora PostgreSQL, segue alguns pontos:

- A versão dele precisa ser 12.5+ (se for menos, tu tem um problemão haha);
- Validar se o parâmetro `shared_preload_libraries` contém `pg_cron` (via parameter group do banco);
- Ativar a extensão, como user principal da base, rode `CREATE EXTENSION IF NOT EXISTS pg_cron;`;
- Criar suas crons e ser feliz \o/.

Pra criar as suas crons, é muito simples:

```sql
SELECT cron.schedule(
  'cleanup_old_data', -- name
  '0 2 * * *', -- crontab config (aqui roda 2am)
  $$DELETE FROM logs WHERE created_at < NOW() - interval '30 days'$$ -- query
);
```

Pra gerenciar suas crons, basta validar o que tem: `SELECT * FROM cron.job;` e pra desativar `SELECT cron.unschedule(jobid);`

# 🔐 Alguns cuidados

Como sempre, nem tudo são flores, segue alguns avisos para você ficar alerta:

- O pg_cron executa jobs com o mesmo privilégio do usuário que os criou;
- Jobs falham silenciosamente se houver erro de permissão;
- Ele só roda no nó primário, não em réplicas;
- Monitore uso de CPU/memória caso agende jobs pesados.

# Conclusão

A extensão `pg_cron` transforma o `RDS Aurora PostgreSQL` em um banco ainda mais poderoso, permitindo automação direta, sem precisar de infraestrutura externa. É ideal para tarefas periódicas como limpeza de dados, atualização de caches e envio de notificações.

Diz aí, tá usando cron nativo e otimizando recurso de infra?