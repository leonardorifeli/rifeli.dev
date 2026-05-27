# Concorrência e worker pools em Go: o mínimo que você precisa ter na ponta da língua

Três variações para o LinkedIn. Mesmo título do post no blog. Link do blog no primeiro comentário.

---

## Variação 1 — escala / contexto Harmo

Mais de 50 microservices em Go rodando em produção na Harmo. Atendem 10 milhões de pesquisas e 300 mil avaliações por mês em mais de 60 mil lojas físicas.

Esse é o ambiente em que cada decisão de concorrência conta. Um único serviço com worker pool mal dimensionado vira gargalo da plataforma inteira em minutos, não em horas. Goroutine sem limite, channel sem buffer e disparo ilimitado baseado em input externo são as três armadilhas que aparecem em quase todo code review.

Hoje sai no rifeli.dev o post com o conjunto mínimo de patterns que viraram reflexo escrevendo Go em produção: worker pool com errgroup, fan-out/fan-in com controle de erro, cancelamento via context. Também cobre as três mudanças do Go 1.25 que valem incorporar agora.

Não é tutorial de goroutine. É o que vira reflexo depois de alguns anos de Go em produção em volume.

Link no primeiro comentário.

#Golang #Go #BackendEngineering #SRE

---

## Variação 2 — armadilha técnica / dev sênior

`go func() { ... }()` é uma linha. Disparar mil goroutines em um loop é tentador. Depois a conta chega: exaustão de memória, rate limit estourado, race condition sutil que só aparece em produção sob carga real.

A armadilha que eu mais vejo em code review: alguém usa `sync.WaitGroup` cru com `Add` dentro da goroutine. Vira race entre `Add` e `Wait`. Funciona no laptop, vaza em produção sob concorrência alta. Go 1.25 finalmente entregou `WaitGroup.Go(func())`, que abstrai `Add` + `go` + `Done` em uma chamada só e elimina essa classe inteira de bug.

Pra qualquer coisa com propagação de erro, `errgroup` continua sendo o caminho. Aceita context, cancela o derivado quando um erro acontece, e ainda tem `SetLimit` pra cap fácil. Se você está escrevendo `sync.WaitGroup` cru pra coordenar trabalho com erro, provavelmente está reescrevendo mal o que o `errgroup` faz bem.

Análise completa, com exemplos em Go e as três mudanças do 1.25, no rifeli.dev. Link no primeiro comentário.

#Golang #Go #Engineering #BackendDev

---

## Variação 3 — decisão operacional / líder técnico

Três coisas mudaram em Go 1.25 que valem migração só por elas.

Primeira: `sync.WaitGroup.Go(func())` abstrai `Add` + `go` + `Done` em uma chamada e elimina a classe clássica de race entre `Add` e `Wait`. Caso simples sem erro fica trivial.

Segunda: runtime respeita limites de CPU de cgroups e ajusta `GOMAXPROCS` automaticamente. No EKS, isso encerra a história do `automaxprocs` da Uber que todo serviço Go importava manualmente na inicialização. Latência de graça só atualizando a versão.

Terceira: `testing/synctest` saiu de experimental e virou estável. Permite testar código concorrente de forma determinística. Substitui boa parte dos `time.Sleep` que a gente colocava em teste de goroutine pra dar tempo de a coisa rodar.

Pra time que opera dezenas de microservices em Go (no nosso caso, mais de 50 atendendo 10M pesquisas e 300 mil avaliações por mês), são três upgrades que pagam o custo de migração sozinhos.

Detalhamento e o conjunto inteiro de patterns no rifeli.dev. Link no primeiro comentário.

#Golang #Go #DevOps #SRE #Kubernetes

---

## Notas operacionais

- Recomendo Variação 1 como primária pra hoje: número absoluto de stack Harmo no primeiro parágrafo, calibra audiência sênior e C-level em quem opera Go em volume.
- Variação 2 é a mais cirúrgica tecnicamente, fala direto com dev sênior.
- Variação 3 é tom de líder técnico / SRE, vende migração pra 1.25 com argumentos operacionais.
- Link no primeiro comentário em até 60 segundos após postar.
