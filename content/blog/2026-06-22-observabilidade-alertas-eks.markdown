---
title: "Observabilidade e alertas no EKS: fechando o loop"
draft: false
date: 2026-06-22T00:00:00.000Z
description: "Métricas com Prometheus, logs centralizados, alertas de custo e performance, a camada que transforma um cluster cloud-native em operação real, e como evitar os alertas que só fazem você desligar o celular."
comments: true
keywords: [
  "EKS",
  "observabilidade",
  "Prometheus",
  "Grafana",
  "alertas",
  "logs centralizados",
  "Loki",
  "CloudWatch",
  "alerta fadiga",
  "SRE",
  "cloud native",
  "como configurar alertas EKS",
  "como evitar alerta fatigue",
  "monitoramento kubernetes produção"
]
tags:
  - eks
  - observabilidade
  - sre
  - kubernetes
  - aws
---

<img id="image-custom" src="/images/posts/a67480be-998f-4f5d-b948-24fe0b5c531b.png" alt="" />
<p id="image-legend">Duzentos alertas piscando, e o que importa é aquele único sinal que você consegue enxergar no meio do ruído.</p>

# Introdução

Essa é a última peça de uma série que caminhou por crise de performance no banco, batch inserts, IRSA e Pod Identity, relatórios de custo e concorrência em Go. Cada um desses posts resolveu um problema específico. Observabilidade é o que liga eles, o que transforma "consegui consertar" em "vou ver chegar da próxima vez".

Vou falar do que realmente usamos na Harmo pra operar o cluster EKS: stack de métricas, estratégia de logs, e principalmente a filosofia de alerta, que é onde a maioria das operações se perde, seja por alertar demais, seja por alertar de menos.

# Métricas: Prometheus + Grafana é o default por um motivo

O stack Prometheus + Grafana é o default no Kubernetes por motivos práticos:

- **Integração nativa via ServiceMonitor.** Qualquer serviço que exponha `/metrics` entra no scrape automaticamente.
- **PromQL é a lingua franca.** Aprende uma vez, usa em todo lugar.
- **Alertmanager é separado de Grafana.** Alerting não depende do dashboard estar respondendo.
- **Custo controlado.** Você paga storage e compute dos nós que já tem. Sem per-metric pricing.

Na prática, instala via Helm chart `kube-prometheus-stack` (antigo Prometheus Operator), ajusta retention conforme disco disponível, e está 80% do caminho.

```yaml
prometheus:
  prometheusSpec:
    retention: 30d
    retentionSize: "80GB"
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: gp3
          resources:
            requests:
              storage: 100Gi
```

30 dias de retention é suficiente pra investigar qualquer incidente recente. Pra análise de tendência mais longa, exporta pra S3 via Thanos ou Mimir, mas só se você tem caso real de uso. Não instala por instalar.

# Logs: centralize, mas não tudo

Logs no Kubernetes têm três caminhos comuns:

| Solução             | Quando vale                                         |
| ------------------- | --------------------------------------------------- |
| CloudWatch Logs     | Stack já AWS-nativo, times pequenos, tolera latência e custo por volume |
| Loki                | Stack já Grafana, times com disciplina de labels, volume alto |
| Elasticsearch/OpenSearch | Precisa full-text search agressivo, tem orçamento |

Usamos Loki. Motivo: integra direto com Grafana (queria dashboards correlacionando log e métrica no mesmo painel), tem custo previsível, e força disciplina de labels. Indexar só labels e ler texto bruto vira hábito que paga.

O erro clássico: centralizar todo log de toda aplicação de todo nível. Você paga storage por ruído. Política que adotamos:

- **Aplicação em produção**: `INFO` e acima.
- **Nó e infra**: logs de sistema, kubelet, containerd.
- **Audit log do Kubernetes**: sim, sempre.
- **Debug logs**: só quando debug. Liga temporariamente via config, desliga depois.

# A estratégia de alerta

Aqui mora o que mais diferencia operação boa de operação ruim. A armadilha é simples: você começa com poucos alertas, eles avisam bem, você vai ganhando confiança e adicionando mais. Em 6 meses você tem 200 alertas, metade é falso positivo, você começa a ignorar. E no dia que alerta verdadeiro chega, ele some no meio do ruído.

Regra que seguimos: **alerta só existe se tem ação humana associada e precisa acontecer agora**. Se a ação pode esperar o horário comercial, não é alerta, é uma task no board. Se não tem ação ("a CPU subiu"), não é alerta, é métrica no dashboard.

Três camadas que valem alertar:

**1. Alertas de disponibilidade (página alguém)**

- API principal retornando 5xx em taxa acima de baseline
- Fila de processamento com idade do item mais velho acima de threshold
- Banco indisponível ou latência de commit acima de patamar
- Cluster sem nós prontos ou com pressure crônico

Essas acordam gente de madrugada. Tem que ser tratadas como coisa séria: runbook conhecido, SLA de resposta, e postmortem depois.

**2. Alertas de anomalia (não-urgente, mas sinal)**

- Custo diário AWS acima do baseline (o CronJob do post 4 já resolve isso)
- Taxa de erro acima de baseline mas abaixo do crítico
- Queda súbita em throughput (queue drenando mais devagar)

Esses chegam em canal de Slack, sem on-call. Se ninguém olhar em 24h, não quebra nada, mas se aparecerem três juntos, muda de gravidade.

**3. Alertas de saúde técnica (semanal)**

- Índices do banco com `idx_scan = 0` há mais de 30 dias
- Imagens com CVE alto não atualizadas
- Certificado vencendo em menos de 15 dias

Esses viram tasks num board. Nunca alerta real, só coisa pra revisar no ritmo certo.

# Exemplos de regra no Prometheus

```yaml
groups:
  - name: api-availability
    rules:
      - alert: ApiHighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 3m
        labels:
          severity: page
        annotations:
          summary: "API com 5xx acima de 5% há 3 minutos"
          runbook: "https://wiki.internal/runbook/api-5xx"

      - alert: DbCommitLatencyHigh
        expr: pg_stat_database_commit_time_seconds > 1
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "Latência de commit no Postgres > 1s"
```

Três detalhes não-negociáveis:

- **`for`** (duração antes de disparar): evita alarme por ruído de 30 segundos.
- **`severity`**: roteamento no Alertmanager. `page` acorda, `ticket` cria task, `warning` fica no Slack.
- **`annotations.runbook`**: link pra o que fazer. Alerta sem runbook é alerta novo, e alerta novo nunca deveria ir pra `page` na primeira vez.

# Fechando o loop com os posts anteriores

Cada post da série deixou uma deixa pra cá:

- **Crise no Aurora**: alerta em latência de commit e em `idx_scan = 0` (saúde técnica semanal) teria detectado a deterioração antes do pico.
- **Batch inserts**: alerta em idade do item mais velho na fila detecta regressão de throughput antes do cliente reclamar.
- **IRSA / Pod Identity**: alerta em `AccessDeniedException` com baseline por serviço detecta config quebrada rapidamente.
- **Relatório de custo**: o CronJob gera anomalia detectada, já é alerta estruturado.
- **Worker pool em Go**: expor métricas de goroutines ativas, queue length e erros por worker torna o pool observável.

# Lições aprendidas

- **Observabilidade é investimento contínuo.** Cada incidente é uma oportunidade de adicionar a métrica ou o alerta que teria avisado antes. Feito depois, ainda é feito.
- **Menos alerta é mais alerta.** Alerta só existe se aciona humano e tem ação. Tudo outro é dashboard ou task.
- **Runbook no annotation, sempre.** Alerta sem runbook é quase um alerta falso, vai chegar numa pessoa que não sabe o que fazer.
- **Custo também é métrica.** Tratar custo como sinal técnico, não como "problema do financeiro", reduz surpresa no fim do mês.
- **Loop fechado vale mais que ferramenta cara.** Um stack simples e bem usado bate um stack sofisticado e abandonado.

# Fechando a série

Seis posts cobriram um corte de cloud-native operado de verdade: banco sob pressão e como reagir, consumer eficiente, permissões de pod, visibilidade de custo, concorrência na ponta, e a camada que fecha o loop: observabilidade e alerta.

Nada disso é novo. O valor está em colocar tudo junto e defender a decisão de não sofisticar onde não precisa. Operação boa é repetível, e repetível é o que você consegue explicar pra alguém que entrou no time ontem.

E no seu cluster, qual foi o último alerta que mudou como vocês operam: um que você adicionou preventivamente, ou um que só existe porque um incidente já tinha acontecido?
