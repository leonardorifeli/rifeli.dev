---
title: "Como utilizar Cronjobs no AWS RDS Aurora Cluster"
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

# Cenários

#

# Conclusão
