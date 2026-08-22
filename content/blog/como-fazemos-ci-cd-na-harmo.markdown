---
title: "Como estruturamos nosso pipeline CI/CD para aplicações cloud-native no EKS"
draft: false
date: 2025-11-01T00:00:00.000Z
description: "Entenda como funciona nosso pipeline CI/CD usando GitHub, Copilot AI, CircleCI, AWS ECR, Jenkins e Kubernetes (EKS) para garantir deploys previsíveis, seguros e escaláveis."
comments: true
keywords: [
  "CI/CD",
  "pipeline",
  "GitHub",
  "CircleCI",
  "ECR",
  "Jenkins",
  "EKS",
  "cloud-native",
  "devops",
  "deploy automatizado"
]
tags:
  - cloud
  - devops
  - aws
  - engenharia
  - automação
---

<img id="image-custom" src="https://assets.primotech.com/wp-content/uploads/2022/07/CICD-Pipeline-Everything-You-Need-to-Know-1024x546.png" alt="cloud-native" />
<p id="image-legend"></p>

## Introdução

Construir uma plataforma cloud-native moderna não depende apenas de Kubernetes, observabilidade e arquitetura distribuída, mas sim de um **pipeline de entrega contínua confiável**, capaz de compilar, testar, versionar, empacotar e implantar aplicações de forma consistente.

Na Harmo, adotamos um fluxo que conecta:

- **GitHub** (código + PRs)
- **Copilot AI** (code-review, refinamento, lint, segurança, padrões)
- **CircleCI** (build, testes, análise estática, push no ECR)
- **AWS ECR** (registry de imagens)
- **Jenkins** (orquestração do deploy)
- **Amazon EKS** (execução final das aplicações)

## Como fazemos

Buscamos ao longo dos anos, um fluxo confiável e robusto de entrega contínua.

1. O dev abre um **Pull Request** no GitHub.
2. O **Copilot AI** sugere melhorias de código, segurança, testes e estilo. Além de outras pessoas desenvolvedoras.
3. O PR é revisado com regras rígidas e padronizadas.
4. Ao receber *approve*, o **merge** dispara pipelines no CircleCI.
5. O CircleCI:
   - roda testes
   - executa linting
   - builda a imagem Docker
   - faz push no **AWS ECR**
   - chama o **Jenkins via CLI**
6. O Jenkins executa o pipeline de deploy:
   - baixa a nova imagem
   - aplica YAML ou roda Helm
   - valida readiness
   - realiza rollback automático se necessário
7. A aplicação é atualizada no **EKS**.

Resultado: deploys previsíveis, auditáveis e rastreáveis.

## Por que CI/CD é um pilar do cloud-native

Cloud-native não significa simplesmente "estar na nuvem"s. Significa projetar e operar sistemas que exploram a nuvem ao máximo. Tendo autonomia e facilidade para entrega contínua de soluções.

Em uma filosofia Cloud-native exige:

- **deploys frequentes**
- **rollback instantâneo**
- **ambientes efêmeros**
- **consistência entre ambientes**
- **imagens imutáveis**
- **infra em YAML ou Helm**
- **zero intervenção manual**

Na minha visão, sem um pipeline maduro, Kubernetes vira risco, não vantagem.

## Visão geral da arquitetura do nosso pipeline

Fluxo completo:

GitHub → Pull Request → Copilot AI → Code Review → Merge → CircleCI → Build Docker → Scan → Push ECR → Trigger Jenkins → Deploy no EKS → Observabilidade

**Pontos fundamentais:**

- Um PR **nunca** vira deploy sem revisão humana.
- Toda imagem tem **tag semântica + tag por SHA**.
- Todo deploy é rastreável até o commit original.

## GitHub + Copilot AI: a primeira linha de defesa e automação

O GitHub atua como centro de controle:

#### ✔️ Branching model padrão
- `main` → produção
- `develop` → staging (estamos em constante avanço nessa parte)
- branches de feature: `feature/nome`
- hotfixes controlados por tag

#### ✔️ O Copilot ajuda no PR
Usamos o Copilot para:

- detectar código inseguro
- revisar padrões de estilo
- identificar endpoints sem cobertura
- explicar diffs complexos durante code review

Ele não substitui a revisão humana, mas agiliza muito.

## Template de Pull Request (padrão Harmo)

Usamos um PR *enxuto, objetivo e baseado em engenharia madura*:

```markdown
## 🔍 Descrição
O que foi alterado? Por quê?

## 🎯 Motivação / Contexto
Qual problema isso resolve?

## 📊 Observabilidade
- [ ] Logs ajustados
- [ ] Métricas adicionadas/alteradas
- [ ] Dashboards/alerts impactados?

## 💰 Impacto em Custos
- [ ] Avaliado (I/O, memória, storage, execuções, banda)

## 🚀 Deploy
Serviço / namespace afetado:

## 🔙 Rollback
Como desfazer? (passo a passo)
```

## CircleCI: build, scan e push para o ECR

Quando o PR é aprovado e mergeado, pipeline CircleCI executa:

- Checkout do código
- Lint + análise estática
- Testes unitários
- Build da imagem Docker

Tag da imagem com:

- versão semântica
- commit SHA
- timestamp
- Push para o AWS ECR

Chamada ao Jenkins:

Temos um repositório interno de CLI, ele é clonado durante o build, e o jenkins é acionado via bash, usando a API do jenkins.

## Jenkins: deploy seguro no EKS

O Jenkins recebe o trigger e roda o pipeline de deploy:

- Baixar imagem do ECR
- Edita os arquivos helm
- Atualiza o EKS/pods

Utilizando a flag `--atomic`, o Helm reverte sozinho se algo falhar.

## Rastreabilidade e confiabilidade

Toda versão na produção possui:

- referência ao SHA do commit
- tag exata da imagem
- ambiente, namespace e cluster
- pipeline de origem (CircleCI job ID)
- logs de deploy no Jenkins
- métricas de latência pós-deploy

Isso facilita postmortems (fica pra um próximo artigo), auditorias e diagnósticos.

## Benefícios reais

- Deploys rápidos e previsíveis
- Zero intervenção manual
- Menos incidentes
- Versionamento rigoroso
- Segurança reforçada
- Redução drástica de falhas humanas
- Replicabilidade entre ambientes
- Cultura de engenharia madura
- Time mais rápido e com mais confiança

## Conclusão

CI/CD não é um acessório, é a coluna vertebral de uma plataforma cloud-native.
Sem automação, sem padrões e sem disciplina, Kubernetes se torna uma fábrica de riscos.

Ao integrar GitHub, Copilot, CircleCI, ECR, Jenkins e EKS, criamos um pipeline:

- seguro
- rastreável
- escalável
- automatizado
- de fácil auditoria
- e resiliente a falhas

Esse pipeline permite que a Harmo evolua sua plataforma sem medo de quebrar produção, com velocidade de startup e qualidade de empresa enterprise.
s
E quais são suas experiências em CI/CD? Compartilha conosco nos comentários.