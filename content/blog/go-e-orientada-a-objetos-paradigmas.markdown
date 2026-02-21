---
title: "Go é Orientada a Objetos? A resposta pragmática para uma dúvida comum"
draft: false
date: 2026-02-21T00:00:00.000Z
description: "Go é orientada a objetos? Descubra como a linguagem subverte os pilares clássicos ao trocar classes e herança por uma composição poderosa e interfaces implícitas. Entenda o pragmatismo por trás do design do Go e como ele se diferencia de linguagens como Java e C#."
comments: true
keywords: [
  "Go é orientada a objetos?",
  "Golang OOP vs Procedural",
  "Composição vs Herança em Go",
  "Interfaces em Golang",
  "Paradigmas da linguagem Go",
  "Structs e métodos em Go",
]
tags:
  - golang
  - programacao 
  - oop 
  - softwareengineering 
  - backend 
  - desenvolvimento 
  - tecnologia
---

<img id="image-custom" src="https://camo.githubusercontent.com/c53ca67708c63613f769ebd7fd9b5f030a308845b483d7f9189e60a625d0f857/68747470733a2f2f676f6c616e672e6f72672f646f632f676f706865722f6669766579656172732e6a7067" alt="cloud-native" />
<p id="image-legend">
  <a href="https://github.com/golang/go" target="_blank">golang/go</a>
</p>

# Introdução

Se você perguntar para três desenvolvedores se Go é uma linguagem Orientada a Objetos (OO), você provavelmente receberá quatro respostas diferentes. Uns dirão que é procedural "com esteroides", outros que é funcional por causa das funções de primeira classe, e alguns defenderão que é OO purista.

Sempre gosto de dizer que a melhor linguagem é que resolverá o seu problema da melhor forma.

A verdade? Go é o que você precisa que ela seja, mas ela odeia burocracia (isso que me fez amar desde cedo).

Mas a realidade é mais sofisticada. Segundo o FAQ oficial do Go: "Sim e não". Go é OO, mas não da forma que você aprendeu na faculdade. Vamos entender os pilares da OO sob a ótica de um Gopher.

# O que Go NÃO tem (e por que isso confunde)

Para quem vem do Java ou C#, a falta de certos pilares pode parecer estranha:

- **Não existem classes:** Temos structs;
- **Não existe herança:** Você não pode fazer uma struct `Dog extends Animal`;
- **Não existe polimorfismo de subtipo:** Esqueça as hierarquias complexas.

# O que Go TEM (A alma da OO)

Se definirmos OO como "objetos que encapsulam estado e expõem comportamento", Go é absolutamente OO:

- **Encapsulamento:** Usamos maiúsculas e minúsculas para exportar (ou não) campos e funções;
- **Métodos:** Você pode pendurar métodos em qualquer tipo, não só em structs;
- **Interfaces (O superpoder):** Em Go, as interfaces são satisfeitas implicitamente. Se algo "caminha como um pato", ele é um pato. Não precisa de implements.

#### O veredito: Composição sobre Herança

Tenho um artigo antigo onde explico a diferença entre [Herança e Composição](https://rifeli.dev/blog/2016-08-19-heranca-ou-composicao-qual-utilizar/).

# Sobre o Veredito: Go é Orientada a Objetos?

Se você define OO como hierarquias de classes e herança de tipos, então não.
Mas, se você define OO como um paradigma que permite:

- Encapsular estado;
- Definir comportamento (métodos) para tipos;
- Usar polimorfismo (interfaces).

Então Go é uma das linguagens OO mais pragmáticas e eficientes que existem. Ela remove a "cerimônia" e foca na composição, o que evita o famoso problema da "fronteira frágil" em sistemas grandes.

Go força você a usar composição. Em vez de dizer que um Gerente é um Funcionario, em Go dizemos que um Gerente contém um Funcionario. É uma mudança de mindset que gera códigos mais flexíveis e fáceis de testar.

# Exemplos

### 1. Encapsulamento: O poder das iniciais

Em linguagens tradicionais, usamos **public**, **private** e **protected**. Em Go, o encapsulamento é resolvido no nível do package através da capitalização.

- Inicia com Maiúscula: Exportado (Público);
- Inicia com Minúscula: Não exportado (Privado ao package).

```golang
package account

type CheckingAccount struct {
  Owner  string  // Público
  balance float64 // Privado: ninguém fora do package 'account' altera o saldo direto
}

// NewCheckingAccount é o nosso "Construtor"
func NewCheckingAccount(owner string) *CheckingAccount {
  return &CheckingAccount{Owner: owner, balance: 0}
}

// Deposit é um método (comportamento)
func (c *CheckingAccount) Deposit(amount float64) {
  if amount > 0 {
    c.balance += amount
  }
}
```

### 2. Métodos em qualquer lugar

Diferente do Java, onde métodos pertencem a classes, em Go você pode adicionar comportamento a qualquer tipo definido no seu package. Isso é OO puro: associar dado ao comportamento.

```golang
type Celsius float64

// Adicionando comportamento a um tipo primitivo (float64)
func (c Celsius) IsFreezing() bool {
  return c <= 0
}

func main() {
  temp := Celsius(25.5)
  fmt.Println(temp.IsFreezing()) // false
}
```

### 3. Adeus Herança, Olá Composição

Este é o ponto onde muitos desenvolvedores "travam". Go não permite que uma struct herde campos e métodos de outra. Em vez disso, usamos Struct Embedding (composição).

Em vez de dizer que um Gerente é um Funcionario, dizemos que um Gerente contém um Funcionario.

```golang
type User struct {
  Name  string
  Email string
}

func (u User) Label() string {
  return fmt.Sprintf("%s (%s)", u.Name, u.Email)
}

type Admin struct {
  User  // Embedding: Admin "ganha" os campos e métodos de User
  Level int
}

func main() {
  a := Admin{
      User:  User{Name: "Alice", Email: "alice@dev.com"},
      Level: 1,
  }
  
  // Podemos acessar Label() direto em 'a' como se fosse dele
  fmt.Println(a.Label()) 
}
```

### 4.Interfaces: O Polimorfismo Implícito

O maior trunfo do Go é a interface. Em C#, você precisa declarar `class Pato: IPato`. Em Go, se a sua struct tem os métodos que uma interface pede, ela automaticamente satisfaz a interface.

Isso é chamado de Structural Typing (ou Duck Typing estático).

```golang
type Speaker interface {
    Speak() string
}

type Dog struct{}
type Robot struct{}

func (d Dog) Speak() string { 
  return "Au Au!" 
}

func (r Robot) Speak() string {
  return "Beep Boop!" 
}

// Esta função não sabe (nem se importa) o que é um Dog ou Robot
func MakeItSpeak(s Speaker) {
  fmt.Println(s.Speak())
}
```

# O que vem a seguir?

Agora que entendemos que Go favorece a composição e o desacoplamento, como aplicamos regras rígidas de design para manter esse código limpo? No próximo artigo, vamos explorar o **Object Calisthenics** aplicado ao Go. 

Mas, você já pode dar uma lida sobre, neste artigo do mestre Elton Minetto sobre o assunto: [Como melhorar seus códigos usando Object Calisthenics
](https://eltonminetto.dev/2016/06/24/como-melhorar-seus-codigos-usando-object-calisthenics/)

# Conclusão

Go é uma linguagem multiparadigma que abraça a simplicidade. Ela pega o melhor da OO (interfaces e encapsulamento) e joga fora o pior (hierarquias de herança profundas).