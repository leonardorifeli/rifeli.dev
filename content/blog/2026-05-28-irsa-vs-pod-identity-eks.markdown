---
title: "IRSA vs Pod Identity no EKS: diferenças, armadilhas e um bug silencioso que me custou duas horas"
draft: false
date: 2026-05-28T00:00:00.000Z
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

<img id="image-custom" src="/images/posts/5e48087d-d8f7-4bb8-bef5-e013c9f238a3.png" alt="" />
<p id="image-legend">IRSA vs Pod Identity</p>

# Introdução

Na Harmo, +70 microservices (Golang, python e node.js) rodam em EKS atendendo +10 milhões de pesquisas e +300 mil avaliações públicas por mês. Cada um desses serviços precisa de credencial AWS pra acessar S3, Secrets Manager, SQS, DynamoDB, o que for. Por anos, IRSA foi a resposta: IAM Role atrelada a Service Account via OIDC, e fim. Em 2023 a AWS lançou Pod Identity, que faz a mesma coisa de forma mais simples. Hoje os dois coexistem, e a dúvida de qual usar aparece em cluster novo e em qualquer conversa de migração.

Esse post é o destilado do que aprendi configurando, quebrando e migrando entre os dois nos últimos meses, incluindo um bug silencioso que me custou umas duas horas num cluster antigo. A mensagem de erro da AWS não ajudou em absolutamente nada.

# Como IRSA funciona

IRSA associa uma Service Account do Kubernetes a uma IAM Role usando o provedor OIDC do cluster EKS. Em uma frase: você registra o OIDC issuer do cluster como Identity Provider na conta AWS, cria uma IAM Role cuja trust policy aceita `sts:AssumeRoleWithWebIdentity` vindo desse issuer pra uma Service Account específica, e anota a SA no Kubernetes com `eks.amazonaws.com/role-arn`. O EKS injeta token projetado e variáveis de ambiente no pod, e o SDK AWS faz o `AssumeRoleWithWebIdentity` sozinho.

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

Pod Identity tira o OIDC da equação. Você instala o **EKS Pod Identity Agent** como addon do cluster, cria uma Role com trust policy pro principal `pods.eks.amazonaws.com` (não mais federated OIDC), e registra um "Pod Identity Association" linkando role e Service Account. O agent, que roda como DaemonSet, intercepta as chamadas do SDK e injeta credenciais.

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

Estava migrando um serviço de IRSA pra Pod Identity num cluster da Harmo criado há mais de um ano. Fiz tudo: nova role, associação via CLI, removi a annotation antiga. Rollout do pod. Resultado:

```
AccessDeniedException: User: anonymous is not authorized to perform: secretsmanager:GetSecretValue
```

"User: anonymous", ou seja, o pod estava fazendo a chamada sem nenhuma credencial. Não era problema de permissão da role, era problema de não ter role nenhuma injetada.

Checklist que rodei na sequência:

- Associação existe? Sim (`aws eks list-pod-identity-associations` confirma).
- Trust policy ok? Sim.
- Service Account certa no deployment? Sim.
- Logs do pod mostram tentativa de chamada? Sim.

Travei. Foram uns 40 minutos só de debug ativo em frente ao terminal, e o incidente todo, contando rollback do serviço pra IRSA, voltar pra Pod Identity depois do fix e revalidar, comeu umas duas horas no total. O erro era óbvio quando encontrei: **o EKS Pod Identity Agent não estava instalado no cluster**. Era um cluster antigo, criado antes do Pod Identity existir, e o addon simplesmente não estava lá. Sem o agent rodando como DaemonSet em cada nó, a interceptação não acontece, o SDK não encontra credencial e cai pra modo anonymous.

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
- **Cluster existente, IRSA funcionando**: não migre só por migrar. Migração dá trabalho e o valor pode pode ser limitado. Migre quando tiver um motivo real (reuso de role entre clusters, simplificar auditoria).
- **Role compartilhada entre vários clusters**: Pod Identity ganha por muito. Com IRSA, cada OIDC provider precisa aparecer na trust policy, vira lista enorme. Com Pod Identity, uma trust policy serve todos.
- **Ambiente multi-cloud ou precisa de OIDC issuer externo**: IRSA. Pod Identity é AWS-only.

# Lições

IRSA é sólido mas verboso. Trust policy com OIDC funciona bem até você precisar debugar, e qualquer erro de string no `sub` vira `AccessDenied` sem pista. Pod Identity simplifica o caminho feliz com menos peças móveis e trust policy legível, mas em troca depende de infraestrutura no cluster: o agent precisa estar rodando como DaemonSet, e se você está migrando cluster antigo, o primeiro passo é checar o addon, não a trust policy.

A lição transversal é mais geral. Erro de `AccessDenied` no EKS pede checagem de camadas, não só de permissão. "User: anonymous" não é permissão insuficiente, é credencial ausente, e isso vira problema de infraestrutura até prova em contrário.

Pensa num prédio com catraca controlada por leitor de crachá. Você passa o crachá e a catraca não abre, mostrando "acesso negado". O reflexo é pensar que seu crachá perdeu permissão, foi desativado, mudou de departamento, e você vai falar com o RH, com a segurança, gasta uma hora investigando o cadastro. Aí descobre que o leitor de crachá daquele andar nunca foi instalado. O equipamento que faria a leitura simplesmente não está lá, e qualquer crachá apresentado vai cair na mesma mensagem genérica. É exatamente o que acontece sem o Pod Identity Agent: o leitor não existe, ninguém intercepta a credencial, e a AWS responde como se o pod fosse anônimo. A pista estava num andar acima do que eu estava investigando.

Por último, coexistência é viável: serviços com IRSA e outros com Pod Identity convivem no mesmo cluster sem atrito. Não precisa migrar tudo de uma vez, e talvez nem precise migrar.

Pra quem já roda IRSA bem mapeado em produção, qual foi o motivo concreto que te fez (ou te fará) migrar pra Pod Identity? Reuso de role entre clusters, simplificar trust policy, ou alguma dor específica de debugging que ainda não vi? Quero ler esses casos aqui embaixo, esse tipo de história economiza horas pra quem vem depois.
