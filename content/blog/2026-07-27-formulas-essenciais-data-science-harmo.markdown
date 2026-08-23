---
title: "As oito famílias de matemática que rodam por trás da Plataforma Harmo todo dia"
draft: false
date: 2026-07-27T00:00:00.000Z
description: "Continuação do post sobre o alpinista no nevoeiro. Existe um cheatsheet clássico de fórmulas essenciais de data science: estatística descritiva, probabilidade, álgebra linear, cálculo, machine learning, information theory, data science essentials e séries temporais. Cada uma dessas oito famílias tem aplicação direta na operação da Plataforma Harmo, todo dia. Esse post mapeia onde cada uma mora."
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

<img id="image-custom" src="/images/posts/e7834d8b-c618-4db0-a1be-d685e1c8ad67.png" alt="" />
<p id="image-legend">As oito famílias do cheatsheet não param na lousa: descem até a loja física e viram fluxo de gente na porta.</p>

## Introdução

Existe um cheatsheet clássico circulando pela internet com oito famílias de fórmulas essenciais de data science: estatística descritiva, probabilidade, álgebra linear, cálculo, machine learning, information theory, data science essentials e séries temporais. Na imagem, cada caixa traz três ou quatro fórmulas em notação acadêmica limpa. A reação mais comum de quem bate os olhos é "isso é coisa de pesquisador, eu só faço CRUD".

Esse post amplia o que comecei a contar no [post do alpinista no nevoeiro](/blog/2026-06-19-alpinista-nevoeiro-gradiente-descendente-ia/). Lá mostrei que uma única ferramenta de Cálculo II, o gradiente descendente, sustenta o treinamento de grande parte da IA moderna. Aqui o quadro é maior. Cada uma das oito famílias do cheatsheet tem aplicação direta na operação da Plataforma Harmo, em volume que dá pra dimensionar: processamos 10 milhões de pesquisas e 300 mil avaliações públicas por mês, em mais de 60 mil lojas físicas. Nada disso roda sem matemática trabalhando no background, mesmo quando o time que opera não chama as coisas por esses nomes.

O objetivo aqui é mapeamento, não tutorial. Por onde cada família anda na operação, e como elas se conectam pra entregar coisas concretas. Vou seguir a ordem do cheatsheet só nas primeiras seções, depois agrupo por aplicação porque na vida real as fórmulas raramente aparecem sozinhas. Pra não perder o fio, o mapa das oito caixinhas contra o que aparece nas seções abaixo:

| Família do cheatsheet | Onde ela aparece neste post |
| --------------------- | --------------------------- |
| Estatística descritiva | Correlação de Ouro, média e desvio padrão de nota dentro da rede, variância, covariância |
| Probabilidade | Bayes como forma de raciocinar sobre churn e avaliação falsa, valor esperado em decisão de investimento |
| Álgebra linear | Embedding de avaliação, multiplicação de matrizes no motor de NLP, redução de dimensão |
| Cálculo | Gradiente descendente e regra da cadeia no treino do classificador de sentimento |
| Machine learning | O próprio classificador de sentimento do motor de NLP, do treino à inferência |
| Information theory | Entropia, cross-entropy no treino, comparação de distribuição, seleção de feature |
| Data science essentials | Similaridade de cosseno entre embeddings, z-score, leitura de outlier |
| Séries temporais | Moving average nos alarmes de custo e de concorrência, suavização e previsão |

## A correlação de ouro: estatística descritiva como bússola comercial

Começo pelo caso mais simples e mais importante. Nas análises internas que deram origem ao que a gente chama de Correlação de Ouro, loja com nota média mais alta no Google Business Profile também aparece com mais pedidos de rota gerados (os cliques de "como chegar"). E o efeito observado é grande o bastante pra ninguém ignorar: a cada 0,1 estrela adicional, aparece em média uma diferença de 8,8% nos pedidos de rota.

Vale separar as duas medidas, porque elas são confundidas o tempo todo, inclusive por mim em conversa apressada. Pearson mede a força e a direção da associação linear, num coeficiente que vive entre −1 e 1. Ele não cospe percentual por 0,1 estrela. O número de 8,8% vem da análise do tamanho do efeito, não do coeficiente. São leituras complementares que respondem perguntas diferentes: uma diz o quanto as duas variáveis andam juntas, a outra diz o quanto isso pesa na prática. Juntas, elas mostram que reputação não é apenas imagem: ela anda junto com indicador concreto de performance.

A fórmula em si é trivial. Correlação de Pearson é a covariância entre as duas variáveis normalizada pelo produto dos desvios padrão de cada uma, e está na primeira página de qualquer livro de estatística:

<div class="formula">
$$ r_{xy} = \frac{\operatorname{cov}(X,Y)}{\sigma_X\,\sigma_Y} = \frac{\sum_{i=1}^{n}(x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i-\bar{x})^2}\;\sqrt{\sum_{i=1}^{n}(y_i-\bar{y})^2}} $$
</div>
<p class="formula-nota">Aqui \(x\) é a nota média da loja e \(y\) o volume de pedidos de rota. O numerador mede se as duas variáveis se afastam da própria média na mesma direção; o denominador tira a escala, e é por isso que o resultado sempre cai entre −1 e 1.</p>

Mas a aplicação é tudo menos trivial. Descobrir esse ponto, validar que ele se mantém em diferentes segmentos de varejo, sustentar ele dentro de reunião com CFO de cliente, e usar ele como bússola pra decisão de investimento em programa de reputação. Aí mora o valor real da fórmula.

Em paralelo a Pearson, a operação usa o resto da família descritiva o tempo inteiro. Média e desvio padrão pra entender distribuição de notas dentro de uma rede de cliente, identificando lojas que destoam pra cima ou pra baixo. Variância pra dimensionar o quanto os dados se espalham em volta da média, que é o insumo que depois alimenta erro padrão, intervalo de confiança e teste.

<div class="formula">
$$ \sigma^2 = \frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^2 \qquad \operatorname{cov}(X,Y) = \frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})(y_i-\bar{y}) $$
</div>
<p class="formula-nota">Variância e covariância lado a lado, na forma populacional. A segunda é a primeira com duas variáveis em vez de uma: troque o quadrado pelo produto dos dois desvios e a mesma conta passa a medir movimento conjunto. Em amostra, o divisor vira \(n-1\).</p>

 Ela sozinha não responde se a diferença entre dois grupos é sinal ou ruído, mas sem ela não dá nem pra fazer a pergunta direito. Covariância pra rastrear como pares de variáveis se movem juntos. Estatística descritiva é o que separa "achismo de loja" de "leitura de loja", e essa diferença sustenta praticamente toda conversa estratégica entre Harmo e cliente.

## Álgebra linear e cálculo: o motor de NLP por dentro

O motor de NLP da Harmo classifica sentimento de avaliação, extrai aspectos mencionados (atendimento, produto, preço, ambiente) e dá suporte a respostas em escala. Tudo isso é álgebra linear e cálculo combinados, em arquiteturas que aprenderam a fazer essas operações em paralelo na GPU.

Cada avaliação que chega vira um vetor numérico de centenas de dimensões através de um embedding. Comparar duas avaliações pra ver se são parecidas pode ser feito calculando a similaridade de cosseno entre os vetores delas:

<div class="formula">
$$ \operatorname{sim}(\mathbf{a},\mathbf{b}) = \cos\theta = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert} = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2}\;\sqrt{\sum_{i=1}^{n} b_i^2}} $$
</div>
<p class="formula-nota">Note que é a mesma estrutura da correlação de Pearson: produto no numerador, normalização pelas magnitudes no denominador. A diferença é que Pearson centra os dados na média antes, e o cosseno não. Por isso ele mede ângulo entre vetores e ignora o tamanho deles, que é exatamente o que se quer quando uma avaliação é longa e a outra curta.</p>

 Agrupar avaliações por similaridade pra entender padrões emergentes cai no mesmo terreno: distância euclidiana ou cosseno aplicados em larga escala, e qual das duas usar depende de como o espaço vetorial foi construído.

<div class="formula">
$$ d(\mathbf{a},\mathbf{b}) = \sqrt{\sum_{i=1}^{n}(a_i-b_i)^2} $$
</div>
<p class="formula-nota">A euclidiana mede distância absoluta entre dois pontos; o cosseno mede direção. Duas avaliações sobre o mesmo assunto, uma detalhada e outra em duas linhas, ficam longe na euclidiana e perto no cosseno.</p>

 Identificar avaliações que poderiam ser respondidas com um mesmo template (porque tratam do mesmo tema) é busca de vizinhança no espaço de embedding.

A multiplicação de matrizes é a operação de base de tudo isso. Cada camada de um modelo neural moderno tem, no núcleo, uma matriz de pesos multiplicando uma matriz de entrada. Modelos de linguagem que rodam por trás de classificadores e extratores fazem isso milhares de vezes por inferência. A fórmula é esta, e ela descreve uma das operações que dominam o custo computacional da inferência desses modelos:

<div class="formula">
$$ (AB)_{ij} = \sum_{k=1}^{n} A_{ik}\,B_{kj} $$
</div>
<p class="formula-nota">Uma multiplicação de matrizes de tamanho \(n\) custa na ordem de \(n^3\) operações na forma ingênua. É essa cúbica que explica por que inferência de modelo grande é caro, e por que GPU existe.</p>

 E quando o problema é o oposto, reduzir dimensão em vez de multiplicá-la, PCA e eigenvalues são o caminho clássico da família: comprimir dezenas ou centenas de métricas de loja em componentes que preservam a parcela de variância definida como suficiente pra aquela análise. Quanto de variância sobra não é dado da natureza, depende de quantos componentes você mantém e do threshold que decidiu adotar.

O cálculo entra no momento de treinar. Treinar um classificador de sentimento é minimizar uma função de erro, e minimizar uma função de erro é exatamente o gradiente descendente que descrevi no post anterior, repetido numa escala que seria impossível acompanhar manualmente. Derivada parcial em cada peso da rede, retropropagada pela regra da cadeia, parâmetro por parâmetro, batch por batch.

<div class="formula">
$$ \theta_{t+1} = \theta_t - \eta\,\nabla_\theta L(\theta_t) \qquad \frac{\partial L}{\partial w} = \frac{\partial L}{\partial a}\cdot\frac{\partial a}{\partial z}\cdot\frac{\partial z}{\partial w} $$
</div>
<p class="formula-nota">À esquerda, o passo do gradiente descendente: ande na direção contrária à do gradiente, num tamanho de passo \(\eta\). À direita, a regra da cadeia, que é como o erro medido na saída chega até um peso lá no meio da rede. A retropropagação é essa multiplicação aplicada camada a camada, de trás pra frente.</p>

 O Cálculo II da prova final virou infraestrutura silenciosa do classificador. A regra da cadeia que parecia exercício de aula virou o algoritmo de retropropagação que treina as redes neurais modernas.

## Séries temporais e detecção de anomalia: matemática que dispara alarme

A operação gera séries temporais o tempo inteiro. Volume de avaliações por hora, latência de microserviço, custo AWS por serviço por dia, NPS rolando ao longo da semana, taxa de resposta a avaliações por loja. Boa parte das anomalias que disparam alarme operacional aqui dentro sai de alguma combinação de três fórmulas dessa família, quase sempre com uma comparação contra baseline em cima.

Moving average é o ponto de partida. Você compara o valor de hoje com a média rolling de 7 ou 14 dias. Se o valor escapa de uma faixa razoável, é sinal.

<div class="formula">
$$ \mathrm{MA}_t = \frac{1}{k}\sum_{i=1}^{k} x_{t-i} \qquad \Delta_t = \frac{x_t - \mathrm{MA}_t}{\mathrm{MA}_t} $$
</div>
<p class="formula-nota">À esquerda a média dos \(k\) períodos anteriores; à direita o desvio percentual do valor de hoje contra ela. É literalmente o que os nossos alarmes calculam, com \(k = 7\) e limite em \(\Delta_t > 0{,}5\).</p>

 Aplicado: o [robô diário de cost tracking](/blog/2026-06-03-relatorios-custo-aws-cronjob-eks/) compara o custo do dia com a média dos 7 dias anteriores e abre task automaticamente quando um serviço estoura 50% acima dela, com piso absoluto em dólar pra não alarmar sobre centavos. O alarme sobre concorrência de lambda contra baseline rolling de 7 dias, que ficou de pé depois do [postmortem do loop em Step Functions](/blog/2026-06-05-loop-improdutivo-step-functions-6x-aws/), é moving average aplicado em métrica de invocação. Nos dois casos o mecanismo é desvio percentual contra a média móvel, não coisa mais sofisticada que isso.

Z-score é o irmão mais formal dessa abordagem. Normaliza o valor pelo desvio padrão da série e pergunta "quantos desvios padrão isso está fora da média?".

<div class="formula">
$$ z_t = \frac{x_t - \mu}{\sigma} $$
</div>
<p class="formula-nota">A diferença entre esta fórmula e a de cima é o denominador, e é ela que separa as duas coisas: dividir pela média dá desvio percentual, dividir pelo desvio padrão dá z-score. Só a segunda é comparável entre séries de escalas diferentes.</p>

 A distinção importa na hora de nomear o que você tem: comparar valor contra baseline só vira z-score quando você divide pelo desvio padrão, e a maior parte dos alarmes que citei acima para no desvio percentual mesmo. Em série suficientemente estável, a gente usa valor acima de 3 como sinal forte e acima de 4 como caso extremo. É heurística operacional, não regra universal, e em série com cauda pesada ou sazonalidade forte esses cortes enganam. Onde isso encaixa no nosso mundo: detectar avaliação suspeita (loja recebendo 50 avaliações em uma hora quando o normal seriam 5), flagrar comportamento de pesquisa anômalo, investigar caso extremo antes de calcular correlação, separando erro de coleta de variação legítima pra não distorcer a leitura. Esse último ponto merece cuidado: loja que explodiu em avaliação porque tomou fraude é uma coisa, loja que explodiu porque abriu num shopping novo é outra, e jogar as duas no mesmo filtro automático é jogar informação fora.

Exponential smoothing e autocorrelação entram na previsão. Estimar quantos pedidos de rota uma loja deve gerar nas próximas duas semanas, dado o histórico dela e a sazonalidade conhecida.

<div class="formula">
$$ s_t = \alpha\,x_t + (1-\alpha)\,s_{t-1} \qquad \rho_k = \frac{\sum_{t=k+1}^{n}(x_t-\bar{x})(x_{t-k}-\bar{x})}{\sum_{t=1}^{n}(x_t-\bar{x})^2} $$
</div>
<p class="formula-nota">A suavização exponencial dá peso decrescente ao passado, e \(\alpha\) decide o quanto o valor de hoje manda na estimativa. A autocorrelação é a correlação da série com ela mesma deslocada em \(k\) períodos: é assim que sazonalidade semanal aparece como pico em \(k = 7\).</p>

 Capacity planning de processamento em janelas de pico, baseado em volume previsto de avaliações. Quando o time fala em "previsão suavizada", está aplicando exponential smoothing, mesmo quando ninguém chama por esse nome.

## Probabilidade e information theory: decisão sob incerteza

A última camada que vale destacar mistura duas famílias: probabilidade e information theory, as ferramentas que sustentam decisão quando não há certeza completa, o que é praticamente sempre.

Bayes formaliza uma ideia que aparece o tempo inteiro em decisão sob incerteza: você parte de uma estimativa anterior e atualiza ela quando chega evidência nova. Estimar a probabilidade de um cliente fazer churn dado o histórico de NPS dele é um problema desse formato. Atualizar a probabilidade de uma avaliação ser falsa dado um padrão suspeito de IP, conta e timestamp também. Uma ressalva que eu mesmo já atropelei: o modelo cuspir uma probabilidade condicional no final não significa que ele seja bayesiano por dentro. Bayes aqui é o modo de raciocinar, não a descrição da implementação. A fórmula é compacta, três símbolos arrumados em uma razão, e esse modo de raciocinar cobre boa parte do nosso trabalho de classificação probabilística.

<div class="formula">
$$ P(A \mid B) = \frac{P(B \mid A)\,P(A)}{P(B)} $$
</div>
<p class="formula-nota">Lendo da direita pra esquerda: você tinha uma crença inicial \(P(A)\), chegou a evidência \(B\), e a razão ajusta essa crença conforme a evidência é mais ou menos esperada. Aplicado a avaliação falsa: \(A\) é "a avaliação é fraudulenta" e \(B\) é o padrão suspeito de IP, conta e horário.</p>


Valor esperado é mais simples e igualmente potente. Se uma intervenção em loja tem 30% de chance de gerar 10 pedidos de rota adicionais e 70% de chance de gerar 2, o valor esperado é 4,4 pedidos por intervenção.

<div class="formula">
$$ E[X] = \sum_{i} p_i\,x_i = 0{,}3 \times 10 + 0{,}7 \times 2 = 4{,}4 $$
</div>
<p class="formula-nota">Toda a força dessa fórmula está em obrigar você a escrever a probabilidade que já estava na sua cabeça. Depois de escrita, ela pode ser discutida, e é aí que a conversa sai do achismo.</p>

 Multiplica isso por escala de milhares de lojas e você tem decisão de investimento orçamentário ancorada em matemática, não em achismo. Aparece em conversa de pricing, de roadmap de feature, de priorização de cliente.

Entropy, cross-entropy e KL-divergence são onde a coisa fica densa, mas valem o esforço. Entropia mede o quão incerto é um sistema.

<div class="formula">
$$ H(p) = -\sum_{i} p_i \log p_i \qquad H(p,q) = -\sum_{i} p_i \log q_i \qquad D_{\mathrm{KL}}(p \parallel q) = \sum_{i} p_i \log \frac{p_i}{q_i} $$
</div>
<p class="formula-nota">As três são a mesma soma com peças trocadas. A entropia usa a distribuição contra si mesma; a cross-entropy troca o segundo termo pela distribuição prevista, e é isso que a torna função de erro; a KL é a diferença entre as duas, ou seja o custo de usar \(q\) quando a verdade é \(p\). Vale reparar que ela não é simétrica: trocar \(p\) e \(q\) de lugar muda o número.</p>

 Cross-entropy é uma das funções de erro mais usadas no treinamento de classificador com múltiplas classes; nos classificadores neurais de sentimento, é ela que o treino minimiza, debaixo dos panos. KL-divergence não é medida simétrica de semelhança: ela mede o quanto uma distribuição diverge de uma distribuição de referência, e a ordem importa, porque KL de A pra B não dá o mesmo número que KL de B pra A. Perguntar "o quanto a distribuição de sentimento da loja A se afasta da distribuição da rede dela?" é o tipo de pergunta que essa família responde, com leitura comercial direta. Quando o que você quer é comparar duas lojas de igual pra igual, aí é outra métrica, e a escolha muda a interpretação do resultado. Mutual information vira ferramenta de feature selection: qual variável carrega mais informação sobre o que queremos prever, e qual é redundante?

<div class="formula">
$$ I(X;Y) = \sum_{x}\sum_{y} p(x,y) \log \frac{p(x,y)}{p(x)\,p(y)} $$
</div>
<p class="formula-nota">O termo dentro do logaritmo compara a distribuição conjunta com o que ela seria se as duas variáveis fossem independentes. Quando dá zero, a variável não diz nada sobre o alvo. Note que é uma KL disfarçada, entre a conjunta real e a conjunta hipotética das independentes.</p>


Information theory parece esotérica até o momento em que você precisa selecionar features pra um modelo com centenas de candidatas. Aí ela vira ferramenta especialmente útil pra separar quais variáveis carregam informação relevante sobre o que você quer prever e quais são redundância cara de carregar. Registro honesto: aqui isso é aplicação possível da família, não etapa fixa do pipeline de hoje.

## Fechamento

O cheatsheet tem oito caixinhas. Cada uma é uma família de ferramenta matemática. A leitura mais útil dele não é "preciso decorar tudo isso pra fazer data science". É "cada uma dessas famílias tem aplicação concreta em produção, e a maioria delas é exatamente o que sustenta o que você consome hoje em qualquer plataforma SaaS séria".

Na Harmo, a estatística descritiva sustenta a Correlação de Ouro que orienta a proposta de valor inteira. A álgebra linear e o cálculo sustentam o motor de NLP que processa avaliações em escala. As séries temporais sustentam os alarmes operacionais que evitam que incidente vire desastre. A probabilidade e a information theory organizam a decisão sob incerteza que define onde investir o tempo do time e o orçamento dos clientes. Cada caixinha do cheatsheet aparece em algum momento do dia operacional, mesmo quando ninguém chama as coisas por esses nomes.

Fechando a amarração do post do alpinista no nevoeiro: aquele aluno de Cálculo II que torcia o nariz pra derivada parcial estava aprendendo o motor de uma das oito famílias. As outras sete, ele já viu, em Cálculo I, em Estatística, em Álgebra Linear, em Probabilidade. Tudo o que parecia abstração de prova é, dez anos depois, infraestrutura silenciosa do que ele usa pra trabalhar. A diferença entre o aluno que aproveita isso na carreira e o que não aproveita é só saber onde olhar.

Qual dessas oito famílias você aplica em produção sem enxergar como matemática? Aparição disfarçada é o caso comum: regra de negócio que esconde uma probabilidade condicional, métrica de dashboard que esconde uma moving average, threshold de alarme que esconde uma comparação contra baseline. Rastrear essas é o exercício mais útil que o cheatsheet permite.
