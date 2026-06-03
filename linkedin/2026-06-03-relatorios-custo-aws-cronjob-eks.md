# Relatório diário de custo AWS com CronJob no EKS: encurtando a demora entre a anomalia e alguém perceber

Três variações para o LinkedIn. Link do blog no primeiro comentário. Primeira linha sempre narrativa, nunca bloco de código (lição do post de IRSA: bloco de código como hook custou o reach).

---

## Variação 1 — war story / a janela cega

Nossa conta AWS sangrou por 76 horas e ninguém percebeu. Não por falta de dado. Por falta de rotina.

Em março, um fluxo serverless da Harmo entrou em loop improdutivo e multiplicou a conta do mês por quase 6x. O consumo anômalo atravessou um final de semana inteiro porque a única defesa que pegou o problema foi a revisão manual do dashboard de billing. E revisão manual não acontece no sábado.

O postmortem completo do incidente sai na sexta. Hoje publiquei a primeira contramedida que nasceu dele: um CronJob no próprio EKS que roda toda manhã, inclusive sábado e domingo, puxa o Cost Explorer, compara cada serviço com a média dos últimos 7 dias e posta o resultado num Doc no ClickUp. Detectou anomalia, abre task com dono e prazo no board que o time já olha de manhã.

A regra de detecção é intencionalmente simples: serviço 50% acima da média dos 7 dias anteriores e diferença absoluta maior que USD 5. Os dois guard-rails juntos evitam alertar variação percentual em serviço que custa centavos. Foi escrita numa tarde e roda há dois meses sem falhar.

Lição que ficou: custo anômalo na AWS é assintomático. Não derruba serviço, não dispara exceção, não acorda ninguém. Quem só olha o billing quando sente alguma coisa descobre tarde.

Arquitetura completa, código Python, IRSA e o manifest do CronJob no rifeli.dev. Link no primeiro comentário.

#AWS #EKS #FinOps #Kubernetes #CloudNative

---

## Variação 2 — escala / decisão de arquitetura (C-level e champion)

A Harmo processa 10 milhões de pesquisas e 300 mil avaliações públicas por mês em cima de AWS. Com esse volume, variação de custo deixa de ser detalhe de fatura e vira sinal operacional. E sinal precisa de rotina, não de boa vontade.

Construí um robô de FinOps que virou peça central da nossa rotina diária:

:: CronJob no próprio EKS, toda manhã às 8h, inclusive fim de semana. Roda nos nós que já pagamos, sem Lambda nem EventBridge.
:: Script Python consulta o Cost Explorer e compara cada serviço com a média dos últimos 7 dias.
:: IRSA pra credenciais AWS e Secrets Manager pro token do ClickUp. Zero segredo em código ou env var.
:: Relatório vai pra um Doc no ClickUp com histórico. Anomalia vira task com dono no board que o time já usa.

O destino do alerta importa tanto quanto o alerta. Relatório que mora fora da ferramenta do dia a dia vira aba esquecida em duas semanas. Task no board tem cobrança natural.

Custo da automação: USD 2,40 por mês de Cost Explorer API. Setup: uma tarde. A demora de detecção de anomalia caiu de "quando alguém lembra de olhar" pra no máximo um dia.

Post completo com código e manifest no rifeli.dev. Link no primeiro comentário.

#FinOps #AWS #EKS #CloudArchitecture #Harmo

---

## Variação 3 — insight contra-intuitivo / detecção simples

Custo anômalo na AWS não dói. E é exatamente por isso que ele é perigoso.

Não derruba serviço, não dispara exceção, não acorda ninguém de madrugada. Todo healthcheck verde, todo endpoint respondendo, e o caixa sangrando em silêncio. Pressão arterial alta funciona igual: não dá sintoma, e por isso a medicina não espera sintoma. Mede em toda consulta, de rotina. Quem só mede quando sente alguma coisa descobre tarde.

Depois de um incidente que multiplicou nossa conta do mês por quase 6x (postmortem sai na sexta), construí a medição de rotina: CronJob no EKS que roda toda manhã, puxa o Cost Explorer e compara cada serviço com a média dos últimos 7 dias.

A parte contra-intuitiva: a regra de detecção tem duas linhas. Serviço 50% acima da média e delta maior que USD 5. Sem média móvel exponencial, sem sazonalidade, sem ML. E captura a maior parte do que importa na prática.

Detecção simples supera sofisticação ausente. O robô imperfeito rodando todo dia vence o sofisticado que ficou no backlog. Dá pra evoluir depois, mas evolução pressupõe que a versão um existe e roda.

Código, arquitetura e as decisões que pouparam dor no rifeli.dev. Link no primeiro comentário.

#AWS #FinOps #EKS #Engineering #SRE

---

## Notas operacionais

- Recomendo Variação 1 como primária: war story com número absoluto na primeira linha (76 horas), tease do postmortem de sexta cria continuidade entre os dois posts.
- Variação 2 pra audiência C-level / champion: proporções e custo da automação, sem dólar do incidente.
- Variação 3 carrega a analogia da pressão arterial como hook e a lição "detecção simples supera sofisticação ausente". Leitor SRE / engenheiro sênior.
- Nenhuma variação entrega o root cause do incidente — isso é o conteúdo do post de sexta. Só proporção (6x) e janela (76h), que já estão aprovadas no postmortem.
- Link no primeiro comentário em até 60 segundos da publicação.
