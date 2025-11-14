---
title: "Como estruturamos nosso pipeline CI/CD para aplicações cloud-native no EKS"
draft: true
date: 2025-11-14T00:00:00.000Z
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

# Como estruturamos nosso pipeline CI/CD para aplicações cloud-native no EKS

Construir uma plataforma cloud-native moderna não depende apenas de Kubernetes, observabilidade e arquitetura distribuída — depende de um **pipeline de entrega contínua confiável**, capaz de compilar, testar, versionar, empacotar e implantar aplicações de forma consistente.

Na Harmo, adotamos um fluxo que conecta:

- **GitHub** (código + PRs)
- **Copilot AI** (refinamento, lint, segurança, padrões)
- **CircleCI** (build, testes, análise estática, push no ECR)
- **AWS ECR** (registry de imagens)
- **Jenkins** (orquestração do deploy)
- **Amazon EKS** (execução final das aplicações)

Este artigo detalha todo o processo, incluindo template de PR, boas práticas de mercado e a visão arquitetural geral.

---

# Resumo rápido (para quem quer entender o fluxo em 20 segundos)

1. O dev abre um **Pull Request** no GitHub.
2. O **Copilot AI** sugere melhorias de código, segurança, testes e estilo.
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

---

# 1. Por que CI/CD é um pilar do cloud-native

Cloud-native exige:

- **deploys frequentes**
- **rollback instantâneo**
- **ambientes efêmeros**
- **consistência entre ambientes**
- **imagens imutáveis**
- **infra em YAML ou Helm**
- **zero intervenção manual**

Sem um pipeline maduro, Kubernetes vira risco, não vantagem.

---

# 2. Visão geral da arquitetura do nosso pipeline

Fluxo completo:

GitHub → Pull Request → Copilot AI → Code Review → Merge → CircleCI → Build Docker → Scan → Push ECR → Trigger Jenkins → Deploy no EKS → Observabilidade

yaml
Copy code

**Pontos fundamentais:**

- Um PR **nunca** vira deploy sem revisão humana.
- Nada roda sem testes — mínimo aceitável de cobertura.
- Toda imagem tem **tag semântica + tag por SHA**.
- Todo deploy é rastreável até o commit original.

---

# 3. GitHub + Copilot AI: a primeira linha de defesa

O GitHub atua como centro de controle:

### ✔️ Branching model padrão
- `main` → produção
- `develop` → staging
- branches de feature: `feature/nome`
- hotfixes controlados por tag

### ✔️ O Copilot ajuda no PR
Usamos o Copilot para:

- sugerir testes automatizados
- detectar código inseguro
- revisar padrões de estilo
- identificar endpoints sem cobertura
- explicar diffs complexos durante code review

Ele não substitui a revisão humana, mas agiliza muito.

---

# 4. Template de Pull Request (padrão Harmo)

Usamos um PR *enxuto, objetivo e baseado em engenharia madura*:

```markdown
## 🔍 Descrição
O que foi alterado? Por quê?

## 🎯 Motivação / Contexto
Qual problema isso resolve?

## 🧪 Testes
- [ ] Testes unitários escritos/atualizados
- [ ] Testes manuais realizados (descrever abaixo)

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

## 📎 Checklist final
- [ ] Segurança revisada
- [ ] Código idempotente
- [ ] Sem breaking changes ocultos


5. Regras de mercado para aprovação de PR

Apenas PRs que seguem práticas maduras são aceitos:

🔹 PR pequeno > PR grande

Pull requests grandes escondem falhas.

🔹 Tudo versionado

Nada fora do Git. Nada.

🔹 Testes obrigatórios

Sem teste = sem merge.

🔹 Padrões de commit

Usamos Conventional Commits:

feat: nova funcionalidade
fix: correção
chore: manutenção
refactor: melhoria sem alterar comportamento
perf: performance
docs: documentação

🔹 Sem merges na sexta-feira

Política que salva finais de semana.

6. CircleCI: build, scan e push para o ECR

Quando o PR é aprovado e mergeado:

O pipeline CircleCI executa:

Checkout do código

Lint + análise estática

Testes unitários

Build da imagem Docker

Execução do Trivy (scan de vulnerabilidades)

Tag da imagem com:

versão semântica

commit SHA

timestamp

Push para o AWS ECR

Chamada ao Jenkins:

jenkins-cli trigger build -p image_tag=$TAG -p service=$SERVICE

7. Jenkins: deploy seguro no EKS

O Jenkins recebe o trigger e roda o pipeline declarativo:

Etapas:

Baixar imagem do ECR

Executar migrações (quando aplicável)

Atualizar ConfigMaps/Secrets

Aplicar manifestos:

kubectl apply -f deployment.yaml


ou

helm upgrade --install service chart/ --atomic --timeout 5m


Aguardar readiness

Validar health checks

Executar rollback automático caso necessário

Com --atomic, o Helm reverte sozinho se algo falhar.

8. Rastreabilidade e confiabilidade

Toda versão na produção possui:

referência ao SHA do commit

tag exata da imagem

ambiente, namespace e cluster

pipeline de origem (CircleCI job ID)

logs de deploy no Jenkins

métricas de latência pós-deploy

Isso facilita postmortems, auditorias e diagnósticos.

9. Benefícios reais desse pipeline

Deploys rápidos e previsíveis

Zero intervenção manual

Menos incidentes

Versionamento rigoroso

Segurança reforçada

Redução drástica de falhas humanas

Replicabilidade entre ambientes

Cultura de engenharia madura

Time mais rápido e com mais confiança

10. Conclusão

CI/CD não é um acessório — é a coluna vertebral de uma plataforma cloud-native.
Sem automação, sem padrões e sem disciplina, Kubernetes se torna uma fábrica de riscos.

Ao integrar GitHub, Copilot, CircleCI, ECR, Jenkins e EKS, criamos um pipeline:

seguro

rastreável

escalável

automatizado

de fácil auditoria

e resiliente a falhas

Esse pipeline permite que a Harmo evolua sua plataforma sem medo de quebrar produção, com velocidade de startup e qualidade de empresa enterprise.