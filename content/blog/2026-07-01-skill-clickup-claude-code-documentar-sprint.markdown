---
title: "Ensinei o Claude Code a documentar minha sprint no ClickUp (e ele abriu a última task sozinho)"
draft: true
date: 2026-07-01T00:00:00.000Z
description: "War story de produtividade: numa única conversa saíram 15 tasks pontuadas, 11 subtasks reestimadas e dois PRs, sem eu abrir o ClickUp na mão. Como transformei isso numa skill do Claude Code que fala com a API do ClickUp, as decisões de engenharia que apareceram no caminho (os dois campos de ponto, o cheiro do default, segredo por env var) e o limite que mantive: a skill propõe, eu aprovo."
comments: true
keywords: [
  "Claude Code",
  "skill custom",
  "ClickUp API",
  "automação de sprint",
  "story points ClickUp",
  "produtividade com IA",
  "Anthropic",
  "ferramentaria de dev",
  "como criar skill Claude Code",
  "documentar tasks com IA",
  "orquestrar ClickUp via API"
]
tags:
  - claude-code
  - ai
  - dev-tools
  - anthropic
  - produtividade
---

<img id="image-custom" src="/images/posts/f973e008-4073-4ae7-ba2c-2ab7ab37e399.png" alt="" />
<p id="image-legend">Da conversa pro board: a skill propõe as tasks pontuadas, eu aprovo, ela escreve.</p>

# Introdução

Numa única conversa com o Claude Code saíram 15 tasks pontuadas, 11 subtasks reestimadas e dois pull requests. Eu não abri o ClickUp em momento nenhum. No fim, a parte que mais me marcou foi banal: a própria ferramenta que eu tinha acabado de construir criou a última task do board, sozinha, fechando o loop.

Esse post é a história de como cheguei nisso, e principalmente das decisões de engenharia que apareceram no caminho. Não é um tutorial de "como criar uma skill" do zero. Esse eu já contei no post do [/save-session](/blog/2026-06-17-slash-command-save-session-claude-code/). Aqui o assunto é outro: o que acontece quando você dá a uma skill o poder de escrever num sistema externo de verdade, e o que você decide manter no controle humano.

# O problema que ninguém resolve

Trabalho de infraestrutura quase sempre acontece antes da burocracia. Você investiga um custo, mexe num cluster, prepara um upgrade de banco, e só depois lembra que aquilo precisa virar registro em algum lugar. O registro fica pra trás. A sprint não reflete o que foi feito. O esforço some.

Abrir task no meio do trabalho dá preguiça porque dá trabalho de verdade: título, escopo, pontos, épico, sprint certa, atribuição. Multiplica por quinze e ninguém faz. Foi exatamente o que aconteceu comigo numa sessão de trabalho de custo: eu tinha um monte de coisa feita e planejada, e zero disso no board.

A virada foi parar de tratar a documentação como uma segunda jornada e passar a tratar como subproduto. Eu conversei com o Claude Code enquanto fazia o trabalho de verdade, e no fim pedi pra ele documentar.

# A primeira versão foi feia, e tudo bem

Não comecei com uma skill. Comecei com a coisa mais burra que funcionava: pedi pro Claude descobrir como minha empresa já falava com o ClickUp. Ele varreu o código, achou uma integração existente que postava alertas, entendeu o padrão da API e passou a montar chamadas a partir dali. Em poucos minutos eu tinha tasks sendo criadas via `curl` improvisado.

Funcionou, mas era frágil. A cada novo pedido o modelo redescobria os mesmos IDs, os mesmos campos, a mesma convenção. É o tipo de coisa que pede pra virar ferramenta. Foi aí que empacotei numa skill: instruções fixas, um arquivo de referência com os IDs e o mapeamento dos campos, e um script Python que faz o trabalho sujo. A partir daí, a skill virou o caminho, e o modelo parou de reinventar a roda a cada turno.

# As decisões que importaram

A parte interessante não foi escrever o código. Foi o que apareceu enquanto eu olhava o resultado.

A primeira foi um detalhe chato da API do ClickUp que vale registrar pra quem for tentar: existem dois campos de ponto. Tem o custom field que o time configurou no board, e tem o Sprint Points nativo, que é o que alimenta a velocity. Eles são independentes. Preencher só um deixa o board mentindo pra você no relatório de sprint. A skill passou a sempre escrever nos dois, iguais. Parece bobo, mas é o tipo de armadilha que só dá as caras quando você confere o gráfico de velocity uma semana depois e os números não batem.

A segunda foi mais sutil, e é onde a IA quase me passou a perna sem querer. Eu tinha um conjunto de subtasks pra pontuar, e o campo de pontos já vinha preenchido: todas com 8. Olhei e o número não cheirava bem. Oito pontos em tudo, de "fallback quando não tem dado" a "conversa multi-turno de sugestão de resposta", é o padrão clássico de quem aplicou um valor em lote e seguiu a vida. Se eu mandasse o Claude "só copiar o que já estava lá", ele teria propagado um default sem sentido com a maior cara de competência. Em vez disso, pedi pra reestimar feature a feature. Saíram pontos variados, de 2 a 8, somando bem menos que o bloco de oito em tudo. A lição não é sobre ClickUp. É que ferramenta nenhuma substitui o seu julgamento sobre o tamanho das coisas. Ela acelera o registro, não a decisão.

A terceira foi sobre segredo, e essa eu não abri mão. O token de acesso jamais entra no arquivo da skill nem no repositório. Ele vive numa variável de ambiente, resolvida de um secrets manager no startup do shell. Quando o próprio modelo sugeriu, em algum momento, salvar o token num arquivo pra ficar mais fácil, eu recusei e expliquei o porquê. Credencial em texto puro versionada é dívida que volta pra te morder. Construir uma ferramenta nova não é desculpa pra repetir o erro que você passa a vida pedindo pros outros não cometerem.

# O limite que mantive

O ponto da skill não é automação cega. Ela não cria task em lote sem me mostrar antes. Quando peço "abre essas tasks na sprint", ela descobre qual é a sprint corrente pela data, monta cada uma com título, escopo, pontos e épico, e me apresenta a lista pra revisar. Eu aprovo ou ajusto, e só então ela sobe.

Esse passo de confirmação é deliberado. A diferença entre uma ferramenta que te ajuda e uma que te assombra é quem aperta o botão final. Trabalho que afeta outras pessoas, compromisso externo, decisão com impacto: a supervisão é humana. A IA prepara o rascunho qualificado e organiza. Quem assina sou eu.

# O loop que fecha sozinho

No fim da sessão, fazendo a investigação de algumas tasks, descobri uma ação residual que não estava no board. Pedi pra registrar. A skill, agora pronta, criou a task. Foi a primeira vez que ela rodou em produção a partir de uma decisão tomada na própria conversa, em vez de um comando meu explícito de "cria task tal". Pequeno, mas é o sinal de que a ferramenta deixou de ser um experimento e virou parte do fluxo.

# O que fica

Construir a skill levou menos tempo do que documentar uma sprint cheia na mão levaria, e ela paga esse custo toda vez que eu abro um board agora. Mas o aprendizado que carrego não é sobre velocidade.

É que dar poder de escrita a uma IA muda a natureza da revisão. Quando ela só lê e responde, um erro é um parágrafo errado. Quando ela escreve num sistema que o time usa, um erro vira ruído no board, número errado na velocity, decisão tomada em cima de dado falso. O ganho é real, mas ele só é seguro com dois cuidados que valem pra qualquer skill que toque o mundo externo: segredo nunca no código, e nada definitivo sem o humano olhar antes. O resto é conveniência.
