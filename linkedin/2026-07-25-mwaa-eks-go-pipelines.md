# MWAA orquestrando workers em Go no EKS

Três variações para o LinkedIn. Post no blog datado 2026-07-25. Link do blog no
primeiro comentário. Primeira linha sempre narrativa, nunca bloco de código.

Primeiro comentário (qualquer variação):

> Post completo: https://rifeli.dev/blog/2026-07-25-airflow-eks-go-orquestracao-pipelines/

---

## Variação 1 — como a stack funciona (recomendada)

Nosso ambiente de Airflow é um mw1.medium, a classe mais modesta que a AWS oferece no MWAA. É de propósito: ele coordena cerca de 500 pods de Go por dia e não executa nenhum deles.

A divisão é essa. MWAA é scheduler, EKS é runtime. O Airflow assume Python no plano da orquestração, e Python sustenta coordenação muito bem. O que a gente não deixou acontecer foi o trabalho pesado ficar preso ali.

A peça que destrava é o KubernetesPodOperator com uma execution role IAM. O MWAA tem permissão de chamar a API do EKS, então a DAG em Python define a imagem, os parâmetros e a política de retry, e o pod sobe no nosso cluster mesmo com o Airflow não morando dentro dele. O scheduler nunca hospeda o processo pesado: ele acompanha um pod e um estado.

Do outro lado, o worker em Go. O perfil do nosso trabalho é I/O concorrente, paginação e escrita em massa em banco, e ali Go entrega throughput maior com consumo previsível. Binário único compilado pra arm64, imagem mínima, `cmds=["./main"]` como entrypoint. Quatro categorias cobrem quase tudo: coleta de avaliações em fontes externas, processamento de texto e IA sobre o que foi coletado, sincronização de feeds com a ponta do Google, e disparo de notificações com consolidação de relatórios.

Python não saiu de cena, ficou onde ganha: DataFrame com pandas, ML clássico com scikit-learn. A escolha de linguagem por task é consciente, não inércia.

Duas regras que sustentam isso de pé:

:: XCom carrega referência, não payload. Dado pequeno passa por ele; dataset vai pro S3 e a próxima task lê o path.
:: DAG nova não reinventa configuração. A maioria nem instancia o KubernetesPodOperator direto, usa um operator interno que já traz namespace, recursos e proteção contra disrupção nos defaults.

E o melhor termômetro que essa arquitetura me deu: se o ambiente do MWAA precisasse ser grande, seria sinal de que trabalho pesado está vazando pra dentro do scheduler.

Hoje são mais de 25 DAGs ativas, cerca de mil tasks por dia com 0,35% de falha no último mês, e cerca de 15 mil pods de Go em 30 dias sustentando as mais de 300 mil avaliações públicas que entram por mês.

No post tem a DAG real anonimizada, a integração MWAA com EKS em detalhe e as cinco cicatrizes que custaram tempo. Link no primeiro comentário.

#DataEngineering #Airflow #Golang #Kubernetes #AWS

---

## Variação 2 — war story do eviction

Uma execução da nossa coletora perdeu 1.189 dos 2.037 estabelecimentos no meio do caminho. O pod não travou nem estourou memória: ele foi despejado.

A coleta leva cerca de meia hora. Nesse intervalo, a consolidação do Karpenter decidiu que aquele nó podia ser drenado, e os pods rodavam em QoS Burstable, sem nenhuma proteção declarada. `EvictionByEvictionAPI` no evento, mais de mil estabelecimentos sem coletar, e o Airflow reportando só a task falhada.

A correção saiu em duas ondas no mesmo dia, e ela junta dois mecanismos que eu aprendi a não confundir:

:: `karpenter.sh/do-not-disrupt` fala com o Karpenter e pede pra ele não escolher aquele nó pra consolidação ou drain voluntário.
:: Requests iguais a limits fazem outra coisa: promovem o pod a QoS Guaranteed, o que reduz o risco de eviction quando o nó entra em pressão de recurso.

Nenhuma das duas cobre o buraco da outra. QoS Guaranteed sozinho não impede o Karpenter de consolidar o nó embaixo do pod. E `do-not-disrupt` não protege contra disrupção involuntária: se o nó morre, o pod cai igual.

O que ficou como regra: pod de task longa sem proteção explícita é aposta contra o autoscaler, e o autoscaler ganha.

Essa stack sustenta hoje mais de 25 DAGs ativas, cerca de mil tasks por dia com 0,35% de falha no último mês, e 500 dessas tasks viram pod de Go no EKS todo dia. No post tem a topologia inteira, por que MWAA como scheduler e EKS como runtime, e as outras quatro cicatrizes. Link no primeiro comentário.

#DataEngineering #Kubernetes #Airflow #Golang #SRE

---

## Variação 3 — decisão de arquitetura

Airflow é Python por natureza. Nosso trabalho pesado roda em Go. A gente não escolheu entre os dois, escolheu os dois, cada um no lugar certo.

A Harmo já roda mais de 50 microservices em Go no EKS, com observabilidade, autoscaling e secrets compartilhados. Subir o compute pesado em outro lugar só pra agradar o Airflow seria duplicar operação sem ganho. Então a divisão ficou clara: MWAA como scheduler em Python, EKS como runtime dos workers em Go.

A peça que destrava a topologia é o KubernetesPodOperator. A DAG em Python define a imagem do worker, os parâmetros e a política de retry. O MWAA chama a API do EKS via execution role e sobe o pod no cluster, mesmo sem o Airflow morar dentro dele. Cada task pesada vira um pod Go separado, que faz o trabalho, escreve em destino persistente e termina com exit code limpo.

Hoje isso é cerca de 15 mil pods em 30 dias, cuidando da coleta, do processamento e da sincronização das mais de 300 mil avaliações públicas que entram por mês na plataforma.

O Airflow fica excelente quando você o restringe ao que ele faz bem: orquestrar. Coordenação em Python, throughput em Go. Decisão de linguagem por task, feita conscientemente, não por inércia.

Topologia completa, a integração MWAA com EKS e as cinco cicatrizes que custaram tempo estão no post. Link no primeiro comentário.

#DataEngineering #Airflow #EKS #Golang #Kubernetes

---

## Variação 4 — builder / as cinco cicatrizes

Separar scheduler de runtime resolve um problema e cria cinco novos. Os cinco que custaram tempo aqui estão no post de hoje.

Quando o Airflow dispara pods Go no EKS via KubernetesPodOperator, a fronteira entre os dois sistemas é onde mora a maior parte da dor:

:: Eviction no meio da coleta. Uma execução perdeu 1.189 de 2.037 estabelecimentos quando o Karpenter drenou o nó. QoS Guaranteed e `do-not-disrupt` resolvem coisas diferentes, e você precisa dos dois.
:: O retry do Airflow reinicia do zero. Task despejada aos 90% refaz 100%. Isso transforma idempotência em pré-requisito de desenho, não em refinamento.
:: O CLI do MWAA não conhece as suas DAGs. `dags list` retornava 3 das nossas, com `ModuleNotFoundError: airflow.providers.cncf` pras outras. O container do CLI não tem o provider do Kubernetes, enquanto o scheduler parseia tudo normalmente.
:: Logs em dois lugares por construção. Com `get_logs=True` a mesma linha existe em dois log groups. Decida a fonte da verdade antes do incidente, não às 3 da manhã.
:: A DAG que consulta a AWS no parse. Montar a lista de pods no nível do módulo acopla o parse à disponibilidade do ECR e do S3, e paga essas chamadas continuamente. É dívida assumida.

A lição que atravessa todas: idempotência vale mais que retry esperto. Desenhar o worker idempotente é mais barato que configurar política de retry sofisticada que vai te morder depois.

Cada cicatriz com a mitigação que ficou de pé está no post. Link no primeiro comentário.

#Kubernetes #DataEngineering #Golang #Airflow #SRE

---

## Notas operacionais

- Recomendada: Variação 1. Foco em como a stack funciona, que é o pedido. Abre
  com narrativa e número absoluto na primeira linha, e o gancho é
  contraintuitivo: o ambiente do MWAA é o menor possível de propósito. Fecha
  com o termômetro do scheduler, que é a frase mais reaproveitável do post.
- Variação 2 abre pela war story do eviction (1.189 de 2.037 estabelecimentos).
  É a mais forte em engajamento pelo histórico, mas puxa pro incidente, não pra
  stack.
- Variação 3 é o ângulo de decisão de arquitetura, mais curta e mais alto
  nível. Boa pra audiência de liderança técnica.
- Variação 4 é a mais builder, lista as cinco cicatrizes com marcador ::. Boa
  pra quem já opera Airflow.
- Todos os números conferidos contra o post em 23/08/2026: mw1.medium, Airflow
  2.10.1, dois schedulers, workers Celery de um a cinco, mais de 25 DAGs, ~mil
  tasks/dia, 0,35% de falha no último mês, 500 pods/dia, ~15 mil pods em 30
  dias, 300 mil avaliações/mês, mais de 50 microservices Go, 1.189 de 2.037
  estabelecimentos, retries=3.
- Primeira linha narrativa. Link no primeiro comentário. Hashtags no fim, 5.
  Sem emoji, sem travessão.

### Histórico da revisão

A versão anterior, de 25/07, foi escrita quando o post ainda tinha placeholders
e avisava pra não divulgar antes de preenchê-los. Ao revisar em 23/08 apareceram
cinco problemas: os números novos do post não eram usados, a war story do
eviction estava de fora, a Variação 3 anunciava cinco gotchas e listava quatro,
os gotchas listados não eram os do post, e um deles, "OOMKilled silencioso",
não existe no post nenhum. Esse último mandaria o leitor procurar algo que não
está lá.
