---
title: "As oito famílias de matemática que rodam por trás da Plataforma Harmo todo dia"
draft: true
date: 2026-06-17T00:00:00.000Z
description: "Continuação do post sobre o alpinista cego. Existe um cheatsheet clássico de fórmulas essenciais de data science: estatística descritiva, probabilidade, álgebra linear, cálculo, machine learning, information theory, data science essentials e séries temporais. Cada uma dessas oito famílias tem aplicação direta na operação da Plataforma Harmo, todo dia. Esse post mapeia onde cada uma mora."
comments: true
keywords: [
  "data science",
  "machine learning",
  "estatística aplicada",
  "álgebra linear",
  "correlação de Pearson",
  "gradiente descendente",
  "NLP",
  "séries temporais",
  "detecção de anomalia",
  "information theory",
  "Harmo",
  "drive-to-store",
  "matemática em produção",
  "data science aplicada"
]
tags:
  - matemática
  - ai
  - machine-learning
  - data-science
  - educação
---

<img id="image-custom" src="" alt="" />
<p id="image-legend"></p>

# Introdução

Existe um cheatsheet clássico circulando pela internet com oito famílias de fórmulas essenciais de data science: estatística descritiva, probabilidade, álgebra linear, cálculo, machine learning, information theory, data science essentials e séries temporais. Na imagem, cada caixa traz três ou quatro fórmulas em notação acadêmica limpa. A reação mais comum de quem bate os olhos é "isso é coisa de pesquisador, eu só faço CRUD".

Esse post amplia o que comecei a contar no [post do alpinista cego](/blog/2026-06-12-alpinista-cego-gradiente-descendente-ia/). Lá mostrei que uma única ferramenta de Cálculo II, o gradiente descendente, sustenta toda IA moderna. Aqui o quadro é maior. Cada uma das oito famílias do cheatsheet tem aplicação direta na operação da Plataforma Harmo, em volume que dá pra dimensionar: processamos 10 milhões de pesquisas, 1 milhão de eventos de performance de loja e 300 mil avaliações públicas por mês, em mais de 60 mil lojas físicas. Nada disso roda sem matemática trabalhando no background, mesmo quando o time que opera não chama as coisas por esses nomes.

O objetivo aqui é mapeamento, não tutorial. Por onde cada família anda na operação, e como elas se conectam pra entregar coisas concretas. Vou seguir a ordem do cheatsheet só nas primeiras seções, depois agrupo por aplicação porque na vida real as fórmulas raramente aparecem sozinhas.

# A correlação de ouro: estatística descritiva como bússola comercial

Começo pelo caso mais simples e mais importante. Numa amostra grande das lojas que a Harmo monitora, a correlação de Pearson entre nota média no Google Business Profile e pedidos de rota gerados (os cliques de "como chegar") fica estável em um ponto preciso. Cada 0,1 estrela a mais na nota média se associa, em média, a 8,8% a mais de pedidos de rota. Esse número é o que a gente chama internamente de Correlação de Ouro, e é o ponto que explica por que reputação é performance, não imagem.

A fórmula em si é trivial. Correlação de Pearson é a covariância entre as duas variáveis normalizada pelo produto dos desvios padrão de cada uma, e está na primeira página de qualquer livro de estatística. Mas a aplicação é tudo menos trivial. Descobrir esse ponto, validar que ele se mantém em diferentes segmentos de varejo, sustentar ele dentro de reunião com CFO de cliente, e usar ele como bússola pra decisão de investimento em programa de reputação. Aí mora o valor real da fórmula.

Em paralelo a Pearson, a operação usa o resto da família descritiva o tempo inteiro. Média e desvio padrão pra entender distribuição de notas dentro de uma rede de cliente, identificando lojas que destoam pra cima ou pra baixo. Variância pra calibrar quando uma diferença entre dois grupos é grande o bastante pra ser sinal e não ruído. Covariância pra rastrear como pares de variáveis se movem juntos. Estatística descritiva é o que separa "achismo de loja" de "leitura de loja", e essa diferença sustenta praticamente toda conversa estratégica entre Harmo e cliente.

# Álgebra linear e cálculo: o motor de NLP por dentro

O motor de NLP da Harmo classifica sentimento de avaliação, extrai aspectos mencionados (atendimento, produto, preço, ambiente) e dá suporte a respostas em escala. Tudo isso é álgebra linear e cálculo combinados, em arquiteturas que aprenderam a fazer essas operações em paralelo na GPU.

Cada avaliação que chega vira um vetor numérico de centenas de dimensões através de um embedding. Comparar duas avaliações pra ver se são parecidas é literalmente o cálculo do cosseno entre os vetores delas, fórmula que está no canto direito da seção "Data Science Essentials" do cheatsheet. Agrupar avaliações por similaridade pra entender padrões emergentes é distância euclidiana ou cosseno aplicados em larga escala. Identificar avaliações que poderiam ser respondidas com um mesmo template (porque tratam do mesmo tema) é busca de vizinhança no espaço de embedding.

A multiplicação de matrizes é a operação de base de tudo isso. Cada camada de um modelo neural moderno é literalmente uma matriz de pesos multiplicando uma matriz de entrada. Modelos de linguagem que rodam por trás de classificadores e extratores fazem isso milhares de vezes por inferência. Quando o cheatsheet mostra a fórmula `(AB)ij = Σ Aik · Bkj`, está descrevendo o trabalho que ocupa quase 100% do tempo de inferência do modelo. PCA e eigenvalues entram quando precisamos reduzir dimensão de features de loja, comprimindo dezenas ou centenas de métricas em um pequeno número de componentes principais que ainda carregam quase toda a variância da operação.

O cálculo entra no momento de treinar. Treinar um classificador de sentimento é minimizar uma função de erro, e minimizar uma função de erro é exatamente o gradiente descendente que descrevi no post anterior, em escala bilhões de vezes maior. Derivada parcial em cada peso da rede, retropropagada pela regra da cadeia, parâmetro por parâmetro, batch por batch. O Cálculo II da prova final virou infraestrutura silenciosa do classificador. A regra da cadeia que parecia exercício de aula virou o algoritmo de retropropagação que treina toda rede neural moderna.

# Séries temporais e detecção de anomalia: matemática que dispara alarme

A operação gera séries temporais o tempo inteiro. Volume de avaliações por hora, latência de microserviço, custo AWS por serviço por dia, NPS rolando ao longo da semana, taxa de resposta a avaliações por loja. Toda anomalia útil que disparou alarme operacional aqui dentro foi detectada por alguma combinação das três fórmulas da seção "Time Series" do cheatsheet, geralmente conversando com o z-score da seção de Data Science Essentials.

Moving average é o ponto de partida. Você compara o valor de hoje com a média rolling de 7 ou 14 dias. Se o valor escapa de uma faixa razoável, é sinal. Aplicado: o [robô diário de cost tracking](/blog/2026-06-03-relatorios-custo-aws-cronjob-eks/) usa essa lógica pra abrir task automaticamente quando custo de um serviço foge da baseline. O alarme P1 sobre concorrência de lambda contra baseline rolling de 7 dias, que entrou em pé depois do [postmortem do loop em Step Functions](/blog/2026-06-05-loop-improdutivo-step-functions-42k-aws/), é literalmente moving average aplicado em métrica de invocação.

Z-score é o irmão mais formal dessa abordagem. Normaliza o valor pelo desvio padrão da série e pergunta "quantos desvios padrão isso está fora da média?". Z-score acima de 3 é sinal forte, acima de 4 é gritante. Aplicação direta no nosso mundo: detectar avaliação suspeita (loja recebendo 50 avaliações em uma hora quando o normal seriam 5), flagrar comportamento de pesquisa anômalo, filtrar outlier antes de calcular correlação pra não contaminar a média com caso extremo.

Exponential smoothing e autocorrelação entram na previsão. Estimar quantos pedidos de rota uma loja deve gerar nas próximas duas semanas, dado o histórico dela e a sazonalidade conhecida. Capacity planning de processamento em janelas de pico, baseado em volume previsto de avaliações. Quando o time fala em "previsão suavizada", está aplicando exponential smoothing, mesmo quando ninguém chama por esse nome.

# Probabilidade e information theory: decisão sob incerteza

A última camada que vale destacar mistura as seções 2 e 6 do cheatsheet. Probabilidade e information theory são as ferramentas que sustentam decisão quando não há certeza completa, o que é praticamente sempre.

Bayes é a fórmula que atualiza crença com evidência. Estimar a probabilidade de um cliente fazer churn dado o histórico de NPS dele é Bayes aplicado. Atualizar a probabilidade de uma avaliação ser falsa dado um padrão suspeito de IP, conta e timestamp é Bayes aplicado. A fórmula é compacta, três símbolos arrumados em uma razão, mas a aplicação cobre uma boa parte do nosso trabalho de classificação probabilística.

Valor esperado é mais simples e igualmente potente. Se uma intervenção em loja tem 30% de chance de gerar 10 pedidos de rota adicionais e 70% de chance de gerar 2, o valor esperado é 4,4 pedidos por intervenção. Multiplica isso por escala de milhares de lojas e você tem decisão de investimento orçamentário ancorada em matemática, não em achismo. Aparece em conversa de pricing, de roadmap de feature, de priorização de cliente.

Entropy, cross-entropy e KL-divergence são onde a coisa fica densa, mas valem o esforço. Entropia mede o quão incerto é um sistema. Cross-entropy é o que se minimiza quando se treina classificador (é a função de erro padrão pra problema com múltiplas classes, então todo classificador de sentimento que rodou aqui dentro está minimizando cross-entropy debaixo dos panos). KL-divergence compara distribuições, então perguntar "a distribuição de sentimento da loja A se parece com a da loja B?" é uma KL-divergence aplicada, com leitura comercial direta. Mutual information vira ferramenta de feature selection: qual variável carrega mais informação sobre o que queremos prever, e qual é redundante?

Information theory parece esotérica até o momento em que você precisa selecionar features pra um modelo com centenas de candidatas. Aí ela vira a única coisa que funciona em escala.

# Fechamento

O cheatsheet tem oito caixinhas. Cada uma é uma família de ferramenta matemática. A leitura mais útil dele não é "preciso decorar tudo isso pra fazer data science". É "cada uma dessas famílias tem aplicação concreta em produção, e a maioria delas é exatamente o que sustenta o que você consome hoje em qualquer plataforma SaaS séria".

Na Harmo, a estatística descritiva sustenta a Correlação de Ouro que orienta a proposta de valor inteira. A álgebra linear e o cálculo sustentam o motor de NLP que processa avaliações em escala. As séries temporais sustentam os alarmes operacionais que evitam que incidente vire desastre. A probabilidade e a information theory sustentam a decisão sob incerteza que define onde investir o tempo do time e o orçamento dos clientes. Cada caixinha do cheatsheet aparece em algum momento do dia operacional, mesmo quando ninguém chama as coisas por esses nomes.

Fechando a amarração do post do alpinista cego: aquele aluno de Cálculo II que torcia o nariz pra derivada parcial estava aprendendo o motor de uma das oito famílias. As outras sete, ele já viu, em Cálculo I, em Estatística, em Álgebra Linear, em Probabilidade. Tudo o que parecia abstração de prova é, dez anos depois, infraestrutura silenciosa do que ele usa pra trabalhar. A diferença entre o aluno que aproveita isso na carreira e o que não aproveita é só saber onde olhar.

Pergunta de fechamento, e essa é genuína: qual dessas oito famílias você tem aplicado em produção sem enxergar como matemática? Eu sei que tem aplicação que aparece sem o nome ser dito, regra de negócio que esconde uma probabilidade condicional, métrica de dashboard que esconde uma moving average, threshold de alarme que esconde um z-score. Curioso pra mapear as aparições disfarçadas que vocês encontram no dia a dia, e os comentários abaixo costumam ser bom lugar pra esse tipo de troca.
