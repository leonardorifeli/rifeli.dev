---
title: "Concorrência e worker pools em Go: o mínimo que você precisa ter na ponta da língua"
draft: false
date: 2026-05-27T00:00:00.000Z
description: "Goroutines, channels, fan-out/fan-in, worker pool com errgroup e cancelamento via context. Os patterns de concorrência que realmente aparecem em código de produção."
comments: true
keywords: [
  "Go",
  "Golang",
  "concorrência",
  "goroutine",
  "channel",
  "worker pool",
  "fan-out fan-in",
  "sync.WaitGroup",
  "errgroup",
  "context cancelamento",
  "como criar worker pool em go",
  "como usar errgroup golang",
  "como cancelar goroutine"
]
tags:
  - golang
  - concorrência
  - backend
  - patterns
---

<img id="image-custom" src="/images/posts/5ba7c7c0-1ce0-4913-b12e-b004122025ef.png" alt="" />
<p id="image-legend">Goroutines, channels, fan-out/fan-in, worker pool com errgroup e cancelamento via context</p>

# Introdução

Na Harmo, +50 dos nossos microservices em produção rodam em Go. Eles atendem +10 milhões de pesquisas, +1 milhão de eventos de performance de loja e +300 mil avaliações públicas por mês em mais de 60 mil lojas físicas, com picos que estouram facilmente um worker pool mal dimensionado. Quando você opera nesse volume, um único serviço com goroutine sem limite vira gargalo da plataforma inteira em minutos, não em horas.

Também usamos Go pesado em workloads orquestrados pelo nosso Airflow rodando em MWAA, com workers em Go disparados sob demanda pelas DAGs. É uma stack que merece post próprio e vai sair aqui em breve: a topologia inteira, as decisões de orquestração entre o scheduler em Python e os workers em Go, e os gotchas operacionais que aparecem quando se opera DAGs grandes apoiadas em Kubernetes. Por enquanto, fica registrado que o worker pool desse post é a base mental de muito do que roda lá.

`go func() { ... }()` é uma linha. Disparar mil goroutines em um loop é tentador. Depois a conta chega: exaustão de memória, rate limit de API estourado, race condition sutil que só aparece em produção sob carga real.

Esse post é o conjunto mínimo de patterns que eu uso e reviso em code review na Harmo. Não é tutorial de goroutine nem de channel. É o que vira reflexo depois de alguns anos escrevendo Go em produção: worker pool bem feito, fan-out/fan-in com controle de erro, cancelamento via `context`, e o que mudou com Go 1.25 que vale incorporar agora.

Começamos a usar Go na Harmo em 2017, ainda na versão 1.7. Famosa frase: quando chegamos, era tudo mato haha.

# Goroutines: mais é menos

O instinto errado é "se goroutines são baratas, use muitas". Cada goroutine é barata sim (alguns KB iniciais), mas:

- **Recurso externo não é.** Se você abre 10.000 goroutines fazendo HTTP pra um serviço, a outra ponta te bloqueia (ou vai cair \o/).
- **Conexão com banco é cara.** Pool de conexões do PostgreSQL raramente é maior que 20 ou 30. 10.000 goroutines esperam uma conexão. Sem concorrência real, só enfileiramento disfarçado.
- **CPU é finita.** Trabalho CPU-bound não se beneficia de ter mais goroutines que cores disponíveis.

A pergunta certa não é "como disparar muitas goroutines", é "quantas fazem sentido pra esse trabalho, e como limitar a esse número".

# Worker pool: o padrão básico

O worker pool resolve o problema de limitar concorrência. Estrutura:

```go
func processItems(items []Item) error {
    const workers = 10
    jobs := make(chan Item)
    var wg sync.WaitGroup

    // producers
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for item := range jobs {
                process(item)
            }
        }()
    }

    // workers
    for _, item := range items {
        jobs <- item
    }
    close(jobs)

    wg.Wait()
    return nil
}
```

Três partes:

- **Abre N workers** que consomem de um channel.
- **Produtor envia trabalho** e fecha o channel quando termina.
- **`WaitGroup` espera** todos os workers terminarem.

Funciona, mas tem dois problemas: não propaga erro, e não cancela se algum worker falhar.

# errgroup: o que worker pool moderno deveria ser

`golang.org/x/sync/errgroup` resolve os dois problemas:

```go
import "golang.org/x/sync/errgroup"

func processItems(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10)

    for _, item := range items {
        g.Go(func() error {
            return process(ctx, item)
        })
    }

    return g.Wait()
}
```

O que isso te dá:

- **`SetLimit(10)`** limita goroutines concorrentes. Chegou no limite, `g.Go(...)` bloqueia até uma terminar.
- **Primeiro erro cancela o contexto derivado.** Outras goroutines que respeitam `ctx` param sozinhas.
- **`g.Wait()` retorna o primeiro erro.** Os demais são ignorados, o que costuma ser o que você quer. Erro é erro, não precisa coletar todos.

Se você ainda roda em Go anterior à 1.22, precisa de `item := item` dentro do loop pra escapar o shadowing clássico do `for/range` com closure. A partir do 1.22, cada iteração cria variável nova automaticamente e a linha extra deixou de ser necessária.

# O que mudou em Go 1.25

Duas mudanças do Go 1.25 entram direto nessa conversa e valem incorporar.

A primeira é `sync.WaitGroup.Go(func())`. O `WaitGroup` ganhou um método novo que substitui o trio `wg.Add(1)` + `go func` + `defer wg.Done()` por uma única chamada:

```go
var wg sync.WaitGroup

for i := 0; i < workers; i++ {
    wg.Go(func() {
        for item := range jobs {
            process(item)
        }
    })
}

wg.Wait()
```

Mesmo comportamento do exemplo da seção de worker pool, três linhas a menos por chamada, e uma classe inteira de bug eliminada (esquecer o `Add` antes da goroutine, ou colocar dentro dela, que é o caso clássico de race entre `Add` e `Wait`). Se você usa `WaitGroup` cru sem propagação de erro, `wg.Go(...)` é o novo default. Pra fan-out com erro, `errgroup` continua sendo o caminho.

Por baixo dos panos, o `wg.Go(f)` é equivalente a três linhas que você já escreveu mil vezes na vida \o/:

```go
func (wg *WaitGroup) Go(f func()) {
    wg.Add(1)
    go func() {
        defer wg.Done()
        f()
    }()
}
```

Não tem mágica, é só o idiom canônico empacotado dentro do próprio `WaitGroup`. O detalhe que importa está na ordem: o `Add(1)` acontece síncronamente, na mesma goroutine que chamou `Go`, antes do `go func()` que faz o spawn. Isso é o que elimina o race condition clássico (eu pelo menos, já esqueci muito de implementar certo haha).

No antigo, quando alguém colocava `wg.Add(1)` dentro da goroutine (em vez de antes), abria janela pro produtor chamar `wg.Wait()` antes da goroutine começar a executar. `Wait()` retornava imediatamente porque o contador ainda estava em zero, e o trabalho rodava sem nenhuma barreira de sincronização esperando por ele. Bug invisível em laptop, problema sério sob carga, daqueles que só aparecem quando você precisa explicar pro time por que o teste de integração passa mas a feature falha em staging.

O `defer wg.Done()` dentro da goroutine garante o decremento mesmo se `f` panicar, mantendo o `WaitGroup` consistente, e o panic propaga normalmente pra cima. E como `wg.Go` aceita só `func()`, não há captura de erro nem de retorno: pra trabalho com falha possível, `errgroup` continua sendo o caminho. A escolha de design é coerente com o resto do pacote `sync`: oferece primitivo baixo-nível correto, deixa abstrações de alto-nível (erro, contexto) pro `errgroup` e amigos.

A segunda mudança é mais profunda e operacional: o runtime agora respeita limites de CPU de cgroups ao definir `GOMAXPROCS` automaticamente. Antes do 1.25, um pod com limite de 2 CPUs rodando numa máquina física de 64 cores fazia o Go assumir `GOMAXPROCS=64`. Resultado: scheduler do Go competindo desnecessariamente com o cgroup do Linux pelo CPU real do pod, latência inflada sem causa aparente, contenção de scheduler invisível pro APM.

No EKS, isso sempre foi armadilha clássica. A mitigação até 1.24 era importar `go.uber.org/automaxprocs` em todo serviço Go pra ajustar manualmente na inicialização. A partir do 1.25, vira comportamento default do runtime. Quem opera em container ganha latência de graça só atualizando a versão. Vale o esforço de migração só por esse item.

E uma terceira que vale citar mesmo não sendo de concorrência direta: o pacote `testing/synctest` saiu de experimental e virou estável. Permite testar código concorrente de forma determinística, sem flakiness de teste que falha 1 em 100 execuções. Substitui boa parte dos `time.Sleep` feios que a gente colocava em teste de goroutine pra dar tempo da coisa rodar. Pelo menos aqui, fizemos festa por conta disso haha.

# Fan-out / fan-in: quando tem transformação

Worker pool é bom pra processar items independentes. Fan-out/fan-in é pra pipeline: pegar entrada, transformar em paralelo, juntar resultados.

```go
func fanOutFanIn(ctx context.Context, ids []string) ([]Result, error) {
    in := make(chan string)
    out := make(chan Result)

    g, ctx := errgroup.WithContext(ctx)

    g.Go(func() error {
        defer close(in)
        for _, id := range ids {
            select {
            case in <- id:
            case <-ctx.Done():
                return ctx.Err()
            }
        }
        return nil
    })

    const workers = 10
    workerGroup := errgroup.Group{}
    for i := 0; i < workers; i++ {
        workerGroup.Go(func() error {
            for id := range in {
                result, err := fetch(ctx, id)
                if err != nil {
                    return err
                }
                select {
                case out <- result:
                case <-ctx.Done():
                    return ctx.Err()
                }
            }
            return nil
        })
    }

    go func() {
        workerGroup.Wait()
        close(out)
    }()

    var results []Result
    for r := range out {
        results = append(results, r)
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }
    if err := workerGroup.Wait(); err != nil {
        return nil, err
    }
    return results, nil
}
```

Mais verboso, mas o padrão é claro:

- **Um produtor** coloca IDs no channel `in`.
- **Workers consomem** de `in`, processam, colocam em `out`.
- **Goroutine separada** fecha `out` quando todos os workers terminam.
- **Leitor principal** drena `out`.

Detalhe crítico: todo envio em channel deve ter um `select` com `ctx.Done()`. Sem isso, se o contexto cancela mas um worker está bloqueado tentando enviar em `out`, a goroutine vaza.

# Cancelamento com context

`context.Context` é o mecanismo padrão de cancelamento em Go. Qualquer função que faz trabalho não-trivial deve aceitar `ctx` e respeitar `ctx.Done()` (mas não vai passar ctx default em cada chamada né).

Padrão correto em loop longo:

```go
func doWork(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
        }

        if err := step(ctx); err != nil {
            return err
        }
    }
}
```

O `default:` no `select` faz ele não bloquear quando o contexto não está cancelado. O check roda uma vez por iteração, custo desprezível, e garante que um cancelamento externo pare o loop.

Em I/O (HTTP, SQL, Redis), não precisa do check manual. As libs modernas respeitam `ctx` automaticamente, então o check só aparece em loops CPU-bound longos.

# Armadilhas comuns

**Goroutine leak por send em channel não drenado.** Se você sai de uma função e deixa uma goroutine bloqueada tentando enviar num channel sem leitor, ela vaza pra sempre. `defer close()` + `select` com `ctx.Done()` evita. Pra detectar leaks que já chegaram em produção, [`pprof`](/blog/tooling-nativo-go-produtividade-e-profiling-pprof/) (valida esse artigo massa na sequência) é a ferramenta padrão e cobri ela com detalhe num post separado sobre tooling nativo do Go.

**`sync.WaitGroup` com `Add` dentro de goroutine.** O `Add` tem que acontecer antes da goroutine começar. Dentro dela, existe race entre `Add` e `Wait`:

```go
wg.Add(1)
go func() {
    defer wg.Done()
    ...
}()
```

Nunca:

```go
go func() {
    wg.Add(1)
    defer wg.Done()
    ...
}()
```

**Shared state sem mutex.** Se duas goroutines escrevem no mesmo map, você tem race. `go run -race` detecta. Use `sync.Mutex`, `sync.RWMutex`, ou `sync.Map` quando fizer sentido.

**Channel sem buffer em fan-in.** Se o consumidor é mais lento que o produtor, produtores ficam bloqueados. Às vezes é o comportamento que você quer (backpressure). Às vezes não é, e nesses casos buffer pequeno (tamanho do número de workers) costuma ser um bom compromisso.

# Lições aprendidas

Cinco fechamentos que valem internalizar antes de fechar essa aba.

Limite sempre, sem exceção. Worker pool ou `errgroup.SetLimit`, mas nunca dispare goroutines ilimitadas baseado em input externo. É a primeira gambiarra que vira incidente em produção quando o input chega 10x mais do que você esperava, e a fila a montante decide que hoje é dia de empurrar tudo (vai por mim, isso vai salvar tua vida).

`errgroup` é quase sempre o que você quer. Se você está usando `sync.WaitGroup` cru pra coordenar trabalho com possibilidade de erro, provavelmente está reescrevendo mal o que o `errgroup` faz bem. A partir do Go 1.25, o `WaitGroup.Go(...)` cobre o caso simples sem erro de forma muito mais limpa, mas pra qualquer coisa com propagação, `errgroup` segue como default.

Cancelamento é contrato, não opção. Se a sua função aceita `ctx`, precisa respeitar `ctx.Done()`. Função que faz I/O sem aceitar `ctx` é sinal de algo mal desenhado, e geralmente quem está no topo da pilha precisa fazer um milagre pra forçar timeout do lado de fora.

Teste com `-race` sempre. O race detector é um dos melhores recursos do Go. CI que não roda `go test -race` está perdendo bug invisível que vai aparecer em produção sob carga. No 1.25 ele ganhou companhia útil: `testing/synctest` permite testes determinísticos de código concorrente. Se você ainda escreve teste de goroutine com `time.Sleep` esperando a coisa rodar, troca essa abordagem.

Concorrência é técnica, não filosofia. Vai longe mais rápido quem tem quatro ou cinco patterns na ponta da língua e os usa consistentemente em todo lugar. Channel pattern exótico e goroutine com sinal customizado ficam pra quem já passou da regra básica. A maioria do código de produção precisa só do básico bem feito.

Se você está revendo um serviço crítico em Go essa semana, escolhe um worker pool da sua base e roda esse checklist mental:
1. tem limite?
2. aceita context?
3. propaga erro com `errgroup`?
4. tem teste com `-race`?

Já está no 1.25 pra colher o **GOMAXPROCS** container-aware de graça? Cada "não" é dívida técnica esperando incidente.

Pra fechar com uma curiosidade que me interessa de verdade: qual armadilha de concorrência em Go você já bateu em produção que não entrou nessa lista? Esse tipo de história, costuma valer mais que tutorial bem escrito. Vou ler os comentários abaixo com caderno em mãos, e provavelmente atualizando essa página com o que aparecer.

Obrigado.