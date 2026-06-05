# O loop improdutivo que multiplicou nossa conta AWS por quase 6x em quatro madrugadas

Três variações para o LinkedIn. Link do blog no primeiro comentário. Primeira linha sempre narrativa, nunca bloco de código (lição do post de IRSA: bloco de código como hook custou o reach). Esse é o postmortem que o post de terça teaseou.

---

## Variação 1 — war story / o root cause

Toda invocação retornou HTTP 200. Nenhum erro, nenhuma exceção, nenhum stack trace. E mesmo assim a conta AWS do mês fechou quase 6x acima da baseline.

Em março, mergeei numa quarta às 19h um PR que mudou a lógica de paginação de uma lambda. Passou no review, nos testes, na esteira. Não violava o contrato de I/O, todos os campos do payload continuavam com tipo certo e schema válido. Sob uma combinação rara de filtros, ela passou a retornar o mesmo payload a cada invocação: cursor=0, totalFetched=0, pageCount=1, isFinished=false. Sem variar entre chamadas consecutivas.

Essa lambda alimenta uma Step Function de coleta paginada que tem um Choice state: enquanto isFinished=false, reinvoca. Do ponto de vista da máquina de estado, o payload era instrução pra continuar. Ela continuou. Cada execução rodava ~8h30 de loop até bater no teto hard de 25.000 eventos da Step Function e morrer com States.Runtime. Na madrugada seguinte, de novo. Quatro madrugadas, um final de semana no meio, 76 horas de sangria. A única defesa que pegou foi a revisão manual do billing na segunda de manhã.

Da detecção à contenção, 30 minutos. O caro não foi corrigir, foi as 76 horas até alguém olhar.

A lição que ficou doendo: sucesso técnico pode mascarar falha de negócio. Monitoramento baseado só em erro e exceção não pega fluxo que falha por ausência de progresso. Tem que monitorar comportamento, não só sucesso sintático.

Postmortem completo, os guard rails que entraram e a frente comercial com a AWS no rifeli.dev. Link no primeiro comentário.

#AWS #StepFunctions #Serverless #SRE #FinOps

---

## Variação 2 — escala / decisão de arquitetura e canal (C-level e champion)

A Harmo processa 10 milhões de pesquisas e 300 mil avaliações públicas por mês em cima de AWS. Nesse volume, um único fluxo serverless em loop improdutivo multiplicou a conta de um mês por quase 6x em quatro madrugadas, com zero impacto pra usuário final, zero perda de dado, zero degradação em serviço vizinho.

Três camadas falharam ao mesmo tempo, e o conserto atacou as três:

:: Código. Virou obrigatório teste de invariância em fluxo de paginação. Teste de shape confirma que o campo existe e tem o tipo certo. Teste de invariância confirma progresso entre invocações: se diz pra continuar, algo precisa ter mudado.
:: Arquitetura. O Choice state ganhou teto de iterações máximas e guard rail de progresso. O teto contém o pior caso, a invariância contém o caso comum.
:: Observabilidade. Três alarmes CloudWatch com latência de minutos, não de dias: duração de execução acima do p99 por fluxo, transições por execução acima de teto, e concorrência da lambda contra baseline rolling.

A frente comercial pesou tanto quanto a técnica. Trabalhei com a Infomach, nossa parceira AWS articulada via TD Synnex, em duas frentes em paralelo: validação do diagnóstico e dos guard rails, e abertura do pleito junto à AWS com o postmortem completo. A AWS reconheceu o caso e concedeu uma fração relevante do delta como crédito. O blameless postmortem com root cause clara e correções já concluídas foi o que sustentou a negociação.

Documento técnico bem feito é insumo de negociação, não burocracia. Canal AWS bem ativado é ativo estratégico.

Postmortem completo no rifeli.dev. Link no primeiro comentário.

#AWS #FinOps #CloudArchitecture #StepFunctions #Harmo

---

## Variação 3 — insight contra-intuitivo / a analogia

Existe movimento sem deslocamento, e nenhum sinal vital sabe diferenciar os dois.

Pensa num atleta numa esteira de academia versus correndo na rua. Frequência cardíaca, suor, gasto calórico: indistinguíveis. Só o GPS responde se a pessoa saiu do lugar. Foi exatamente isso que aconteceu com um fluxo serverless nosso que entrou em loop e multiplicou a conta AWS do mês por quase 6x.

A lambda retornava HTTP 200 a cada invocação, payload bem-formado, schema válido. Batimento cardíaco perfeito. O que faltava era o GPS: cursor=0, totalFetched=0, pageCount=1 a cada chamada, sinal inequívoco de que ninguém estava saindo do lugar. A Step Function lia só uma chave, isFinished=false, e reinvocava. Todo healthcheck verde, e o caixa sangrando por 76 horas.

A parte contra-intuitiva pra quem monitora sistema distribuído: sinal de batimento e sinal de deslocamento são coisas diferentes. Monitoramento que só observa erro e exceção enxerga o batimento. Pra fluxo com loop de negócio, a invariante crítica é progresso, e ela precisa ser explícita no código, no teste e no desenho do fluxo.

A segunda, que vale tanto quanto: latência de sinal importa tanto quanto existência de sinal. O sinal de custo existia, chegou com três dias de atraso. Em consumo exponencial, três dias é a diferença entre um susto e um evento material. Sinal técnico tem latência de minutos e é primeira linha. Sinal financeiro é backstop.

Se você opera Step Functions ou qualquer máquina de estado com loop: audite hoje quais fluxos podem rodar sem progresso, e veja se a defesa primária é técnica ou financeira.

Postmortem completo no rifeli.dev. Link no primeiro comentário.

#StepFunctions #AWS #SRE #Observability #Engineering

---

## Notas operacionais

- Recomendo Variação 1 como primária: o root cause é o gancho que o post de terça segurou de propósito, e a primeira linha (todo 200, e mesmo assim 6x) é o paradoxo que prende. Continuidade direta com o post do CronJob de custo.
- Variação 2 pra C-level / champion: proporções, nunca dólar do incidente, e carrega a frente comercial (Infomach, TD Synnex, crédito AWS). Pré-flight: confirmar com a Infomach antes de publicar, são citados nominalmente.
- Variação 3 carrega a analogia da esteira vs rua como hook e a lição central "sucesso técnico mascara falha de negócio". Leitor SRE / engenheiro sênior.
- Números expostos: só proporções (6x, teto de 25.000 eventos que é público da AWS, 76h de janela) e os volumes aprovados (10M pesquisas, 300k avaliações). Nenhum dólar absoluto.
- Link no primeiro comentário em até 60 segundos da publicação.
</content>
</invoke>
