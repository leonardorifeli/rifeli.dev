---
title: "Seis anos de Harmo: o que aprendi como CTO construindo infraestrutura Drive-to-Store"
draft: false
date: 2026-06-08T00:00:00.000Z
description: "A Harmo fez seis anos. Escrevo como co-founder e CTO sobre o que custou caro construir: tratar pilares Drive-to-Store como um sistema único em vez de quatro produtos costurados, processar +300 mil avaliações e +10 milhões de pesquisas por mês em mais de +60 mil lojas, e por que time e arquitetura são a mesma coisa. Decisões técnicas, lições de gestão e o diferencial que só aparece quando você constrói infraestrutura/plataforma, não feature."
comments: true
keywords: [
  "Harmo",
  "drive-to-store",
  "infraestrutura",
  "arquitetura de software",
  "CTO",
  "gestão de engenharia",
  "FloraAI",
  "reputação",
  "avaliações",
  "Google Business Profile",
  "GBP",
  "varejo",
  "dados em produção",
  "escala",
  "ciclo contínuo"
]
tags:
  - harmo
  - arquitetura
  - gestão
  - carreira
  - drive-to-store
---

<img id="image-custom" src="/images/posts/f4160481-ac27-4807-a036-e04c1b394436.png" alt="" />
<p id="image-legend">6 anos como CTO de uma infraestrutura Drive-to-Store</p>

# Introdução

A Harmo fez seis anos no mês de junho. Esse tipo de data costuma virar texto de marketing, mas eu queria escrever de outro lugar: o de quem assina o código e responde pelo time que o mantém. Então esquece o tom de release. Quero falar do que de fato custou caro construir, das decisões de arquitetura que sustentaram os outros cinco anos, e das lições de gestão que eu só aprendi errando.

A pergunta que a gente fazia no começo era simples e a resposta era difícil: por que a voz do cliente, que é o dado mais valioso que uma rede de varejo tem, vivia espalhada em ferramentas que não conversavam entre si? Avaliação num lugar, presença digital em outro, pesquisa em outro. Cada pedaço resolvido por uma solução isolada, nenhuma resolvendo o problema inteiro. A Harmo nasceu dessa inconformidade. Seis anos depois, ela não é uma ferramenta de GBP, não é uma plataforma de reputação e não é uma agência. É infraestrutura Drive-to-Store: um único sistema, integrado e governado, que transforma a voz do cliente em mais fluxo para a loja.

# O problema técnico nunca foi o óbvio

De fora parece que o desafio é integrar APIs e mostrar avaliação num dash bonito. Não é. O desafio real é manter um ciclo contínuo rodando em escala, com dados que chegam o tempo todo, de fontes que mudam as regras sem avisar, sobre uma base que hoje passa de 60 mil lojas. Processar mais de 300 mil avaliações e mais de 10 milhões de pesquisas por mês não é número de dashboard, é problema de arquitetura de verdade, com tudo que isso implica: idempotência, deduplicação, reprocessamento, e a disciplina chata de tratar fonte externa como algo que vai falhar, mudar de contrato e te surpreender no pior dia.

A decisão que sustentou todo o resto foi tratar pilares Drive-to-Store como um sistema único, não como quatro produtos costurados depois. Isso significou pagar adiantado em complexidade de modelagem de dados para que cada avaliação, cada pesquisa e cada ponto de presença digital alimentassem o mesmo ciclo, com o mesmo identificador de loja, o mesmo conceito de evento, a mesma fonte de verdade. Foi mais difícil no começo e é exatamente o que hoje nos deixa entregar coisas que um amontoado de ferramentas isoladas nunca vai entregar. Inteligência de verdade não se pluga em dados desconectados.

Boa parte do que sustenta isso na prática é matemática: estatística, correlação e os modelos que ligam a nota da loja ao fluxo na porta. Já mostrei o lado de dados e Python disso em [como começamos com Python para IA e dados na Harmo](/blog/python-ia-dados-harmo-basico-ao-pratico/), e em breve vou dedicar um post inteiro às oito famílias de fórmulas que rodam por trás da plataforma. Do lado da entrega, já escrevi sobre [como fazemos CI/CD na Harmo](/blog/como-fazemos-ci-cd-na-harmo/). Este post aqui é mais sobre as escolhas que vieram antes do código.

# Time é arquitetura

A lição de gestão que eu mais carrego é que time e arquitetura são a mesma coisa. O sistema que você consegue construir é o sistema que o seu time consegue sustentar. A Lei de Conway não é uma curiosidade acadêmica, é uma profecia que se cumpre todo trimestre. Por seis anos a prioridade não foi contratar rápido, foi contratar gente que entendesse que estávamos construindo infraestrutura, não feature. São coisas diferentes. Feature você entrega e comemora. Infraestrutura você entrega e passa a sustentar para sempre, e a régua de qualidade é outra porque o custo de errar se acumula em vez de passar.

A parte mais difícil como CTO foi aprender a dizer não para o caminho fácil. Toda vez que aparecia o atalho de resolver um caso pontual com uma gambiarra que não cabia no ciclo, a resposta certa quase sempre era a mais cara no curto prazo. Manter a coerência do sistema acima da velocidade de uma entrega isolada é uma disciplina que custa caro e some das métricas de curto prazo, e é exatamente ela que separa uma plataforma de uma colcha de retalhos. Eu errei isso algumas vezes nos primeiros anos. Cada vez que cedi ao atalho, paguei depois, com juros, em reescrita.

A outra lição é sobre dívida técnica como decisão de negócio, não como pecado. Nem toda dívida é ruim. A dívida que você contrai consciente, anota e cobra de volta no prazo é alavanca. A que você contrai sem perceber, espalhada em mil decisões pequenas que ninguém documentou, é a que te quebra. O trabalho do líder técnico é separar uma da outra e ter a coragem de defender a primeira na frente do board.

# O diferencial não é uma funcionalidade, é o sistema

Quando comparam a Harmo com o mercado, eu gosto de mostrar um número que diz muito: nas oito funcionalidades centrais de GBP, a Harmo cobre as oito. É o tipo de cobertura que só faz sentido quando você construiu infraestrutura, não quando empilhou recursos um sobre o outro. Cada funcionalidade isolada é fácil de copiar. O que é difícil de copiar é a integração que faz as oito conversarem entre si sobre a mesma base de dados.

E o salto dos últimos anos foi a FloraAI, nossa camada de inteligência transversal, já lançada e disponível em todos os planos. Ela não é um módulo à parte que vendemos como add-on, é inteligência rodando por cima de todo o ciclo. Isso só foi possível porque os dados já estavam integrados desde o primeiro dia. A FloraAI é, no fundo, a colheita de uma decisão de arquitetura que tomamos anos antes de existir hype de IA. A gente não construiu a fundação porque sabia que a IA viria assim. A gente construiu a fundação porque dado integrado sempre vale mais que dado disperso, e isso é verdade independente de moda.

# Reputação é performance, e isso é mensurável

O que mantém tudo isso de pé não é estética, é resultado. Reputação não é imagem, é performance. A correlação que orienta nosso trabalho mostra isso de forma quase brutal: cada 0,1 estrela a mais se traduz em 8,8% a mais em pedidos de rota. Na prática, ao longo de doze meses, isso aparece como um aumento de 36% nos pedidos de rota para a loja. Quando você consegue ligar uma variável que o time de operação enxerga como subjetiva, a nota, a um número que o CFO enxerga como concreto, gente entrando na loja, a conversa muda de departamento.

É por isso que insisto que a voz do cliente é dado estratégico, não SAC. Todo o trabalho técnico, do pipeline de ingestão à modelagem, do CI/CD à FloraAI, existe para uma coisa só: transformar esse dado em fluxo na porta da loja, de forma mensurável e auditável. Se eu não consigo provar o impacto com número, é estética, e estética não é o que a gente vende.

# O que vem agora

Seis anos depois, com mais de 200 clientes confiando na plataforma, eu olho menos para o que construímos e mais para o que essa fundação permite construir agora. Infraestrutura boa é assim: o valor dela não está no que ela já faz, está no que ela torna possível fazer a seguir. A FloraAI é o primeiro grande exemplo disso, e tenho convicção de que não vai ser o último.

Obrigado a todo mundo que escreveu uma linha desse sistema, abriu um chamado às três da manhã, ou brigou comigo numa revisão de arquitetura porque tinha um jeito melhor de fazer. Infraestrutura é coisa de time, e esse time é a melhor coisa que construímos em seis anos. Vamos para o sétimo.
