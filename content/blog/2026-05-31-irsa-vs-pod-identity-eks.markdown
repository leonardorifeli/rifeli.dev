---
title: "IRSA vs Pod Identity no EKS: diferenças, armadilhas e um bug silencioso que me custou duas horas"
draft: true
date: 2026-05-31T00:00:00.000Z
description: "Como IRSA funciona no EKS, o que mudou com Pod Identity, quando preferir um sobre o outro, e um bug real: AccessDeniedException causado por webhook de Pod Identity não instalado no cluster."
comments: true
keywords: [
  "EKS",
  "IRSA",
  "Pod Identity",
  "IAM Roles for Service Accounts",
  "Kubernetes",
  "AWS",
  "OIDC",
  "AccessDeniedException",
  "eks-pod-identity-agent",
  "service account",
  "como configurar IRSA",
  "diferença IRSA Pod Identity",
  "como migrar IRSA para Pod Identity"
]
tags:
  - eks
  - aws
  - kubernetes
  - iam
  - segurança
---

# Introdução

IAM Roles for Service Accounts (IRSA) foi a forma certa de dar credenciais AWS pra pods no EKS por vários anos. Funciona, é seguro, e é o padrão da maioria dos clusters em produção. Em 2023 a AWS lançou Pod Identity — que faz a mesma coisa, mas mais simples. Hoje os dois coexistem, e a dúvida de qual usar aparece em cluster novo e em migração.

Esse post é o destilado do que aprendi configurando, quebrando e migrando entre os dois nos últimos meses — incluindo um bug silencioso que me custou umas duas horas porque a mensagem de erro da AWS não ajudou em nada.

# Como IRSA funciona

IRSA associa uma Service Account do Kubernetes a uma IAM Role usando o provedor OIDC do cluster EKS. O fluxo:

1. O cluster EKS tem um OIDC issuer URL (ex: `https://oidc.eks.us-east-1.amazonaws.com/id/EXAMPLE...`).
2. Você registra esse issuer como Identity Provider na sua conta AWS (é feito uma vez por cluster).
3. Cria uma IAM Role com trust policy que aceita `sts:AssumeRoleWithWebIdentity` vindo desse OIDC issuer, limitado a uma Service Account específica.
4. Anota a Service Account no Kubernetes com `eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/minha-role`.
5. O EKS injeta variáveis de ambiente e um token projetado no pod. SDKs AWS detectam esses vars e fazem `AssumeRoleWithWebIdentity` automaticamente.

A trust policy da role é onde mora a complexidade:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/EXAMPLE"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "oidc.eks.us-east-1.amazonaws.com/id/EXAMPLE:sub": "system:serviceaccount:default:minha-sa",
        "oidc.eks.us-east-1.amazonaws.com/id/EXAMPLE:aud": "sts.amazonaws.com"
      }
    }
  }]
}
```

Qualquer vírgula fora do lugar no `sub` e você pega `AccessDenied` sem pista do porquê.

# O que mudou com Pod Identity

Pod Identity tira o OIDC da equação. O fluxo fica:

1. Você instala o **EKS Pod Identity Agent** no cluster (addon da AWS).
2. Cria uma IAM Role com trust policy pro principal `pods.eks.amazonaws.com` (não mais federated OIDC).
3. Cria um "Pod Identity Association" linkando a role a uma Service Account.
4. O agent intercepta as chamadas do SDK e injeta credenciais.

A trust policy simplifica muito:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "pods.eks.amazonaws.com" },
    "Action": ["sts:AssumeRole", "sts:TagSession"]
  }]
}
```

Pra criar a associação via CLI:

```bash
aws eks create-pod-identity-association \
  --cluster-name meu-cluster \
  --namespace default \
  --service-account minha-sa \
  --role-arn arn:aws:iam::123456789012:role/minha-role
```

Nenhuma annotation na Service Account. A associação mora no plano de controle do EKS.

# Diferenças práticas

| Critério                      | IRSA                            | Pod Identity                  |
| ----------------------------- | ------------------------------- | ----------------------------- |
| Setup por cluster             | OIDC provider + IAM config      | Instalar addon                |
| Trust policy por role         | Complexa (OIDC federation)      | Simples (service principal)   |
| Associação SA → Role          | Annotation na SA                | Associação no plano EKS       |
| Reuso de role entre clusters  | Trust policy precisa listar cada cluster | Trust policy única    |
| Dependência de addon no cluster | Não                           | Sim (Pod Identity Agent)      |
| Região suportada              | Todas                           | Maioria (verificar)           |
| Maturidade ecosistema         | Alta (todas as ferramentas)     | Crescente                     |

# O bug silencioso

Estava migrando um serviço de IRSA pra Pod Identity num cluster que tinha sido criado há mais de um ano. Fiz tudo: nova role, associação via CLI, removi a annotation antiga. Rollout do pod. Resultado:

```
AccessDeniedException: User: anonymous is not authorized to perform: secretsmanager:GetSecretValue
```

"User: anonymous" — ou seja, o pod estava fazendo a chamada sem nenhuma credencial. Não era problema de permissão da role, era problema de não ter role nenhuma injetada.

Checklist que rodei:

- Associação existe? Sim (`aws eks list-pod-identity-associations` confirma)
- Trust policy ok? Sim
- Service Account certa no deployment? Sim
- Logs do pod mostram tentativa de chamada? Sim

Fiquei travado uns 40 minutos. O erro era óbvio quando encontrei: **o EKS Pod Identity Agent não estava instalado no cluster**. Era um cluster antigo, criado antes do Pod Identity existir, e o addon simplesmente não estava lá. Sem o agent rodando como DaemonSet em cada nó, a interceptação não acontece — o SDK não encontra credencial e cai pra modo anonymous.

Solução, uma linha:

```bash
aws eks create-addon \
  --cluster-name meu-cluster \
  --addon-name eks-pod-identity-agent
```

O que piora é que a mensagem de erro da AWS não indica isso. "anonymous" parece problema de trust, não de infraestrutura ausente. A lição: quando um cluster é antigo e você está adotando um recurso novo do EKS, verifique primeiro se o addon correspondente está instalado.

Pra checar rapidamente:

```bash
kubectl get daemonset -n kube-system eks-pod-identity-agent
```

Se não retornar nada, está faltando.

# Quando usar qual

Recomendação pragmática:

- **Cluster novo, sem legado**: Pod Identity. Setup mais simples, trust policy mais limpa, menos coisas pra errar.
- **Cluster existente, IRSA funcionando**: não migre só por migrar. Migração dá trabalho e o valor marginal é limitado. Migre quando tiver um motivo real (reuso de role entre clusters, simplificar auditoria).
- **Role compartilhada entre vários clusters**: Pod Identity ganha por muito. Com IRSA, cada OIDC provider precisa aparecer na trust policy — vira lista enorme. Com Pod Identity, uma trust policy serve todos.
- **Ambiente multi-cloud ou precisa de OIDC issuer externo**: IRSA. Pod Identity é AWS-only.

# Lições aprendidas

- **IRSA é sólido mas verboso.** Trust policies com OIDC são o tipo de coisa que funciona bem até você tentar debugar. Qualquer erro de string no `sub` vira `AccessDenied` sem pista.
- **Pod Identity simplifica o caminho feliz.** Menos peças móveis, trust policy legível.
- **Pod Identity depende de infraestrutura no cluster.** O agent precisa estar rodando. Se estiver migrando cluster antigo, verifique o addon antes de qualquer coisa.
- **Erros de AccessDenied merecem checagem de camadas, não só de permissões.** "User: anonymous" é sinal de credencial ausente, não de permissão insuficiente. Trate como problema de infraestrutura até provar o contrário.
- **Coexistência é viável.** Você pode ter serviços com IRSA e outros com Pod Identity no mesmo cluster. Não precisa migrar tudo de uma vez.

**💬 Vocês já migraram pra Pod Identity?**

Encontraram alguma armadilha que valha registrar? Comentem — esse tipo de história economiza horas pra quem vem depois.
