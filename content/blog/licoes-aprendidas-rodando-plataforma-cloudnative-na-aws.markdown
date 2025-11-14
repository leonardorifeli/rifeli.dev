---
title: "Lições aprendidas rodando uma plataforma cloud-native na AWS"
draft: true
date: 2025-11-14T00:00:00.000Z
description: "Principais aprendizados técnicos, operacionais e culturais ao escalar uma plataforma cloud-native distribuída na AWS usando EKS, Aurora, SQS, Lambda, Firehose e práticas de observabilidade."
comments: true
keywords: [
  "cloud-native",
  "AWS",
  "EKS",
  "observabilidade",
  "Aurora PostgreSQL",
  "FinOps",
  "arquitetura distribuída",
  "devops",
  "engenharia de plataforma",
  "kubernetes"
]
tags:
  - cloud
  - aws
  - arquitetura
  - devops
  - engenharia
---

<img id="image-custom" src="https://clickup.com/images/clickup-v3/CU_3.0_Task_Types.png" alt="cloud-native" />
<p id="image-legend"></p>

# Introdução

Nos últimos anos, a forma como construímos e operamos sistemas evoluiu radicalmente. A migração para a nuvem deixou de ser apenas um movimento tecnológico e passou a ser um movimento cultural, que redefine não só onde rodamos software, mas principalmente como pensamos, desenvolvemos, implantamos e mantemos aplicações em produção.

Antes de entrar nas lições práticas sobre operar uma plataforma cloud-native na AWS, é fundamental alinhar dois conceitos que frequentemente são confundidos, mas que definem todo o restante da arquitetura moderna: Cloud e Cloud-Native.

# O que é Cloud?

Cloud é um modelo de computação baseado no acesso sob demanda a recursos de infraestrutura, armazenamento, redes, dados e serviços gerenciados através da internet.

A nuvem permite:

provisionar recursos em minutos, não semanas;

escalar horizontalmente conforme a carga;

automatizar ambientes inteiros;

reduzir custos ao pagar só pelo uso;

acessar serviços avançados sem comprar hardware;

criar ambientes efêmeros para testes e validação.

Mas mais importante que isso: a nuvem muda o ritmo da engenharia, possibilitando uma velocidade que seria impossível em ambientes tradicionais.

# O que é Cloud-Native?

Cloud-native não significa simplesmente “estar na nuvem”.
Significa projetar e operar sistemas que exploram a nuvem ao máximo.

Um sistema cloud-native nasce com:

elasticidade como padrão,

resiliência embutida,

automação de ponta a ponta,

forte observabilidade,

implantação contínua,

componentes desacoplados,

infraestrutura declarativa,

e alta tolerância a falhas.

Em outras palavras:

Cloud-native é a combinação de arquitetura, cultura e automação para que sistemas sobrevivam e evoluam em ambientes dinâmicos.

# Lições Aprendidas Rodando uma Plataforma Cloud-Native na AWS

Construir e operar uma plataforma verdadeiramente **cloud-native** vai muito além de rodar workloads em containers. Envolve pessoas, processos, arquitetura, governança, automação e uma disciplina contínua de observabilidade.
Nos últimos anos rodando uma stack distribuída na AWS — com EKS, Aurora PostgreSQL, Firehose, Lambda, SQS, OpenSearch, Athena e pipelines de GenAI — aprendemos que o maior desafio não é adotar a nuvem, e sim **operacionalizá-la com confiabilidade e custo-eficiência**.

A seguir, reuni as principais lições aprendidas nesse processo.

---

## 1. Cloud-native não é Kubernetes: é um mindset

Quando migramos nossos primeiros serviços para EKS, fizemos o clássico erro: tratamos Kubernetes como se fosse um datacenter com YAML.

Cloud-native é:

- **Elasticidade real**
- **Efemeridade como padrão**
- **Observabilidade first-class**
- **Automação desde o início**

A mudança mais impactante não foi a tecnologia, mas sim **abandonar o “servidorzão confiável” e abraçar o caos controlado**.

---

## 2. Observabilidade é o que transforma caos em previsibilidade

Os maiores problemas vieram de **falta de visibilidade**.

Lições essenciais:

- CloudWatch sozinho não resolve — centralize em OpenSearch ou Loki
- Correlacione tudo via `trace_id`
- Crie SLOs reais com alertas de burn rate
- Sem P95/P99 você está cego

**Sem observabilidade, Kubernetes vira aleatoriedade.**

---

## 3. Custos se gerenciam no código — não no financeiro

A AWS cobra por tudo que movimenta, armazena ou respira.

Aprendizados:

- O custo real do EKS são os nós, não o cluster
- Aurora cobra caro em I/O
- OpenSearch escala a fatura rápido demais
- Firehose precisa de compressão

Estratégias que funcionaram:

- Autoscaling agressivo
- Instâncias Spot
- Aurora Serverless v2
- Revisão mensal FinOps

**Custos são uma skill técnica.**

---

## 4. Multi-account é segurança operacional

O modelo multi-account trouxe:

- Limitação de impactos
- Ambientes isolados de verdade
- Controle granular de IAM
- Governança mais previsível

Ambientes independentes tornam incidentes muito menos catastróficos.

---

## 5. Deploy contínuo só é bom com rollback contínuo

CI/CD não é sobre deploy rápido — é sobre **desfazer rápido**.

Práticas essenciais:

- Blue/Green ou Canary
- Feature flags
- Versionamento de configs
- Health checks reais

Um deploy não termina até existir rollback de código, infra e dados.

---

## 6. O banco é o coração — e o gargalo

Aurora PostgreSQL é poderoso, mas impõe lições:

- Cuidado com I/O
- Use BRIN em tabelas largas
- Separe leituras e escritas
- Use cache (Redis)

Quando o banco vira gargalo, normalmente **a culpa é sua**.

---

## 7. Autoscaling só funciona com stateless de verdade

Problemas clássicos:

- Sticky sessions
- Buffers locais
- Operações não idempotentes

Quando a plataforma virou 100% stateless, o HPA finalmente começou a funcionar como esperado.

---

## 8. Segurança é atributo do design

Funciona quando:

- IAM é minimizado
- Roles são por serviço
- VPC é segmentada
- Imagens são imutáveis
- Secrets são gerenciados

Segurança não é time; **é arquitetura.**

---

## 9. Testes em produção não são tabus — são obrigatórios

Com responsabilidade:

- Chaos engineering leve
- Canary releases
- Traffic shadowing
- Testes de carga periódicos

Nada simula produção, então **teste em produção com método**.

---

## 10. As maiores lições são humanas

Nada substitui:

- Disciplina de engenharia
- Comunicação clara
- Documentação viva
- Postmortems sem culpados
- On-call saudável

Ferramentas viram plataforma quando existe **cultura**.

---

# Conclusão

Rodar uma plataforma cloud-native na AWS é uma jornada contínua.
A tecnologia evolui, os desafios mudam, mas a essência permanece:

**Cloud-native não é sobre tecnologia — é sobre resiliência, automação e maturidade de engenharia.**