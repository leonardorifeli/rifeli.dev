---
title: "MWAA orquestrando workers em Go no EKS: a stack que sustenta nossos pipelines de dados"
draft: true
date: 2026-06-15T00:00:00.000Z
description: "A topologia que combina MWAA (Airflow gerenciado pela AWS) como scheduler em Python e EKS como runtime dos workers pesados em Go. Por que escolhemos esse split, como as DAGs disparam pods em Go via KubernetesPodOperator, e os gotchas operacionais específicos do MWAA + EKS."
comments: true
keywords: [
  "MWAA",
  "Apache Airflow",
  "Airflow",
  "EKS",
  "Go",
  "Golang",
  "Kubernetes",
  "KubernetesPodOperator",
  "orquestração de pipelines",
  "AWS Managed Airflow",
  "data engineering",
  "pipelines de dados",
  "como rodar workload em go no airflow",
  "MWAA com EKS"
]
tags:
  - mwaa
  - airflow
  - eks
  - golang
  - kubernetes
  - data-engineering
---

<img id="image-custom" src="" alt="" />
<p id="image-legend"></p>

# Introdução

Airflow é Python por natureza. MWAA é o Airflow gerenciado da AWS. EKS é onde nossos workloads pesados rodam, em Go. A combinação dos três não é a mais óbvia, mas é a que sustenta hoje a maior parte dos pipelines de dados que rodam por trás da Plataforma Harmo. Esse post conta o porquê dessa escolha e como as peças se encaixam.

[PLACEHOLDER número absoluto cedo: quantas DAGs ativas em produção, quantos pods Go disparados em dia médio, volume de dados processados/dia ou /mês, qualquer dimensão que dê a escala da operação. Sugestão de formato: "Hoje temos X DAGs ativas, que sobem em média Y pods de Go por dia pra processar Z dados em janelas de tempo variando entre N minutos e M horas."]

Antes de entrar na arquitetura, vale dizer o que isso substituiu. [PLACEHOLDER: stack anterior. Era cron + Lambda? Era SQS com consumer permanente? Era ECS com schedule? Conta em uma ou duas linhas o que motivou a migração pro Airflow.]

# Por que Airflow

DAG como código em Python virou o ganho mais imediato. Cadeias de dependência entre tasks que viravam código procedural feio em cron + script bash ganharam estrutura declarativa: quem depende de quem, qual o critério de sucesso, qual a política de retry, qual a janela de execução. UI nativa pra backfill, retry manual, visualização de dependências, gestão de SLA. Ecossistema maduro de operators que cobre a maioria dos casos de integração comum.

[PLACEHOLDER: comparativos descartados. Vocês olharam Prefect, Dagster, Argo Workflows antes de fechar com Airflow? Se sim, vale uma frase explicando por que Airflow venceu. Se não foi explícita a comparação, pode pular esse parágrafo.]

A maturidade do Airflow trouxe um custo conhecido: ele assume Python no plano da orquestração. E aí entra a decisão de manter Python apenas no scheduler, deixando o trabalho pesado fora dele.

# Por que MWAA pro scheduler e EKS pro runtime

A primeira pergunta foi onde hospedar o Airflow em si. Self-hosted via Helm chart oficial no EKS era opção possível, mas trazia operação inteira do Airflow pra dentro do time: upgrade de versão, gerenciamento de scheduler/web server/workers, backup de metadata DB, segurança. MWAA resolve tudo isso como serviço gerenciado, em troca de menos flexibilidade fina. Pra um time que quer Airflow como ferramenta e não como produto operado, vale a troca.

[PLACEHOLDER: tamanho do ambiente MWAA. Qual classe usam (mw1.small / mw1.medium / mw1.large), quantos workers, qual versão do Airflow. Esse detalhe ajuda quem está dimensionando um setup similar.]

A segunda pergunta foi onde rodar o trabalho pesado. A Harmo já roda mais de 50 microservices em Go no EKS, com observabilidade, autoscaling, secrets management e quotas de recurso compartilhados. Subir compute pro trabalho pesado em outro lugar (Lambda, ECS, Batch) seria duplicação de operação sem ganho. Então a decisão foi natural: scheduler no MWAA, workload no EKS.

O ponto que destrava a topologia é a integração entre os dois. MWAA tem permissão de chamar a API do EKS via execution role configurada com IAM. Isso permite que o KubernetesPodOperator dentro de uma DAG aponte pro nosso cluster EKS e suba pods lá, mesmo o Airflow não morando dentro do cluster. Cada task pesada vira um pod Go separado no EKS, disparado pelo MWAA via API call de pod create.

# Por que Go pros workers

Workers do Airflow padrão em Python sustentam a coordenação, não o trabalho pesado. Quando a task envolve I/O concorrente em volume (coleta paginada, sincronização com APIs externas, escrita em massa em banco), Go entrega throughput de outro patamar com previsibilidade de latência muito melhor. Footprint de container fica pequeno, startup time fica curto, e o padrão de worker pool (com errgroup, context, cancelamento limpo) [já está dominado pelo time](/blog/2026-05-27-concorrencia-worker-pools-go/).

[PLACEHOLDER: exemplos concretos de tipos de workload que rodam em Go. Coleta de avaliações? NLP/processamento de texto? Sincronização com Google Business Profile, com Meta, com ERP de cliente? Indexação? Geração de relatórios? Lista três ou quatro categorias.]

Em paralelo, mantemos workers em Python pra coisas em que Python ganha de Go por bibliotecas (manipulação de DataFrame com pandas, ML clássico com scikit-learn, integrações com bibliotecas científicas). A escolha de linguagem por task é feita conscientemente, não por inércia.

# A topologia

O fluxo típico de uma task pesada é o seguinte. DAG em Python define o KubernetesPodOperator com a imagem do worker em Go, parâmetros de entrada via variáveis de ambiente ou arquivo de config, e política de retry/timeout. Airflow dispara o pod no cluster, o pod roda o binário Go que faz o trabalho, escreve resultado em destino persistente (S3, Postgres, Kafka, dependendo da task), termina com exit code limpo. Airflow lê o exit code, decide próxima task ou retry.

[PLACEHOLDER: exemplo de DAG simplificado. Snippet em Python de 15-25 linhas mostrando uma DAG com um KubernetesPodOperator disparando um worker em Go. Pode ser anonimizado, função fictícia tipo "coleta_avaliacoes" ou "sincroniza_perfil_loja".]

Pra dados pequenos entre tasks (IDs, timestamps, métricas de resumo), usamos XCom. Pra dados grandes (datasets, payloads completos), o intermediário é storage externo: o pod escreve em S3, a próxima task lê o path do XCom e busca o conteúdo de lá. XCom tem limite operacional baixo, forçar dado grande por ele é antipattern que aparece em DAG mal desenhada.

# Os gotchas

Cinco aprendizados que custaram tempo aprender.

[PLACEHOLDER 1: OOMKilled em batch grande. O pod do worker em Go precisa ter request e limit de memória bem dimensionado, não confiar no default do cluster. Quando o batch chega 5x maior que o esperado, o pod morre silenciosamente e o Airflow vê só exit code 137. Conta uma vez que isso pegou vocês, se houver caso.]

[PLACEHOLDER 2: logs em dois lugares. O pod escreve no stdout, CloudWatch captura via fluentd/fluent-bit, mas o Airflow também guarda os logs do pod. Resultado: log duplicado, dois caminhos de busca diferentes na hora do incidente. Decisão: padronizar onde fica a fonte da verdade.]

[PLACEHOLDER 3: retry do Airflow vs idempotência do worker. Se o Airflow disparar a task duas vezes (porque a primeira deu timeout e ele acionou retry), o worker em Go precisa ser idempotente em relação ao dado processado. Sem isso, dado duplicado em destino. Padrão: chave de execução única passada pelo Airflow, worker checa se já processou essa chave antes de começar.]

[PLACEHOLDER 4: KubernetesPodOperator e XCom timing. XCom é persistido depois que o pod termina, lido pelo Airflow via API do cluster. Em pods muito rápidos, o XCom pode ser lido antes de ser totalmente persistido, dando inconsistência rara. Mitigação: pequeno delay antes do término, ou usar XCom backend externo.]

[PLACEHOLDER 5: janela de manutenção do EKS vs DAG longa. Quando o EKS faz rolling update de node, pods são evictidos. DAG que estava no meio de uma task longa quebra. Estratégias: tasks idempotentes com retry forte, ou tasks curtas que sobrevivem à eviction.]

# Lições aprendidas

[PLACEHOLDER prosa (5 parágrafos curtos, alternando com lições do post de 12/06 que será prosa, ou ajustar pra bullet se preferir). Sugestões de temas das lições, baseadas no que vocês já viveram:

- Imagem base padronizada pros workers Go cortou tempo de build e manutenção. Cada worker é o binário compilado + Alpine/distroless + healthcheck mínimo. Mais que isso é sintoma de imagem mal desenhada.

- XCom vs storage externo deve ser decisão de design da DAG, não convenção implícita. Time inteiro precisa saber qual dado vai por XCom e qual vai por path em S3, senão a DAG cresce torta.

- Idempotência é mais importante que retry esperto. Vale a pena gastar tempo desenhando worker idempotente em vez de configurar política de retry sofisticada que vai te morder mais tarde.

- Observabilidade unificada paga por si. Logs em CloudWatch, métricas em Prometheus, traces em onde quer que vocês usem. Dashboards mostrando saúde das DAGs + saúde dos pods + saúde do EKS no mesmo lugar.

- Não usar KubernetesPodOperator pra task trivial. Overhead de subir pod, baixar imagem (se não cacheada), inicializar Go runtime, conectar com destino, fazer trabalho pequeno, e morrer, faz uma task de 200ms levar 30 segundos. Pra trabalho pequeno, BashOperator ou PythonOperator dentro do worker do Airflow é melhor escolha.]

[PLACEHOLDER fechamento sem CTA formulaico. Algo amarrando o motivo dessa stack: a maior parte das empresas trata Airflow + Python como fim em si. Pra quem opera workload pesado em Kubernetes, separar scheduler (Python) de runtime (Go em pods) é arquitetura mais limpa, e Airflow vira excelente nesse papel restrito.]
