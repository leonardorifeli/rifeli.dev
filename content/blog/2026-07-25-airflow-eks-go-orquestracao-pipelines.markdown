---
title: "MWAA orquestrando workers em Go no EKS: a stack que sustenta nossos pipelines de dados"
draft: false
date: 2026-07-25T00:00:00.000Z
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

<img id="image-custom" src="/images/posts/b8dbce8d-80f0-41dd-ad4c-fde4573aef81.png" alt="" />
<p id="image-legend">Um cérebro só decide a ordem; muitas mãos executam. O scheduler resolve o grafo de dependências e dispara os workers que fazem o trabalho pesado.</p>

# Introdução

Airflow é Python por natureza. MWAA é o Airflow gerenciado da AWS. EKS é onde nossos workloads pesados rodam, em Go (cluster k8s). A combinação dos três não é a mais óbvia, mas é a que sustenta hoje a maior parte dos pipelines de dados que rodam por trás da Plataforma Harmo. Esse post conta o porquê dessa escolha e como as peças se encaixam.

A escala que essa stack sustenta hoje: +25 DAGs ativas em produção, executando cerca de mil tasks por dia com taxa de falha de 0,35% no último mês. Dessas tasks, uma média de 500 por dia vira pod de Go no EKS, quase 14 mil pods em 30 dias, cuidando da coleta, do processamento e da sincronização das mais de 300 mil avaliações públicas que entram por mês na plataforma.

Antes de entrar na arquitetura, vale dizer o que isso substituiu. A geração anterior era cronjobs agendando Lambdas em Node.js, coladas por filas SQS, e mais tarde Step Functions coordenando os fluxos de coleta. O MWAA entrou em março de 2024, mas não houve corte: parte do legado coexistiu por mais dois anos.

# Por que Airflow

DAG como código em Python virou o ganho mais imediato. Cadeias de dependência entre tasks que viravam código procedural feio em cron + script bash ganharam estrutura declarativa: quem depende de quem, qual o critério de sucesso, qual a política de retry, qual a janela de execução. UI nativa pra backfill, retry manual, visualização de dependências, gestão de SLA. Ecossistema maduro de operators que cobre a maioria dos casos de integração comum.

A maturidade do Airflow trouxe um custo conhecido: ele assume Python no plano da orquestração. E aí entra a decisão de manter Python apenas no scheduler, deixando o trabalho pesado fora dele.

# Por que MWAA pro scheduler e EKS pro runtime

A primeira pergunta foi onde hospedar o Airflow em si. Self-hosted via Helm chart oficial no EKS era opção possível, mas trazia operação inteira do Airflow pra dentro do time: upgrade de versão, gerenciamento de scheduler/web server/workers, backup de metadata DB, segurança. MWAA resolve tudo isso como serviço gerenciado, em troca de menos flexibilidade fina. Pra um time que quer Airflow como ferramenta e não como produto operado, vale a troca.

Nosso ambiente é um mw1.medium rodando Airflow 2.10.1, com dois schedulers e workers Celery escalando de um a cinco. Classe modesta de propósito: o MWAA só coordena. Se o ambiente precisasse ser grande, seria sinal de que trabalho pesado está vazando pra dentro do scheduler.

A segunda pergunta foi onde rodar o trabalho pesado. A Harmo já roda mais de 50 microservices em Go no EKS, com observabilidade, autoscaling, secrets management e quotas de recurso compartilhados. Subir compute pro trabalho pesado em outro lugar (Lambda, ECS, Batch) seria duplicação de operação sem ganho. Então a decisão foi natural: scheduler no MWAA, workload no EKS.

O ponto que destrava a topologia é a integração entre os dois. MWAA tem permissão de chamar a API do EKS via execution role configurada com IAM. Isso permite que o **KubernetesPodOperator** dentro de uma DAG aponte pro nosso cluster EKS e suba pods lá, mesmo o Airflow não morando dentro do cluster. Cada task pesada vira um pod Go separado no EKS, disparado pelo MWAA via API call de pod create. Foi genial.

# Por que Go pros workers

Workers do Airflow padrão em Python sustentam a coordenação, não o trabalho pesado. Quando a task envolve I/O concorrente em volume (coleta paginada, sincronização com APIs externas, escrita em massa em banco), Go entrega throughput de outro patamar com previsibilidade de latência muito melhor. Footprint de container fica pequeno, startup time fica curto, e o padrão de worker pool (com errgroup, context, cancelamento limpo) [já está dominado pelo time](/blog/2026-05-27-concorrencia-worker-pools-go/).

Quatro categorias cobrem quase tudo que roda em Go por aqui. Coleta de avaliações em fontes externas (Google, iFood, TripAdvisor, etc), em lotes que chegam via arquivo no S3. Processamento de texto e IA sobre o que foi coletado, extraindo sentimento, termos e categorias, que é onde está o maior volume de pods do dia. Sincronização de feeds com a ponta do Google: catálogo, cardápio, ofertas. E disparo de notificações e consolidação de relatórios. Todos os workers seguem o mesmo formato: binário único compilado pra arm64, imagem mínima, `cmds=["./main"]` como entrypoint.

Em paralelo, mantemos workers em Python pra coisas em que Python ganha de Go por bibliotecas (manipulação de DataFrame com pandas, ML clássico com scikit-learn, integrações com bibliotecas científicas). A escolha de linguagem por task é feita conscientemente, não por inércia.

# A topologia

O fluxo típico de uma task pesada é o seguinte. DAG em Python define o **KubernetesPodOperator** com a imagem do worker em Go, parâmetros de entrada via variáveis de ambiente ou arquivo de config, e política de retry/timeout. Airflow dispara o pod no cluster, o pod roda o binário Go que faz o trabalho, escreve resultado em destino persistente (S3, Postgres, Kafka, dependendo da task), termina com exit code limpo. Airflow lê o exit code, decide próxima task ou retry.

Uma DAG de coleta real, enxuta e anonimizada, fica assim:

```python
import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.utils.task_group import TaskGroup

dag = DAG(
    dag_id="coleta_avaliacoes",
    start_date=datetime.datetime(2026, 5, 5),
    schedule="0 4,17 * * *",
    catchup=False,
)

def cria_pod(lote_id, arquivo, versao):
    return KubernetesPodOperator(
        dag=dag,
        task_id=f"coleta_avaliacoes_{lote_id}",
        namespace="<NAMESPACE>",
        image=f"<REGISTRY>/coletor-avaliacoes:{versao}",
        cmds=["./main"],
        arguments=["-data", arquivo],
        annotations={
            "karpenter.sh/do-not-disrupt": "true",
            "cluster-autoscaler.kubernetes.io/safe-to-evict": "false",
        },
        container_resources={
            "requests": {"cpu": "500m", "memory": "1024Mi"},
            "limits":   {"cpu": "500m", "memory": "1024Mi"},
        },
        get_logs=True,
        is_delete_operator_pod=True,
        retries=3,
        startup_timeout_seconds=350,
    )

with TaskGroup("coleta", dag=dag) as grupo:
    for i, arquivo in enumerate(lista_arquivos_do_lote(), start=1):
        cria_pod(i, arquivo, versao_imagem())
```

As annotations de anti-disrupção e o requests igual ao limits não são decoração: cada uma dessas linhas é cicatriz de incidente, e conto a história na seção de gotchas. Boa parte das DAGs nem instancia o **KubernetesPodOperator** direto: usa um operator interno que o estende com os defaults (namespace, recursos, proteção contra eviction), pra que DAG nova não reinvente configuração.

Pra dados pequenos entre tasks (IDs, timestamps, métricas de resumo), usamos XCom. Pra dados grandes (datasets, payloads completos), o intermediário é storage externo: o pod escreve em S3, a próxima task lê o path do XCom e busca o conteúdo de lá. XCom tem limite operacional baixo, forçar dado grande por ele é antipattern que aparece em DAG mal desenhada.

# Os gotchas

Cinco aprendizados que custaram tempo.

**Eviction no meio da coleta.** O coletor do iFood leva cerca de meia hora pra varrer mais de 2 mil estabelecimentos. Em maio, execuções começaram a morrer no meio do caminho: numa delas, 1.189 de 2.037 estabelecimentos se perderam quando o pod foi despejado por `EvictionByEvictionAPI`. A consolidação do Karpenter tinha decidido que aquele nó podia ser drenado, e os pods rodavam em QoS Burstable, sem nenhuma proteção contra disrupção. A correção saiu em duas ondas no mesmo dia: annotations `karpenter.sh/do-not-disrupt` e `safe-to-evict: false`, mais requests iguais a limits pra promover os pods a QoS Guaranteed. Na segunda onda, espelhamos a proteção nas duas coletoras mais longas, a do Google (até 3h08 de execução) e a do TripAdvisor (2h20), que eram alvos ainda maiores. Pod de task longa sem proteção explícita é aposta contra o autoscaler, e o autoscaler ganha.

**O retry do Airflow reinicia do zero.** Todos os nossos pods rodam com `retries=3`, e o incidente de eviction confirmou na prática: task despejada aos 90% refaz 100%. Isso transforma idempotência em pré-requisito de design, não em refinamento. Cada worker recebe um lote fechado via arquivo no S3 e precisa poder reprocessar o mesmo lote sem duplicar no destino. Não temos registro de duplicação em produção, e quero que continue assim, porque isso é propriedade de desenho, não de sorte.

**O CLI do MWAA não conhece as suas DAGs.** Rodar `dags list` pelo endpoint de CLI do MWAA retornava 3 das nossas 24 DAGs, com um `ModuleNotFoundError: No module named 'airflow.providers.cncf'` pras outras. O container que atende o CLI não tem o provider do Kubernetes instalado, então falha ao parsear qualquer arquivo que use KubernetesPodOperator, enquanto o scheduler parseia e executa tudo normalmente. `dags details`, que consulta o banco de metadados em vez de parsear arquivo, funciona pra todas. Custa alguns minutos de pânico até perceber que é artefato do CLI, não DAG quebrada.

**Logs em dois lugares por construção.** Com `get_logs=True`, o Airflow puxa o stdout do pod e reemite no log da própria task, que vai pro CloudWatch no log group de tasks do MWAA. Se o worker também envia log direto pro CloudWatch, a mesma linha passa a existir em dois grupos, com dois caminhos de busca diferentes. Vale decidir cedo qual é a fonte da verdade na hora do incidente, antes que a resposta seja descoberta às 3 da manhã.

**A DAG que consulta a AWS no parse.** Nas DAGs de coleta, a lista de pods é montada no nível do módulo: a cada ciclo do DAG processor, o arquivo consulta o ECR pra resolver a versão da imagem e lê o lote no S3 pra decidir a topologia. Funciona, mas acopla o parse das DAGs à disponibilidade de duas APIs da AWS e paga essas chamadas continuamente, não só na execução. Se o ECR soluçar, o scheduler enxerga DAG quebrada. É dívida assumida, e registrar ela num post público é um jeito de não fingir que não existe.

# Lições aprendidas

- Worker padronizado corta custo de manutenção. Cada worker é um binário Go compilado pra arm64 numa imagem mínima, com `./main` de entrypoint. Qualquer coisa além disso na imagem é sintoma de worker mal desenhado.

- Dado grande nunca passa por XCom. Lote entra por arquivo no S3 e o XCom carrega só metadado: path, contagem, versão de imagem. Essa regra precisa ser explícita no time, não convenção implícita, senão a DAG cresce torta.

- Idempotência vale mais que retry esperto. O retry do Airflow reinicia a task do zero, então o worker que não sabe reprocessar o próprio lote sem duplicar é uma duplicação agendada.

- Task longa exige proteção explícita contra disrupção. QoS Guaranteed e annotations de do-not-disrupt não são paranoia: Burstable numa task de 3 horas é aposta contra o autoscaler.

- Métrica retida não é alarme. O MWAA publica tudo em CloudWatch, mas não cria alarme nenhum por padrão. Alarme de orquestração é trabalho seu, e é o tipo de coisa que se descobre tarde.

- Pod não é pra task trivial. Aqui, só uma em cada cinco tasks criadas vira pod; o resto roda em PythonOperator e afins dentro do próprio worker do MWAA. Subir pod, puxar imagem e inicializar runtime pra 200ms de trabalho transforma uma task rápida numa task de 30 segundos.

# Fechamento

A maior parte das empresas trata Airflow e Python como um pacote indivisível: orquestra em Python, executa em Python, escala em Python. Pra quem já opera workload pesado em Kubernetes, o desenho mais limpo é outro. O scheduler resolve o grafo, dispara o pod e cobra o exit code, e nesse papel restrito o Airflow é excelente. O trabalho pesado fica onde a operação já sabe rodar, observar e escalar: no cluster, em Go. A combinação dos três não é a mais óbvia. É a que deixa cada peça fazendo só o que faz melhor.
