---
title: "Relatório diário de custo AWS com CronJob no EKS: encurtando a demora entre a anomalia e alguém perceber"
draft: false
date: 2026-06-03T00:00:00.000Z
description: "Depois de um incidente em que a conta AWS sangrou por 76 horas sem ninguém perceber, construí um CronJob no EKS que roda toda manhã, puxa o Cost Explorer, detecta anomalia com regra simples e abre task no ClickUp. Arquitetura, código e as decisões que pouparam dor."
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

<img id="image-custom" src="/images/posts/0f89c5bf-73bd-4ab6-b7f9-f960619efc84.png" alt="" />
<p id="image-legend"></p>

# Introdução

Em março, um loop improdutivo numa Step Function rodou por 76 horas e multiplicou a conta AWS do mês da Harmo por quase 6x. Vou falar sobre isso em um artigo aqui na sexta, mas um detalhe da detecção importa pra esse post: o consumo anômalo atravessou um final de semana inteiro sem ninguém perceber, porque a única linha de defesa que pegou o problema foi a revisão manual do dashboard de billing. E revisão manual não acontece no sábado. O anomaly detectou chegou na segunda.

Esse post é sobre uma das contramedidas que nasceram dali: um CronJob no próprio EKS que roda toda manhã, inclusive sábado e domingo, puxa dados do Cost Explorer, compara com a média dos últimos 7 dias e posta o resultado num Doc no ClickUp. Quando detecta anomalia, abre task pra investigação. Roda há dois meses sem falhar e virou peça central da rotina de FinOps de uma operação que processa 10 milhões de pesquisas por mês. O setup todo levou uma tarde. Vou contar aqui a arquitetura, o código essencial e as decisões que pouparam dor.

# Arquitetura

Quatro peças:

1. **CronJob no EKS** — roda às 8h da manhã, todos os dias.
2. **Script Python** — chama Cost Explorer API, calcula deltas, detecta anomalia.
3. **IRSA** — dá permissão pra o pod chamar Cost Explorer sem credencial hardcoded.
4. **Secrets Manager** — guarda o token da API do ClickUp, lido em runtime.

Output vai pra um Doc no ClickUp com histórico (append-only) e, quando detecta anomalia, cria uma task pra investigar.

Por que ClickUp e não Slack, e-mail ou dashboard próprio? Porque é onde o time já trabalha. Relatório que mora fora da ferramenta do dia a dia vira aba esquecida em duas semanas. Task no board que todo mundo olha de manhã tem dono, prazo e cobrança natural. O destino do alerta importa tanto quanto o alerta.

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

A Service Account no Kubernetes anotada com a ARN da role (cobri IRSA em detalhe no [post sobre IRSA vs Pod Identity](/blog/2026-05-28-irsa-vs-pod-identity-eks/)). Pod puxa credenciais via SDK sem código específico.

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

def format_report(day, total, services, anomalies):
    lines = [f"## {day.strftime('%d/%m/%Y')} — total USD {total:.2f}", ""]
    for service, cost in sorted(services.items(), key=lambda s: -s[1]):
        lines.append(f"- {service}: USD {cost:.2f}")
    if anomalies:
        lines.append("")
        lines.append(f"**{len(anomalies)} anomalia(s) detectada(s), tasks criadas.**")
    return {"date": day.strftime("%Y-%m-%d"), "markdown": "\n".join(lines)}

def main():
    yesterday = date.today() - timedelta(days=1)

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
- **Cost Explorer tem delay de ~24h**: dado de "ontem" às 8h da manhã ainda pode ser parcial em alguns serviços (Lambda, S3 Requests). Relatório é diretivo, não auditoria final. Esse delay é estrutural: sinal financeiro nunca vai ser detecção em tempo real, e é por isso que o papel desse robô é encurtar a demora de detecção de dias pra no máximo um, não zerá-la.
- **Separe Doc (histórico) de Tasks (ação)**: humano que vê Doc só no dia ignora; task aparece no board, é trackable.
- **Tem custo a API do Cost Explorer**: USD 0.01 por chamada. 8 chamadas por dia (hoje + 7 dias) dá USD 2,40/mês. Piada de preço, mas vale saber.
- **Alerta pra quando o próprio job falha**: se o CronJob não roda por 2 dias seguidos, você para de receber anomalias e pensa que está tudo bem. Um alert em cima do `failed jobs` do Kubernetes resolve. Detalho isso no post de observabilidade mais adiante na série.

# Lições aprendidas

A lição central não é técnica: custo anômalo na AWS é assintomático. Não derruba serviço, não dispara exceção, não acorda ninguém de madrugada. Pressão arterial alta funciona igual. Não dói, não dá sinal, e por isso a medicina não espera sintoma: mede em toda consulta, de rotina. Quem só mede quando sente alguma coisa descobre tarde. O relatório diário é essa medição de rotina, transformando um problema invisível em número comparável todo dia, inclusive nos dias em que ninguém abriria o dashboard por conta própria.

A segunda lição é que detecção simples supera sofisticação ausente. A regra de 50% sobre a média de 7 dias com piso de USD 5 foi escrita numa tarde e captura a maior parte do que importa. Dá pra evoluir pra média móvel exponencial, sazonalidade, ML. Mas o robô imperfeito rodando todo dia vence o sofisticado que ficou no backlog.

E a terceira: sinal financeiro é backstop, não primeira linha de defesa. Ele chega com 24 a 48 horas de atraso por design. O papel dele é garantir que nenhuma anomalia atravessa um final de semana invisível, como aconteceu com a gente. A janela de minutos é trabalho de alarme técnico em cima de métrica de comportamento, e esse é assunto do post de observabilidade dessa série.

Se você usa o Cost Anomaly Detection nativo da AWS, fica uma pergunta honesta: ele já pegou alguma anomalia sua em tempo útil? No nosso incidente ele estava habilitado e não disparou a tempo. O porquê disso fica pro postmortem, que sai aqui na sexta.
