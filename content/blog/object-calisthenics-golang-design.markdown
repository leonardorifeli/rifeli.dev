---
title: "Object Calisthenics em Go: disciplina de design em uma linguagem pragmática"
draft: false
date: 2026-03-03T00:00:00.000Z
description: "Eleve a qualidade do seu código Go com as 9 regras do Object Calisthenics. Aprenda a aplicar exercícios de disciplina de design para criar structs coesas, funções limpas e um domínio rico, transformando teoria de Clean Code em prática idiomática no seu dia a dia."
comments: true
keywords: [
  "Object Calisthenics Golang",
  "Clean Code em Go",
  "Boas práticas Go",
  "Código idiomático Go",
  "Refatoração de código Go",
  "Regras de Jeff Bay Go",
  "Design Patterns em Go"
]
tags:
  - golang 
  - cleancode 
  - refactoring 
  - softwaredesign 
  - bestpractices 
  - objectcalisthenics 
  - programming
---

<img id="image-custom" src="https://dkrn4sk0rn31v.cloudfront.net/uploads/2022/10/o-que-e-e-como-comecar-com-golang.jpg" alt="cloud-native" />
<p id="image-legend">
  <a href="https://github.com/golang/go" target="_blank">golang/go</a>
</p>

# Introdução

No meu último artigo, discutimos como Go lida com orientação a objetos através de composição ([veja aqui](https://rifeli.dev/blog/go-e-orientada-a-objetos-paradigmas/)). Mas composição sozinha não garante bom design.

Go te dá liberdade: structs simples, métodos livres e interfaces implícitas, porém, é justamente por isso é fácil cair em:

- Funções gigantes
- Services que sabem demais
- DTOs anêmicos
- Lógica espalhada pelo projeto

A pergunta não é "Go suporta OO?". Ela precisa ser: Como manter disciplina arquitetural numa linguagem que não impõe nada?

É aqui que entra **Object Calisthenics**.

# O que é Object Calisthenics?

Tem uma palestra que marcou minha carreira, é do Guilherme Blanco e foi [PHP para Adultos – Object Calisthenics e Clean Code - Guilherme Blanco no InterCon PHP 2014
](https://www.youtube.com/watch?v=u-w4eULRrr0) em set/2014 (entreguei a idade).

Criado por **Jeff Bay**, é um conjunto de 9 regras de design pensadas como treino de musculação para código.

No começo dói.
Depois você começa a enxergar problemas antes deles virarem débito técnico.

Mas aqui vai o ponto importante:

> Object Calisthenics não deve ser aplicado como dogma.
> Ele deve ser usado como lente.

Vamos adaptar as 9 regras para a realidade do Go.

# 1. Apenas um nível de indentação por função

Se sua função parece uma pirâmide, ela já está fazendo coisa demais.

Código em flecha:
```golang
func Process(order Order) error {
	if order.IsValid() {
		if order.HasStock() {
			if err := order.Pay(); err != nil {
				return err
			}
		}
	}
	return nil
}
```

Versão idiomática em Go:

```golang
func Process(order Order) error {
	if !order.IsValid() {
		return ErrInvalidOrder
	}

	if !order.HasStock() {
		return ErrNoStock
	}

	return order.Pay()
}
```

Go já incentiva isso naturalmente via guard clauses (Está PROIBIDO usar ELSE).

Essa regra é praticamente um reforço do estilo idiomático da linguagem.

# 2. Não use else

O else geralmente indica que você poderia ter retornado antes.

Em Go isso é ainda mais evidente:

```golang
if err != nil {
	return err
}
```

Esse padrão não é só estilo, ele reduz:

- Profundidade cognitiva
- Complexidade ciclomática
- Carga mental ao revisar código

# 3. Encapsule todos os primitivos (Value Objects)

Aqui começa a ficar interessante em Go.

Problema comum:

```golang
func CreateUser(id int, age int, email string)
```

Nada impede você de trocar id e age.

Agora:

```golang
type UserID int
type Age int
type Email string
```

Ou melhor:

```golang
type Email struct {
	value string
}

func NewEmail(v string) (Email, error) {
	if !strings.Contains(v, "@") {
		return Email{}, ErrInvalidEmail
	}
	return Email{value: v}, nil
}
```

Agora o erro é impossível de existir fora da criação.

Esse padrão é poderoso especialmente em sistemas de domínio rico, algo comum em produtos SaaS complexos.

# 4. Coleções como cidadãos de primeira classe

Se você tem isso:

```golang
func CalculateTotal(prices []float64) float64
```

Você espalha lógica por todo lugar.

Prefira:

```golang
type Prices []float64

func (p Prices) Total() float64 {
	var total float64
	for _, price := range p {
		total += price
	}
	return total
}
```

Agora o comportamento mora com o dado.

Isso reduz:

- Vazamento de regras
- Duplicação de loops
- Inconsistência

# 5. Um ponto por linha (Lei de Demeter)

Evite isso:

```golang
order.Customer.Address.City.Name
```

Isso cria acoplamento estrutural profundo.

Prefira:

```golang
order.CityName()
```

Se amanhã, a estrutura de City mudar, só um lugar precisa ser alterado.

# 6. Não abrevie nomes

Go aceita variáveis curtas.
Mas isso não significa que tudo deve ser abreviado.

Existe diferença entre:

```golang
i, r, w
```

E:

```golang
usrSvcProcMgr
```

Se o nome precisa ser abreviado para caber, talvez a responsabilidade esteja grande demais.

# 7. Entidades pequenas

Structs grandes quase sempre indicam:

- Baixa coesão
- Muitas razões para mudar
- Violação de SRP ([tenho um artigo antigo sobre o assunto](https://rifeli.dev/blog/2017-03-25-principios-solid-srp-e-sopa-de-letrinhas/))

Se você tem:

```golang
type UserService struct {
	repo Repository
	cache Cache
	mailer Mailer
	logger Logger
	metrics Metrics
}
```

Talvez você tenha:

- Um Service Orquestrador
- Um Service de Notificação
- Um Service de Persistência

> Composição > concentração.

# 8. Sem Getters e Setters

Go já não força encapsulamento clássico.

Mas o problema real não é o método.
É o modelo anêmico.

Em vez de:

```golang
if order.Status() == Pending {
	order.SetStatus(Paid)
}
```

Prefira:

```golang
order.Pay()
```

Isso mantém regras de negócio dentro da entidade.

# 9. No máximo dois campos por struct

Essa é a mais polêmica. Ela força alta coesão.

Mas em Go isso precisa ser interpretado com cuidado.

DTOs de transporte? Podem ter muitos campos.
Entidades de domínio? Devem ter poucos e bem relacionados.
Essa regra não é literal, é um detector de alerta.

### Onde Object Calisthenics NÃO funciona bem em Go:

- Código de infraestrutura
- Adaptadores HTTP
- Serialização
- Mappers
- DTOs de banco

Aplicar rigor extremo ali gera abstração artificial.

Object Calisthenics brilha em:

- Domínio rico
- Lógica de negócio
- Regras complexas
- Sistemas que vivem muitos anos

### O Verdadeiro Valor

Object Calisthenics não é sobre OO.

É sobre:

- Coesão
- Encapsulamento
- Redução de acoplamento
- Fluxos simples
- Modelagem intencional

Go não impõe arquitetura.

Ele expõe seu design.

E isso é perigoso.

Porque você pode escrever código simples…
ou simplesmente simplista.

# Conclusão

Aplicar as 9 regras ao mesmo tempo em produção pode ser exagero.

Mas praticá-las:

- Em refatorações
- Em projetos paralelos
- Em código crítico

Treina seu cérebro para enxergar problemas antes deles virarem dívida técnica.

Design em Go não é sobre herança.
Não é sobre frameworks.
Não é sobre patterns da moda.

É sobre disciplina.
E disciplina não é imposta pela linguagem.
É escolhida pelo desenvolvedor.

Na [Harmo](https://harmo.me), usamos Object Calisthenics como disciplina de modelagem para manter nosso domínio coeso, explícito e sustentável ao longo do tempo.