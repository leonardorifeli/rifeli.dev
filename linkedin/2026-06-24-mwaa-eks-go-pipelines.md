# MWAA orquestrando workers em Go no EKS

Três variações para o LinkedIn. Post no blog datado 2026-06-24. Link do blog no primeiro comentário. Primeira linha sempre narrativa, nunca bloco de código.

Primeiro comentário (qualquer variação):

> Post completo: https://rifeli.dev/blog/2026-06-24-airflow-eks-go-orquestracao-pipelines/

---

## Variação 1 — decisão de arquitetura (recomendada)

Airflow é Python por natureza. Nosso trabalho pesado roda em Go. A gente não escolheu entre os dois, escolheu os dois, cada um no lugar certo.

A Harmo já roda mais de 50 microservices em Go no EKS, com observabilidade, autoscaling e secrets compartilhados. Subir o compute pesado em outro lugar só pra agradar o Airflow seria duplicar operação sem ganho. Então a divisão ficou clara: MWAA como scheduler em Python, EKS como runtime dos workers em Go.

A peça que destrava a topologia é o KubernetesPodOperator. A DAG em Python define a imagem do worker, os parâmetros e a política de retry. O MWAA chama a API do EKS via execution role e sobe o pod no cluster, mesmo sem o Airflow morar dentro dele. Cada task pesada vira um pod Go separado, que faz o trabalho, escreve em destino persistente e termina com exit code limpo.

O Airflow vira excelente quando você o restringe ao que ele faz bem: orquestrar. Coordenação em Python, throughput em Go. Decisão de linguagem por task, feita conscientemente, não por inércia.

Topologia completa, integração MWAA com EKS e os gotchas que custaram tempo no blog. Link no primeiro comentário.

#DataEngineering #Airflow #EKS #Golang #Kubernetes

---

## Variação 2 — insight contrário / Airflow no papel certo

A maioria das empresas trata Airflow mais Python como um fim em si. Pra quem opera workload pesado em Kubernetes, isso é deixar performance na mesa.

O Airflow assume Python no plano da orquestração, e Python sustenta a coordenação muito bem. O problema é quando o trabalho pesado também fica preso ali. Coleta paginada, sincronização com APIs externas, escrita em massa em banco: isso é I/O concorrente em volume, e é onde Go entrega throughput de outro patamar com latência previsível e container pequeno.

A decisão foi manter o Python só onde ele ganha. Worker em Python pra DataFrame com pandas e ML clássico com scikit-learn. Worker em Go pro trabalho pesado de I/O. O scheduler coordena, os pods executam. Cada task escolhe a linguagem certa, e o Airflow nunca vira gargalo de runtime porque não é runtime.

Restringir uma ferramenta ao que ela faz bem costuma ser arquitetura mais limpa do que esticá-la pra tudo. Airflow brilha como scheduler exatamente quando para de tentar ser o executor.

Por que MWAA pro scheduler, por que Go pros workers e a topologia inteira no rifeli.dev. Link nos comentários.

#DataEngineering #Airflow #Golang #CloudArchitecture #Kubernetes

---

## Variação 3 — builder / os gotchas

Separar scheduler de runtime resolve um problema e cria cinco novos. Os cinco que custaram tempo aprender estão no post de hoje.

Quando o Airflow dispara pods Go no EKS via KubernetesPodOperator, a fronteira entre os dois sistemas vira a fonte da maior parte da dor:

:: OOMKilled silencioso. Batch chega 5x maior que o esperado, o pod morre, e o Airflow vê só exit code 137. Request e limit de memória bem dimensionados não são opcionais.
:: Retry contra idempotência. Se o Airflow reenvia a task depois de um timeout, o worker em Go precisa ser idempotente, ou você duplica dado no destino. Chave de execução única resolve.
:: Log em dois lugares. CloudWatch captura o stdout do pod, o Airflow também guarda. Defina onde fica a fonte da verdade antes do incidente, não durante.
:: Eviction no meio da DAG. Rolling update de node despeja pods. Task longa quebra. Idempotência com retry forte, ou tasks curtas que sobrevivem.

A lição que atravessa todas: idempotência é mais importante que retry esperto. Vale mais desenhar o worker idempotente do que configurar política de retry sofisticada que vai te morder depois.

Os cinco gotchas com a mitigação de cada um no blog. Link no primeiro comentário.

#DataEngineering #Kubernetes #Golang #Airflow #SRE

---

## Notas operacionais

- Recomendada: Variação 1. Ancora no número concreto que já está no post (50+ microservices Go) e no hook "escolheu os dois".
- ATENÇÃO: o post no blog ainda está com PLACEHOLDERs e sem o número absoluto de DAGs ativas / pods disparados por dia / volume de dados. Assim que você preencher, a Variação 1 fica mais forte abrindo com esse número (ex.: "X DAGs sobem Y pods Go por dia"). Hoje evitei inventar.
- Variação 2 puxa o ângulo contrário (Airflow no papel restrito), boa pra audiência sênior/arquiteto.
- Variação 3 é a mais builder, lista os gotchas com marcador ::. Boa pra engenheiro que já mexe com Airflow.
- Não divulgar enquanto os PLACEHOLDERs do post não forem resolvidos, senão o leitor cai num post incompleto.
- Primeira linha narrativa. Link no primeiro comentário. Hashtags no fim, 4 a 5. Sem emoji, sem travessão.
