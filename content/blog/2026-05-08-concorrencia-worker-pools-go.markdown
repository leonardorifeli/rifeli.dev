---
title: "Concorrência e worker pools em Go: o mínimo que você precisa ter na ponta da língua"
draft: true
date: 2026-05-08T00:00:00.000Z
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

# Introdução

Go facilita concorrência a ponto de ser perigoso. `go func() { ... }()` é uma linha. Dispara mil goroutines em um loop é tentador. Depois a conta chega — exaustão de memória, rate limit de API estourado, race conditions sutis.

Esse post é o conjunto mínimo de patterns que eu uso e reviso em code review. Não é tutorial de goroutine nem de channel. É o que vira reflexo depois de alguns anos escrevendo Go em produção — worker pool bem feito, fan-out/fan-in com controle de erro, cancelamento via `context`.

# Goroutines: mais é menos

O instinto errado é "se goroutines são baratas, use muitas". Cada goroutine é barata sim (alguns KB iniciais), mas:

- **Recurso externo não é.** Se você abre 10.000 goroutines fazendo HTTP pra um serviço, a outra ponta te bloqueia.
- **Conexão com banco é cara.** Pool de conexões do PostgreSQL raramente é maior que 20-30. 10.000 goroutines esperam uma conexão — sem concorrência real, só enfileiramento disfarçado.
- **CPU é finita.** Trabalho CPU-bound não se beneficia de ter mais goroutines que cores disponíveis.

A pergunta certa não é "como disparar muitas goroutines" — é "quantas fazem sentido pra esse trabalho, e como limitar a esse número".

# Worker pool: o padrão básico

O worker pool resolve o problema de limitar concorrência. Estrutura:

```go
func processItems(items []Item) error {
    const workers = 10
    jobs := make(chan Item)
    var wg sync.WaitGroup

    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for item := range jobs {
                process(item)
            }
        }()
    }

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

Funciona, mas tem dois buracos: não propaga erro, e não cancela se algum worker falhar.

# errgroup: o que worker pool moderno deveria ser

`golang.org/x/sync/errgroup` resolve os dois buracos:

```go
import "golang.org/x/sync/errgroup"

func processItems(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10)

    for _, item := range items {
        item := item
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
- **`g.Wait()` retorna o primeiro erro.** Os demais são ignorados, o que costuma ser o que você quer — erro é erro, não precisa coletar todos.

A passagem `item := item` dentro do loop é o classic shadowing. Em Go 1.22+ não precisa mais (cada iteração cria nova variável), mas se você ainda roda em versões anteriores, essa linha é obrigatória.

# Fan-out / fan-in: quando tem transformação

Worker pool é bom pra processar items independentes. Fan-out/fan-in é pra pipeline — pegar entrada, transformar em paralelo, juntar resultados.

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

`context.Context` é o mecanismo padrão de cancelamento em Go. Qualquer função que faz trabalho não-trivial deve aceitar `ctx` e respeitar `ctx.Done()`.

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

Em I/O (HTTP, SQL, Redis), não precisa do check manual — as libs modernas respeitam `ctx` automaticamente. O check só aparece em loops CPU-bound longos.

# Armadilhas comuns

**Goroutine leak por send em channel não drenado.** Se você sai de uma função e deixa uma goroutine bloqueada tentando enviar num channel sem leitor, ela vaza pra sempre. `defer close()` + `select` com `ctx.Done()` evita.

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

**Channel sem buffer em fan-in.** Se o consumidor é mais lento que o produtor, produtores ficam bloqueados. Às vezes é o comportamento que você quer (backpressure). Às vezes não é — buffer pequeno (tamanho do número de workers) costuma ser um bom compromisso.

# Lições aprendidas

- **Limite sempre.** Worker pool ou `errgroup.SetLimit` — nunca dispare goroutines ilimitadas baseado em input externo.
- **`errgroup` é quase sempre o que você quer.** Se você está usando `sync.WaitGroup` cru, provavelmente está reescrevendo mal o que o `errgroup` faz bem.
- **Cancelamento é contrato.** Se sua função aceita `ctx`, precisa respeitar. Não aceitar `ctx` numa função que faz I/O é sinal de API mal desenhada.
- **Teste com `-race` sempre.** O race detector é um dos melhores recursos do Go. CI que não roda `go test -race` está perdendo bugs invisíveis.
- **Concorrência é técnica, não filosofia.** Vai longe mais rápido quem tem 4-5 patterns na ponta da língua e os usa consistentemente. Sofistica depois.

**💬 Qual pattern de concorrência em Go você mais usa no dia a dia?**

Tem alguma armadilha que só aprendeu depois de se queimar? Deixa aí — esse tipo de conhecimento não está em tutorial.
