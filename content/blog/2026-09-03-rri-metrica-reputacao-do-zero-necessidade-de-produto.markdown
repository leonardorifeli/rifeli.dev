---
title: "A métrica que não existia: como tiramos o RRi do zero, na notação"
draft: true
date: 2026-09-03T00:00:00.000Z
description: "Uma necessidade de produto chegou sem métrica que a resolvesse: média de estrelas não distingue loja que era boa de loja que é boa. Não tinha o que comprar, então a gente escreveu a matemática. Essa é a jornada do RRi, do primeiro rascunho em notação ao índice reescrito por econometristas, com as propriedades que exigimos antes da fórmula, o que a álgebra devolveu quando olhamos de novo, o critério explícito que substituiu o chute, e o que sobrou depois que o produto morreu."
comments: true
keywords: [
  "métrica proprietária",
  "índice de reputação",
  "engenharia de métricas",
  "média ponderada",
  "decaimento temporal",
  "econometria aplicada",
  "estatística aplicada",
  "Go",
  "reputação online",
  "drive-to-store",
  "produto e matemática",
  "Harmo"
]
tags:
  - matemática
  - data-science
  - go
  - engenharia
  - produto
---

## Introdução

Entre setembro de 2020 e dezembro de 2022 eu rodei mês a mês a série histórica de uma métrica de reputação que não existia antes da gente escrever. Não tinha fornecedor, não tinha paper pronto pra aplicar, não tinha campo na API do Google esperando pela resposta. Tinha uma necessidade de produto clara, um banco com milhões de avaliações e uma pergunta que a média aritmética não respondia.

O RRi morreu. E eu voltaria a fazer tudo de novo, porque o que ficou na empresa não foi o número, foi a capacidade de pegar uma necessidade de produto e atacar com matemática própria, do zero, sem esperar que alguém publicasse a solução primeiro.

## A necessidade chegou sem métrica

Cliente enterprise de varejo físico não pergunta qual é a nota dele. Ele já sabe a nota. Ele pergunta onde agir na segunda-feira, em qual das centenas de lojas, e por quê.

Média de estrelas não responde isso, por dois motivos. O primeiro é tempo. Uma loja com 4,7 formada por avaliações de 2018 e uma loja com 4,7 formada por avaliações do mês passado são a mesma linha na planilha e não são a mesma loja. A primeira tem um estoque antigo que ninguém confere mais. A segunda tem gente entrando hoje. Quem opera loja sabe a diferença, e a média não sabe.

O segundo é volume. Loja com 12 avaliações e loja com 30 mil aparecem com a mesma autoridade numa tabela ordenada por nota. A lei dos pequenos números faz a nota de quem tem pouco volume chicotear: uma avaliação de 1 estrela num universo de 12 derruba a média em quase meio ponto, e no universo de 30 mil não move o terceiro decimal. Ordenar lojas por média é, em boa parte, ordenar lojas por tamanho de amostra.

A conclusão foi que a gente precisava de uma medida diferente, e que essa medida não existia pronta. Reputação não é média, é estoque. Um acumulado de tudo que já foi dito sobre a loja, com cada avaliação valendo menos conforme envelhece. Isso é uma frase de produto. Virar número é outra história.

## Antes da fórmula, as propriedades

A parte da jornada que eu recomendo pra qualquer time que vá construir métrica própria é essa, e ela vem antes de qualquer símbolo: escrever o que a métrica precisa fazer, e escrever também o que vai atrapalhar.

O que a gente exigiu: refletir o estoque de reputação e não a média; decair a importância de cada avaliação no tempo; ter frequência diária, pra dar leitura acionável e não relatório trimestral; permitir agregação temporal e setorial, pra comparar loja com loja, setor com setor, e loja com o próprio setor; e considerar se a avaliação tem texto, porque avaliação escrita carrega informação que estrela sozinha não carrega.

E o que a gente sabia que ia atrapalhar: valor faltante em volume alto; heterogeneidade entre estabelecimentos; heterogeneidade entre setores, porque a régua de nota de restaurante não é a régua de nota de hotel; sazonalidade semanal, porque fim de semana avalia diferente de terça-feira; e interpretabilidade. Guarde esse último item, ele decide o final da história.

Essa lista de dez linhas fez mais pela métrica do que qualquer decisão técnica que veio depois. É ela que transforma "queremos medir reputação de verdade" em critério de aceite.

## O primeiro rascunho, escrito à mão

Com as propriedades na mesa, escrevi a primeira versão. O peso de cada avaliação e o índice final ficaram assim, com $s_i$ o escore da avaliação, $\Delta t_i$ o tempo decorrido em dias até a data de referência, $N$ o total de avaliações do conjunto e $\tau_i$ valendo 1 quando a avaliação tem texto:

$$ w_i = \frac{\ln(s_i + N + \tau_i)}{\Delta t_i} \qquad\qquad \mathrm{RRi} = 2 \cdot \frac{\sum_i s_i w_i}{\sum_i w_i} $$

Cada pedaço responde a um item da lista. Média ponderada porque o acumulado tem que somar tudo. Peso caindo com o tempo porque avaliação velha importa menos. Logaritmo pra achatar escala. Bônus pra quem escreveu texto. E um dois no fim pra jogar o resultado numa faixa de 0 a 10, que é uma escala que soa mais natural pra quem lê dashboard.

Virou um microserviço em Go que, por motivos que a minha vaidade da época explica melhor que eu, se chamava Wolfram-Alpha. Ele expunha o índice em três níveis de agregação, estabelecimento, grupo e cliente, e passou a rodar em produção.

Esse é o ponto da jornada que eu quero destacar antes de contar o que deu errado: em poucas semanas a gente saiu de uma insatisfação com a média de estrelas pra um índice diário calculado sobre a base inteira, servido por HTTP, consumido por relatório. Sem contratar ninguém, sem esperar seis meses e sem comprar nada. Métrica própria é acessível. O caro não é começar.

## O que a álgebra devolveu quando olhei de novo

O caro é revisar. E revisando aquela fórmula com calma, anos depois, dá pra ver três coisas que a intuição não pegou. Vale escrever porque são erros que qualquer um comete na primeira métrica.

O escore aparece dentro do próprio peso. Logaritmo é monotônico crescente, então avaliação de 5 estrelas pesa mais que avaliação de 1 estrela pelo fato de ser 5 estrelas. Numa loja com 5 avaliações, o peso de uma nota 5 fica 23,2% acima do peso de uma nota 1. A regra que eu levo daí é curta: a grandeza que você mede não pode aparecer no peso com que você a mede.

O $N$, que é o total de avaliações do conjunto, é a mesma constante pra todas as avaliações do cálculo. Somar constante de conjunto dentro de um logaritmo que deveria diferenciar itens individuais faz o escore sumir do peso conforme a base cresce: aquela diferença de 23,2% com 5 avaliações cai pra 0,83% com 100, 0,058% com mil e 0,0013% com 30 mil. O esquema de ponderação atua com força máxima onde a amostra é frágil e se dissolve onde ela é robusta, que é o inverso do desejável. Quantidade de conjunto e valor de item não se misturam na mesma expressão.

E o decaimento é $1/\Delta t$, hiperbólico. Avaliação de ontem pesa 365 vezes mais que avaliação de um ano atrás. Como o $\Delta t$ é float de dias, avaliação de seis horas atrás pesa quatro vezes mais que a de ontem, e o peso tende ao infinito quando o tempo tende a zero. Na prática o índice não media estoque, media as últimas 48 horas com uma cauda decorativa, o que contraria a primeira propriedade da lista que eu mesmo escrevi.

Nenhum desses três é erro de programação. Todos os três são visíveis na notação e invisíveis no código, e é por isso que hoje eu escrevo a fórmula antes de escrever a função.

## A lição de engenharia que veio de brinde

Tem um quarto achado, e esse é de engenharia pura.

O cálculo precisa de uma data de referência. Quando a chamada não passa data, o serviço usa hoje e funciona. Quando passa, ele faz o parsing assim:

```go
dateValidate, _ = time.Parse("2006-01-02 00:00:00", rri.DateTo)
```

Em Go o layout é a data de referência escrita por extenso, e hora, minuto e segundo se escrevem `15`, `04` e `05`. Aquele `00:00:00` não é máscara de horário, é literal: o layout só casa com meia-noite exata. Qualquer outro horário falha. E o erro vai pro `_`.

Quando o parsing falha, `time.Parse` devolve o instante zero, primeiro de janeiro do ano 1. A subtração satura no teto de `time.Duration`, em torno de 106.752 dias, e todo $\Delta t$ do cálculo vira mais ou menos o mesmo número gigante. Pesos praticamente iguais entre si, e média ponderada com pesos iguais é média simples. O decaimento, que era a alma da métrica, desligava sem reclamar.

Meus scripts de exportação passavam a data como `dateTo=2020-09-30 23:59:59`, e o exemplo do README do serviço também. Reproduzi as três funções originais num programa isolado pra medir em vez de deduzir. Numa amostra de cinco avaliações, três notas 5 antigas e duas notas 1 recentes, o índice sai 3,08 com data válida e 7,17 com o formato que eu realmente usava, contra 6,80 de média simples dobrada.

O número quebrado é plausível. Está na faixa, tem uma casa decimal, sobe e desce mês a mês. Se devolvesse -12 ou 400 alguém teria olhado no primeiro dia. Métrica não tem teste de sanidade natural, e essa é a lição que eu carrego pra qualquer pipeline de indicador: cálculo que depende de parsing tem que explodir quando o parsing falha, porque métrica errada não vira alerta, vira gráfico.

## Quando a matemática de artesão virou econometria

O passo seguinte da jornada foi o mais valioso, e foi uma decisão de humildade: a Harmo encomendou um estudo formal pra reescrever o índice, com gente de econometria de verdade. O documento é proprietário e eu não vou reproduzir as equações, mas as correções de rumo são o que importa aqui, e elas mapeiam nos meus três pontos.

O peso passou a depender só do tempo. O escore aparece uma única vez, no numerador, onde ele é objeto da medição e não juiz dela.

O decaimento deixou de ser hiperbólico e virou logarítmico, na forma de um sobre o log do tempo. A diferença é grande na prática: no meu esquema, avaliação de um ano atrás carrega 0,0027 de peso relativo, praticamente nada; no esquema deles, 0,169, sessenta e duas vezes mais. Avaliação velha continua contando, cada vez menos, sem nunca zerar, que é exatamente o que a palavra estoque significa.

E o problema do volume foi atacado onde ele mora, na amostra e não no peso. Em vez de enfiar o $N$ dentro do logaritmo, o estudo define um número mínimo de avaliações pra loja entrar no índice, e escolhe esse número com critério explícito: padroniza desvio-padrão e perda de amostra na mesma escala, traça uma reta de indiferença cuja inclinação é um parâmetro de preferência declarado antes, e toma o ponto mais distante dela. Com preferência neutra, o corte cai em 29 avaliações acumuladas, custa 26,3% da amostra e leva o desvio-padrão mediano de 0,141 pra 0,055.

Essa última parte é a que eu mais admiro no trabalho deles, e é o tipo de coisa que dificilmente sai de dentro da engenharia. Eu tinha resolvido a questão do volume com um logaritmo. Eles resolveram com um critério de decisão declarado, que pode ser discutido, auditado e reajustado quando a preferência da empresa mudar. A diferença entre as duas abordagens não é sofisticação, é rastreabilidade da escolha.

O estudo ainda acrescentou um andar que eu não tinha imaginado: um índice de difusão, que compara cada loja com a média do próprio setor e responde qual porcentagem das lojas está acima dela, numa escala de 0 a 100 com 50 como neutro. Isso resolve de fato a heterogeneidade setorial que estava na minha lista de problemas, e permite comparar restaurante com hotel sem comparar nota com nota.

## O produto morreu de interpretabilidade

E aí a métrica ficou correta e morreu de qualquer jeito, pelo item que estava na lista desde o começo.

Pense no operador do shopping recebendo a leitura. O RRi da loja dele é 4,42 e a difusão do setor está em 57. O que ele faz na segunda-feira com isso? A escala é nova, não tem faixa de alarme, não tem ação atrelada, e na série real a difusão vive num corredor entre 54 e 59 com ruído diário grande, então a variação que ele vê é indistinguível de barulho.

Compare com a frase que a gente usa hoje: a cada 0,1 estrela adicional, aparece em média uma diferença de 8,8% nos pedidos de rota. É a mesma família de estatística descritiva que eu já mapeei [no post sobre as oito famílias de matemática](/blog/2026-07-27-formulas-essenciais-data-science-harmo/), amarrada num número que o lojista já entende, a estrela, e num resultado que ele quer, gente entrando na porta. Nota é comparável com o concorrente da esquina, é auditável no Google, e todo mundo já sabe se 4,3 é bom ou ruim.

Métrica proprietária cobra um pedágio de aprendizado do cliente, e ela só se paga se, depois de aprender, ele souber o que fazer. O RRi cobrava o pedágio e não entregava a ação. Foi por isso que ele saiu, e não por erro de conta.

<!-- PENDENTE, Rifeli: confirmar antes de publicar. (1) RRi é sigla de quê? O deck do estudo só chama de Índice de Reputação e nunca abre o acrônimo, e eu não invento. (2) Ano em que a primeira versão foi escrita: o código entrou no review-ms na consolidação do monorepo em fev/2021, mas os exemplos do README usam datas de 2018 e domínio antigo, então a origem é anterior e eu não tenho prova da data. Hoje o texto diz só "antes da gente escrever". (3) Data e motivo oficial do desligamento: o endpoint ainda está roteado e existe gráfico legado consumindo a coluna consolidada, então "morreu" é a minha leitura. A tese da interpretabilidade também é minha, não conclusão escrita no estudo. Se a decisão real foi outra, me diz e eu reescrevo a seção. -->

## O que ficou depois que o produto saiu

Quatro coisas que sobreviveram ao RRi, e nenhuma delas é o número.

- O vocabulário. Reputação como estoque, e não como média, é uma ideia que continua orientando produto aqui. A frase sobrevive à fórmula que a originou.
- O critério antes do símbolo. Escrever as propriedades desejáveis e os problemas esperados, dez linhas, antes de qualquer notação. É o artefato mais reaproveitável da jornada inteira e serve pra qualquer métrica nova.
- A régua da notação. Os três problemas da minha fórmula eram todos visíveis na álgebra e nenhum era visível no código. Notação é onde erro de raciocínio aparece; código é onde ele fica escondido, rodando e exportando série histórica.
- A descoberta de que interpretabilidade era a restrição dominante, e não precisão. Isso custou uma métrica pra aprender e hoje é o filtro que aplico em toda proposta de indicador novo: se não vem com uma ação atrelada, é decoração.

Se o critério de sucesso fosse o produto continuar de pé, o RRi foi um fracasso. Mas a empresa saiu da jornada sabendo formular uma métrica própria, sabendo quando escalar isso pra econometria formal, e sabendo que sofisticação estatística não compra interpretabilidade. Isso não estava disponível pra compra, e não teria vindo de outro jeito que não tentando. Necessidade de produto que ninguém no mercado resolve é convite pra escrever a matemática você mesmo, e a conta fecha mesmo quando o resultado é desligado depois.
