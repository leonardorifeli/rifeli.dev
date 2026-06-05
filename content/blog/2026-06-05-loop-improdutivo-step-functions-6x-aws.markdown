---
title: "O loop improdutivo que multiplicou nossa conta AWS por quase 6x em quatro madrugadas"
draft: false
date: 2026-06-05T00:00:00.000Z
description: "Case real de um incidente AWS: uma regressão sutil em uma lambda fez uma Step Function reinvocar a mesma tarefa por quatro madrugadas. A conta do mês saltou quase 6x (mesmo com AWS Cost Anomaly Detection habilitado). Como contivemos, como negociamos a concessão com a AWS via Infomach e TD Synnex, e quais guard rails entraram em pé. Case público para que outros times não descubram essa categoria de falha do mesmo jeito que a gente descobriu."
comments: true
keywords: [
  "AWS Step Functions",
  "AWS Lambda",
  "case",
  "loop improdutivo",
  "States.Runtime",
  "cost incident AWS",
  "guard rail",
  "Cost Anomaly Detection",
  "FinOps",
  "Infomach",
  "como evitar loop em step functions",
  "como detectar anomalia de custo aws",
  "limite eventos step functions"
]
tags:
  - aws
  - step-functions
  - lambda
  - postmortem
  - finops
  - incidente
---

<img id="image-custom" src="/images/posts/8114554f-af51-4928-932f-a2bb01af2c38.png" alt="" />
<p id="image-legend">Custo AWS mensal: pico de março com fator próximo de 6x sobre a baseline histórica.</p>

# Introdução

Na manhã de uma segunda-feira de março, abri o dashboard de billing como de hábito e a conta AWS do mês estava quase 6x acima da baseline histórica. Nenhum alarme técnico tinha disparado. Zero impacto pra usuário final, zero perda de dado, zero degradação em serviços vizinhos. Mas o billing sangrou por 76 horas seguidas.

A Harmo é uma Plataforma Drive-to-Store que processa +10 milhões de pesquisas e +300 mil avaliações públicas por mês. Cada um desses números toca uma família de fluxos serverless. Quando um único fluxo entra em loop improdutivo, ele paga o preço pelo restante.

Case público é prática consolidada na engenharia séria de software, e blameless é o nosso padrão interno. Resolvi escrever sobre esse case, porque a topologia da falha é generalizável: quem opera Step Functions, máquinas de estado ou qualquer fluxo com loop pode tropeçar na mesma armadilha. Foi o único evento desse perfil no histórico do ambiente, e a categoria de falha não tem mais como acontecer depois das contramedidas que descrevo abaixo.

# A topologia do fluxo

O fluxo afetado é uma Step Function de coleta paginada de dados via API externa, agendada para rodar de madrugada. O desenho é trivial em pseudocódigo:

```
[Start] → [Invoke Lambda] → [Choice: isFinished?]
                              ├── true  → [Persist] → [End]
                              └── false → [Invoke Lambda]   (loop)
```

Um Choice state que retorna pra invocação da lambda enquanto `$.collector.isFinished == false`. Em operação normal, a lambda esgota a paginação da API de origem em 3 a 8 invocações por execução. Limpinho, funcionou estável por anos.

# A regressão

Numa quinta-feira, 19h05, mergeei um PR que mudou a lógica de paginação dessa lambda. Passou no review, passou nos testes existentes, passou na esteira. Não violava o contrato de I/O da função, todos os campos do payload continuavam com o shape esperado, tipos corretos, schema válido.

Sob uma condição específica de entrada (combinação rara de filtros com janela temporal), a lambda passou a retornar o seguinte payload **a cada invocação**, idêntico, sem variar entre chamadas consecutivas da mesma execução:

| Campo            | Valor    |
| ---------------- | -------- |
| `cursor`         | 0        |
| `buffer`         | 0        |
| `isFinished`     | **false** |
| `totalFiltered`  | 0        |
| `totalFetched`   | 0        |
| `pageCount`      | 1        |

Todos os sinais disponíveis indicavam ausência total de progresso: cursor não avança, nada acumulado, nada trazido, primeira página perpétua, e a chave de saída em `false`. Mas o payload era HTTP 200, bem-formado, schema-válido. Do ponto de vista do Choice state da Step Function, era instrução pra continuar. Ele continuou.

# As quatro madrugadas

Cada execução afetada consumia o teto de 25.000 eventos do histórico da Step Function antes de falhar com um erro `States.Runtime` cuja causa era literalmente `The execution reached the maximum number of history events (25000).`. Eram cerca de 8 horas e meia de loop, com a Step Function consumindo invocações Lambda (por 15min) e transições SFN em ritmo frenético até bater no limite hard da AWS. Esse teto de 25.000 eventos é quota hard de Standard Workflow, não dá pra aumentar via Service Quotas \o/.

O padrão recorreu em quatro madrugadas consecutivas, atravessando um final de semana inteiro. No total, 76 horas de recorrência intermitente em que cada ciclo entregava `States.Runtime`.

# Por que nada disparou

Três camadas falharam ao mesmo tempo, e cada uma vale comentar.

**Camada de código.** Os testes unitários da lambda validavam o shape do payload retornado. O bug não violou nenhum shape, retornou valores logicamente inconsistentes com tipos válidos. Teste de shape passa, problema de invariância não pega. Não havia teste validando "se `isFinished=false`, então deve haver evidência de progresso entre invocações".

**Camada de arquitetura.** O Choice state da Step Function fazia inspeção puramente sintática de uma única chave: `isFinished`. Não havia comparação entre estado antes e depois da invocação, nem teto de iterações. Do ponto de vista da Step Function, o sistema estava se comportando corretamente: recebeu instrução pra continuar, continuou.

**Camada de observabilidade.** Não havia alarme sobre duração de execução de Step Function, sobre número de transições por execução, nem sobre concorrência da lambda contra baseline rolling. A única linha de defesa era o sinal financeiro, que por design tem latência de consolidação de 24 a 48 horas. O Cost Anomaly Detection da AWS requer múltiplos pontos de observação pra estabelecer baseline antes de disparar. Um único evento anômalo pode não ultrapassar o threshold estatístico nos primeiros dias, foi o que aconteceu.

Toda invocação retornou 200. Nenhum erro, nenhuma exceção, nenhum stack trace. O sistema estava funcionando, no sentido mais raso da palavra.

# A detecção e a contenção

Trinta de março, segunda-feira, ~9h. Anomalia de custo identificada na revisão matinal do dashboard de billing. Em 15 minutos de investigação, correlacionei invocações da lambda com transições da Step Function, vi a assinatura do loop, conferi os payloads. Trinta minutos depois do disparo, o fluxo estava contido. No mesmo dia, root cause analysis concluída, correção preparada, deploy com validação ativa.

A partir de 31 de março, monitoramento intensificado, zero recorrência. Abril fechou exatamente na baseline histórica do ambiente. A correção foi efetiva e não havia dívida oculta.

Todo o processo, contamos com a parceria de anos com a [Infomach](https://www.infomach.com.br/), o que foi primordial para um bom sucesso.

# A frente comercial: Infomach, TD Synnex e AWS

O delta do incidente concentrou-se em três serviços. Lambda multiplicou cerca de 100x sobre a média histórica, Step Functions cerca de 50x, e CloudWatch entre 4 e 5x. Somados, o evento representou aproximadamente 80% da conta total do mês. Em quatro madrugadas.

Trabalhei com a [Infomach](https://www.infomach.com.br/), nossa parceira AWS, articulada via TD Synnex como distribuidor. O time da Infomach atuou em duas frentes em paralelo: validação técnica do diagnóstico e desenho dos guard rails que descrevo abaixo, e abertura do ticket comercial junto à AWS apresentando o postmortem completo, a janela do incidente, a causa raiz e o plano de correção já executado. A AWS reconheceu o caso e concedeu uma fração relevante do delta como crédito. Parceria excelente em ambas as pontas, durante anos (rodamos em AWS desde 2016).

A lição operacional é direta: canal AWS bem ativado vira ativo estratégico. O blameless postmortem, com root cause clara e ações corretivas P0 já concluídas, foi o que sustentou a negociação. Documento técnico bem feito é insumo de negociação, não burocracia.

# Os guard rails que entraram

Depois da contenção, o trabalho real começou. As ações P0 atacaram as três camadas que falharam.

No código, virou obrigatório teste de invariância para qualquer fluxo de paginação: se `isFinished=false`, então uma das três precisa ser verdadeira (cursor avançou, totalFetched aumentou, ou pageCount cresceu). Não é teste de shape, é teste de coerência entre invocações.

Na arquitetura, o Choice state ganhou guard rail de iterações máximas (hard stop por teto configurável por fluxo) e guard rail de progresso, em que a invocação precisa retornar evidência explícita de avanço, senão o fluxo encerra com erro de negócio. As duas proteções são complementares: o teto contém o pior caso, a invariância contém o caso comum.

Na observabilidade, três alarmes CloudWatch entraram com prioridade alta: duração de execução SFN acima do p99 histórico por fluxo, número de transições por execução acima de teto por fluxo, e concorrência da lambda versus baseline rolling de 7 dias. Latência de minutos, não de dias.

E mais duas mudanças de processo: freeze de deploy às sextas-feiras e nos últimos cinco dias do mês para pipelines billing-sensitive, e checklist obrigatório de validação D+1 após merge em SFN ou lambda de alto volume (execuções, duração, transições, custo). Janela de deploy importa: merge na quinta à noite mais execução agendada de madrugada mais final de semana na frente totalizam ~72 horas de cegueira operacional antes da primeira oportunidade de observação crítica.

Também construímos um robô diário de cost tracking rodando em EKS (CronJob Python via IRSA para credenciais AWS e Secrets Manager para o token do ClickUp). Ele posta o breakdown de custo por serviço e por dia no ClickUp e abre task automaticamente se houver anomalia. Sobre esse robô [escrevi em separado no post anterior dessa série](/blog/2026-06-03-relatorios-custo-aws-cronjob-eks/), ele virou peça central da rotina de FinOps.

# As lições que ficam

A lição central é simples e desconfortável: sucesso técnico pode mascarar falha de negócio. Toda invocação retornou 200, nenhum erro foi registrado, nenhum stack trace apareceu em lugar nenhum. Monitoramento baseado só em erros e exceções é insuficiente para fluxos que podem falhar por ausência de progresso. É preciso monitorar comportamento, não apenas sucesso sintático.

Pensa num atleta correndo numa esteira de academia: é movimento sem deslocamento. Atleta correndo na rua: movimento com deslocamento. Pela frequência cardíaca, pelo suor, pelo gasto calórico, os dois são indistinguíveis. Só o GPS responde se a pessoa saiu do lugar. Nosso fluxo tinha frequência cardíaca, tinha suor, tinha cada métrica sintática esperada no payload. O que faltava era GPS. `cursor=0`, `totalFetched=0`, `pageCount=1` era exatamente isso: indicador inequívoco de que ninguém estava saindo do lugar, ignorado porque os outros sinais estavam todos verdes. Em sistema distribuído, sinal de batimento cardíaco e sinal de deslocamento são coisas diferentes, e instrumentação madura precisa dos dois.

A segunda é que latência de sinal importa tanto quanto existência de sinal. Existia sinal de custo (mesmo que não consolidado 100% pela AWS), ele chegou com três dias de atraso. Em incidentes de consumo exponencial, três dias é a diferença entre um susto e um evento material. Sinais técnicos têm latência de minutos e devem ser primeira linha de defesa. Sinais financeiros são backstop, não primeira linha.

A terceira é mais cultural. A Step Function afetada operou de forma estável por muito tempo (desde mar/2018). Estabilidade gera familiaridade, familiaridade reduz escrutínio. Fluxos com potencial de custo exponencial merecem atenção proporcional ao seu pior caso, não à sua média histórica. Por isso entrou ação de inventário e revisão arquitetural de todos os workflows legados com potencial de loop ou custo exponencial, aplicando os mesmos guard rails onde couber.

A quarta, talvez a mais imediata pra quem está lendo: invariantes explícitas valem mais que happy path. Teste de shape confirma que os campos existem e têm o tipo certo. Teste de invariância confirma que os valores são coerentes entre si. Pra fluxos com loop de negócio, a invariante crítica é progresso. Se o fluxo diz pra continuar, algo precisa ter mudado. Esse tipo de invariante precisa ser explícita no código, no teste e no próprio desenho do fluxo.

Se você opera Step Functions ou qualquer máquina de estados com loop, dois pedidos diretos: audite hoje quais fluxos têm potencial de loop sem progresso, e veja se o sinal de defesa primário é técnico ou financeiro. Se for financeiro, você está confiando num sinal que chega com dias de atraso pra conter um evento que escala em horas.

Esse case está em público com um propósito específico: que outros times não descubram essa categoria de falha do mesmo jeito que a gente descobriu. Se uma única equipe ler isso, auditar seus fluxos de paginação ou loop, e encontrar uma armadilha equivalente antes dela cobrar, o post pagou o trabalho de escrever.

Gratidão.
