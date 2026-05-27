---
title: "Relatórios de custo AWS com CronJob no EKS: automatizando o que ninguém gosta de fazer manualmente"
draft: true
date: 2026-06-03T00:00:00.000Z
description: "Como construí um sistema de relatórios diários de custo AWS com CronJob no EKS, Python, Cost Explorer API e ClickUp — com detecção simples de anomalia e IRSA pra credenciais sem segredos hardcoded."
comments: true
keywords: [
  "AWS",
  "custo AWS",
  "Cost Explorer",
  "EKS",
  "CronJob",
  "Python",
  "ClickUp",
  "IRSA",
  "Secrets Manager",
  "automação billing",
  "detecção de anomalia",
  "finops",
  "como automatizar relatório de custo aws",
  "como usar Cost Explorer API",
  "como integrar ClickUp com AWS"
]
tags:
  - aws
  - eks
  - finops
  - python
  - automação
---

# Introdução

Relatório de custo AWS é aquele processo que todo mundo concorda que é importante, ninguém gosta de fazer manualmente, e por isso vira rotina abandonada até o mês em que chega uma fatura inesperada. Resolvi construir um CronJob no próprio EKS que roda toda manhã, puxa dados do Cost Explorer, detecta anomalias simples e posta num Doc no ClickUp junto com tasks pra o que precisa de ação.

O resultado: passei de "olhar o billing quando lembro" pra "receber diariamente o que mudou e o que merece investigação". O setup todo levou uma tarde. Vou contar aqui a arquitetura, o código essencial e as decisões que pouparam dor.

# Arquitetura

Quatro peças:

1. **CronJob no EKS** — roda às 8h da manhã, todos os dias.
2. **Script Python** — chama Cost Explorer API, calcula deltas, detecta anomalia.
3. **IRSA** — dá permissão pra o pod chamar Cost Explorer sem credencial hardcoded.
4. **Secrets Manager** — guarda o token da API do ClickUp, lido em runtime.

Output vai pra um Doc no ClickUp com histórico (append-only) e, quando detecta anomalia, cria uma task pra investigar.

# IRSA pra credenciais AWS

Não precisa mais que isso. A role precisa de permissão pra Cost Explorer e pra ler do Secrets Manager:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:clickup/token-*"
    }
  ]
}
```

A Service Account no Kubernetes anotada com a ARN da role (já cobri IRSA no post anterior). Pod puxa credenciais via SDK sem código específico.

# O script Python

Simplificado mas próximo do real:

```python
import boto3
import os
import json
import requests
from datetime import date, timedelta

ce = boto3.client("ce", region_name="us-east-1")
secrets = boto3.client("secretsmanager", region_name="us-east-1")

def get_clickup_token():
    resp = secrets.get_secret_value(SecretId="clickup/token")
    return json.loads(resp["SecretString"])["token"]

def get_cost_for_day(day):
    start = day.strftime("%Y-%m-%d")
    end = (day + timedelta(days=1)).strftime("%Y-%m-%d")
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    services = {}
    for group in resp["ResultsByTime"][0]["Groups"]:
        service = group["Keys"][0]
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if amount > 0.01:
            services[service] = amount
    return services

def detect_anomaly(today, baseline):
    anomalies = []
    for service, cost in today.items():
        baseline_cost = baseline.get(service, 0)
        if baseline_cost > 0 and cost > baseline_cost * 1.5 and cost - baseline_cost > 5:
            anomalies.append({
                "service": service,
                "today": cost,
                "baseline": baseline_cost,
                "delta_pct": (cost - baseline_cost) / baseline_cost * 100,
            })
    return anomalies

def main():
    yesterday = date.today() - timedelta(days=1)
    seven_days_ago = date.today() - timedelta(days=8)

    today_costs = get_cost_for_day(yesterday)

    baseline = {}
    for i in range(2, 9):
        day = date.today() - timedelta(days=i)
        day_costs = get_cost_for_day(day)
        for service, cost in day_costs.items():
            baseline[service] = baseline.get(service, 0) + cost
    baseline = {k: v / 7 for k, v in baseline.items()}

    anomalies = detect_anomaly(today_costs, baseline)

    total = sum(today_costs.values())
    report = format_report(yesterday, total, today_costs, anomalies)

    post_to_clickup(report, anomalies, get_clickup_token())

if __name__ == "__main__":
    main()
```

Regra de anomalia é intencionalmente simples: serviço que gastou 50% acima da média dos 7 dias anteriores **e** a diferença absoluta é maior que USD 5. Os dois guard-rails evitam alertar sobre variação percentual em serviços que custam centavos.

# A publicação no ClickUp

A API do ClickUp tem endpoints pra Docs e pra Tasks. Pro relatório diário, append num Doc fixo. Pra anomalias, cria task num list específico. Pedaço relevante:

```python
def post_to_clickup(report, anomalies, token):
    headers = {"Authorization": token, "Content-Type": "application/json"}

    doc_id = os.environ["CLICKUP_DOC_ID"]
    list_id = os.environ["CLICKUP_LIST_ID"]

    requests.post(
        f"https://api.clickup.com/api/v3/docs/{doc_id}/pages",
        headers=headers,
        json={"name": report["date"], "content": report["markdown"]},
    )

    for anomaly in anomalies:
        requests.post(
            f"https://api.clickup.com/api/v2/list/{list_id}/task",
            headers=headers,
            json={
                "name": f"Custo anormal: {anomaly['service']}",
                "description": (
                    f"Custo de ontem: ${anomaly['today']:.2f}\n"
                    f"Média 7 dias: ${anomaly['baseline']:.2f}\n"
                    f"Variação: +{anomaly['delta_pct']:.0f}%"
                ),
                "priority": 2,
            },
        )
```

Doc ID e List ID vêm de variáveis de ambiente, definidas no manifest do CronJob. Token via Secrets Manager.

# O manifest do CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: aws-cost-report
  namespace: finops
spec:
  schedule: "0 11 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          serviceAccountName: aws-cost-report-sa
          restartPolicy: OnFailure
          containers:
            - name: reporter
              image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/aws-cost-report:latest
              env:
                - name: CLICKUP_DOC_ID
                  value: "abc123"
                - name: CLICKUP_LIST_ID
                  value: "xyz789"
              resources:
                requests: { cpu: 100m, memory: 128Mi }
                limits:   { cpu: 500m, memory: 256Mi }
```

`schedule` em UTC. 11h UTC = 8h em Brasília, chegando antes de qualquer standup da manhã. `concurrencyPolicy: Forbid` evita rodar dois jobs sobrepostos. `backoffLimit: 2` tenta no máximo 3 vezes em caso de falha — pra um relatório diário, basta.

# Detalhes que poupam dor depois

- **Granularidade da Cost Explorer**: ficar em `DAILY` é mais barato e mais preciso pro que a gente quer. `HOURLY` custa mais e tem delay maior.
- **Cost Explorer tem delay de ~24h**: dado de "ontem" às 8h da manhã ainda pode ser parcial em alguns serviços (Lambda, S3 Requests). Relatório é diretivo, não auditoria final.
- **Separe Doc (histórico) de Tasks (ação)**: humano que vê Doc só no dia ignora; task aparece no board, é trackable.
- **Tem custo a API do Cost Explorer**: USD 0.01 por chamada. 8 chamadas por dia (hoje + 7 dias) dá USD 2,40/mês. Piada de preço, mas vale saber.
- **Alerta pra quando o próprio job falha**: se o CronJob não roda por 2 dias seguidos, você para de receber anomalias e pensa que está tudo bem. Um alert em cima do `failed jobs` do Kubernetes resolve. Vai entrar no último post dessa série.

# Lições aprendidas

- **Automatize o que você promete fazer manualmente.** O valor não está na sofisticação do script, está no fato de rodar sem você lembrar.
- **Anomalia com dois guard-rails.** Percentual sozinho gera ruído em serviços baratos. Valor absoluto sozinho perde variações caras em serviços grandes. Combinar os dois é o mínimo pra o alerta ser útil.
- **IRSA e Secrets Manager resolvem credenciais de forma limpa.** Nenhum segredo em env var, nenhum token em código.
- **CronJob no próprio cluster é mais barato que Lambda pra esse caso.** Roda nos nós que você já paga. Pra job que leva segundos, é melhor caminho que Lambda + EventBridge.
- **Detecção simples supera sofisticação ausente.** Dá pra evoluir pra média móvel exponencial, detecção sazonal, ML. Mas 50%/USD 5 captura 95% do que importa na prática, e foi escrito numa tarde.

**💬 Como vocês monitoram custo AWS?**

Usam algum serviço third-party, Cost Anomaly Detection nativo, ou também construíram interno? Curioso pra comparar abordagens.
