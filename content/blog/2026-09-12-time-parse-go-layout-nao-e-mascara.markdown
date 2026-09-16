---
title: "O layout do Go não é máscara: o time.Parse que desligou uma métrica sem reclamar"
seotitle: "time.Parse em Go: quando o layout não é máscara e a métrica quebra em silêncio"
draft: true
date: 2026-09-12T00:00:00.000Z
description: "Uma linha de time.Parse com o layout errado transformou uma média ponderada em média simples e continuou exportando número plausível. O layout do Go é data de referência, não máscara, e um 00:00:00 no lugar de 15:04:05 só casa com meia-noite exata. Este post mostra o mecanismo completo, do erro jogado no underscore até a saturação no teto de time.Duration, e o que eu passei a exigir de qualquer cálculo que dependa de parsing."
comments: true
keywords: [
  "time.Parse",
  "layout de data em Go",
  "golang",
  "2006-01-02 15:04:05",
  "tratamento de erro em Go",
  "time.Duration",
  "zero value",
  "bug silencioso",
  "qualidade de dados",
  "pipeline de métricas",
  "observabilidade"
]
tags:
  - golang
  - go
  - engenharia
  - dev-tools
---

## Introdução

O bug não derrubou nada. Não gerou alerta, não estourou log, não apareceu em dashboard vermelho. Ele fez uma coisa bem pior: continuou devolvendo número plausível, mês após mês, enquanto a parte mais importante do cálculo estava desligada.

A causa era uma linha só, e ela está sintaticamente correta. Compila, roda, passa no `go vet`.

```go
dateValidate, _ = time.Parse("2006-01-02 00:00:00", rri.DateTo)
```

Quem escreveu essa linha, e fui eu, achou que estava dizendo "ano com quatro dígitos, mês, dia, e depois hora, minuto e segundo". Não era isso que estava escrito.

## O layout é data de referência, não máscara

Quase toda linguagem trata formato de data como máscara. Você escreve `YYYY-MM-DD HH:mm:ss` e cada letra é um marcador de posição. Go não faz assim. Em Go o layout é uma data concreta, sempre a mesma, escrita do jeito que você quer ler as suas datas.

A data de referência é segunda-feira, 2 de janeiro de 2006, às 15h04m05s, fuso menos sete. Ela existe pra ser mnemônica: 1, 2, 3, 4, 5, 6, 7 na ordem mês, dia, hora, minuto, segundo, ano, fuso. Então hora se escreve `15`, minuto se escreve `04` e segundo se escreve `05`, porque esses são os valores que aquele instante tem.

Consequência direta: `00:00:00` não é marcador de nada. Não existe componente de tempo cujo valor de referência seja zero. O parser lê aquilo como texto literal e passa a exigir que a entrada tenha, naquela posição, os caracteres `00:00:00`. O layout casa com meia-noite exata e com mais nada.

```go
// o que eu escrevi: casa so com meia-noite
time.Parse("2006-01-02 00:00:00", "2020-09-30 00:00:00") // ok
time.Parse("2006-01-02 00:00:00", "2020-09-30 23:59:59") // erro

// o que eu queria ter escrito
time.Parse("2006-01-02 15:04:05", "2020-09-30 23:59:59") // ok
```

O detalhe cruel é que a versão errada funciona em teste. Se você exercita com meia-noite, e meia-noite é o valor mais natural pra quem digita uma data à mão, o layout passa. Ele só falha com o horário que o sistema de verdade manda.

## O erro foi pro underscore

E o sistema de verdade mandava `2020-09-30 23:59:59`, que é o fim do dia, o recorte que qualquer script de exportação usa quando quer fechar um período.

Aí entra a segunda metade do problema, que é a que realmente autoriza o desastre. O erro do `time.Parse` foi descartado no `_`. Sem erro tratado, o programa segue com o primeiro valor de retorno, e o primeiro valor de retorno de um `time.Parse` que falhou é o zero value de `time.Time`: primeiro de janeiro do ano 1, UTC.

Não é nulo, não é panic, não é sentinela óbvia. É uma data perfeitamente válida, dois mil anos no passado, pronta pra entrar em qualquer conta aritmética sem levantar suspeita.

## A saturação que igualou tudo

O cálculo seguinte era a idade de cada registro, a diferença entre a data de referência e a data do registro. Com a referência no ano 1, essa diferença fica negativa e gigantesca, e aí o Go faz o que está documentado em `Time.Sub`: quando o resultado não cabe numa `time.Duration`, ele devolve o valor máximo ou mínimo representável, em vez de estourar.

`time.Duration` é um `int64` de nanossegundos, então o teto fica em torno de 106.752 dias, uns 292 anos. Todas as idades saturaram no mesmo lugar. Todo $\Delta t$ do cálculo virou aproximadamente o mesmo número gigante.

O peso de cada item era inversamente proporcional a essa idade. Se todas as idades são iguais, todos os pesos são iguais. E média ponderada com pesos iguais é média simples. O decaimento temporal, que era a razão de existir daquela métrica inteira, desligou sem emitir um ruído.

## Medindo em vez de deduzir

Essa parte eu não quis deduzir no papel. Reproduzi as funções originais num programa isolado e rodei.

Numa amostra de cinco avaliações, três notas 5 antigas e duas notas 1 recentes, o índice sai 3,08 com data válida e 7,17 com o formato que eu realmente usava. A média simples dobrada, que é o que o cálculo vira quando o decaimento morre, dá 6,80.

Repare na distância. Com o decaimento funcionando, as duas notas 1 recentes dominam e o índice desce pra 3,08, que é exatamente o comportamento desejado: reputação recente pesa mais. Com o decaimento desligado, o índice sobe pra perto de 7, porque as três notas 5 antigas voltam a valer tanto quanto as novas. A métrica não estava imprecisa. Ela estava respondendo outra pergunta.

## Por que ninguém viu

Porque 7,17 é um número plausível.

Está dentro da faixa esperada, tem uma casa decimal, sobe e desce mês a mês conforme a base muda. Se aquela função tivesse devolvido -12, ou 400, ou `NaN`, alguém teria olhado no primeiro dia. Número absurdo tem um mecanismo de defesa embutido, que é o susto de quem lê.

Métrica não tem teste de sanidade natural. Ela é um número novo, numa escala nova, que ninguém tem intuição calibrada pra conferir. É justamente onde o erro silencioso vive mais confortável, e é por isso que gráfico bonito não é evidência de conta certa.

## O que eu passo a exigir

Três regras, e nenhuma delas é sofisticada.

A primeira é que erro de parsing não vai pro `_`. Nunca. Se a entrada é externa, o retorno de erro é a parte útil da chamada, e descartar ele é escolher não saber.

A segunda é que cálculo que depende de parsing tem que explodir quando o parsing falha. Falhar alto e cedo é barato. Seguir com zero value é caro, e o preço só aparece muito depois, quando alguém confere a série histórica.

A terceira é que todo layout de data ganha um teste com o valor que a produção realmente manda, não com o valor bonitinho que o desenvolvedor digita. No meu caso bastava um teste com `23:59:59` pra derrubar a linha inteira no dia em que ela foi escrita.

O bug era de uma linha. O estrago foi numa métrica inteira, e ele durou o tempo que durou porque o resultado errado parecia certo. Escrevi sobre a jornada completa dessa métrica, da notação ao índice reescrito por econometristas, [no post sobre como tiramos o RRi do zero](/blog/2026-09-09-rri-metrica-reputacao-do-zero-necessidade-de-produto/).
