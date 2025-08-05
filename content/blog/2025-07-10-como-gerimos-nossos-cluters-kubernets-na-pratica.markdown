---
title: "Como gerimos nossos clusters Kubernetes na prática"
draft: false
date: 2025-07-10T00:00:00.000Z
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
  "eks",
  "kubernets",
  "gerenciamento de cluster k8s",
]
tags:
  - eks
  - kubernets
  - gestao
---

# Introdução

Em ambientes modernos de produção, como o nosso na Harmo, gerenciar clusters Kubernetes de forma eficiente e segura é essencial. Utilizamos o **Amazon EKS** como nossa base de orquestração, e para operações diárias: observabilidade, debug, troubleshooting e deploys, utilizamos principalmente duas ferramentas: [Lens](https://k8slens.dev/) e [k9s](https://k9scli.io/).

Neste artigo, explico como estruturamos nosso acesso, como usamos essas ferramentas no dia a dia e quais os benefícios que elas trazem para nosso time técnico.

# Visão geral da arquitetura

- Clusters gerenciados no Amazon EKS, com múltiplos ambientes (dev, staging, prod);
- Acesso via `aws eks update-kubeconfig` com autenticação via IAM;
- Configuração de kubeconfig versionado por ambiente;
- Monitoramento integrado via Prometheus e Grafana (externos ao artigo, mas conectados ao Lens via plugins).

# Por que usamos Lens e k9s

O uso se dá de acordo com a sua necessidade, eu particularmente, prefiro o `k9s` pela praticidade de não sair do terminal.

| Ferramenta | Finalidade Principal                                                               | Quando Usamos                                             |
| ---------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Lens**   | UI para inspeção visual rápida, insights, logs, eventos, port-forward com 1 clique | Durante investigações e acompanhamento em tempo real      |
| **k9s**    | CLI ágil para navegação rápida, deploys e debugging                                | No terminal, via SSH, CI/CD ou local para troubleshooting |

# Alias úteis para k9s por ambiente

É possível facilitar o dia a dia com alguns alias no teu `bash profile`.

```bash
# ~/.bashrc ou ~/.zshrc

alias k9s-dev="k9s --context harmo-dev"
alias k9s-prod="k9s --context harmo-prod"
alias k9s-stg="k9s --context harmo-staging"

# Também pode abrir com namespace já definido:
alias k9s-namespace="k9s --context {context-name} -n {namespace-name}"
```

**Exemplo do k9s**:

![https://k9scli.io/assets/screens/xray.png](https://k9scli.io/assets/screens/xray.png)

**Exemplo do Lens**:

![https://docs.k8slens.dev/using-lens/img/overview.png](https://docs.k8slens.dev/using-lens/img/overview.png)

# Benefícios reais no dia a dia

- Time técnico é mais produtivo: reduz o uso de `kubectl` manual;
- Integração visual com Lens facilita aprendizado para novos devs;
- CLI do k9s é absurdamente rápida para alterações pequenas;
- Observabilidade aumentada (com plugins como `Prometheus` no Lens).

#  Cuidados e boas práticas

- Nunca salve kubeconfigs sensíveis localmente sem proteção;
- Mantenha o acesso IAM dos clusters restrito;
- Revogue acessos inativos ou não rotacionados;
- Versione e audite permissões RBAC com clareza.

# Conclusão

O uso combinado de `Lens e k9s` transformou a forma como operamos nossos clusters no EKS. Ganhamos velocidade, confiabilidade e uma visão muito mais clara do ambiente. Recomendo fortemente essas ferramentas, principalmente quando combinadas com boas práticas de segurança e governança nos clusters.
