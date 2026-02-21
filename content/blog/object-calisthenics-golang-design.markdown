---
title: "Object Calisthenics em Go: Disciplina de Design para Código Idiomático"
draft: true
date: 2026-02-25T00:00:00.000Z
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

IntroduçãoNo [meu último artigo], discutimos como Go lida com Orientação a Objetos através da composição. Mas como garantir que essa liberdade não resulte em um código bagunçado?Object Calisthenics é um conjunto de 9 regras de design criadas por Jeff Bay. Pense nelas como "exercícios de academia" para o seu código: no início dói, mas o resultado é uma base de código flexível, testável e elegante.As 9 Regras Adaptadas para Go1. Apenas um nível de indentação por funçãoEvite o "Código em Flecha" ($>$). Se você tem um if dentro de um for, sua função já está fazendo coisa demais.Em Go: Use Guard Clauses (retornos precoces) para manter o "caminho feliz" à esquerda.2. Não use a palavra-chave elseO else geralmente indica uma lógica que poderia ser simplificada com um retorno antecipado.Go// ✅ Idiomático em Go
if err != nil {
    return err
}
// lógica segue sem indentação extra
3. Encapsule todos os primitivos (Value Objects)Um email string é apenas um texto. Um type Email struct pode garantir que o dado é válido desde o nascimento.Dica: Isso evita o erro comum de passar age onde deveria ser id só porque ambos são int.4. Coleções como Cidadãos de Primeira ClasseSe você tem um slice de preços []float64, transforme-o em um tipo.Gotype Prices []float64

func (p Prices) Total() float64 { /* soma */ }
Isso move a lógica de negócio para onde o dado está, em vez de espalhar for pelo projeto.5. Um ponto por linha (Lei de Demeter)Não "navegue" através de objetos: user.Account.Profile.Picture.Isso cria acoplamento rígido. Peça o que você precisa diretamente: user.ProfilePicture().6. Não abrevie nomesGo tem uma cultura de nomes curtos para variáveis locais (r para reader, i para index). A regra aqui é: clareza acima de tudo. Se o nome precisa ser abreviado para ser lido, talvez o escopo da função esteja grande demais.7. Mantenha as entidades pequenasStructs com 50 campos são um pesadelo. Se uma struct cresce muito, ela está acumulando responsabilidades. Quebre-a em structs menores e use composição.8. Sem Getters ou SettersEm Go, não usamos GetAmount(). Usamos apenas Amount(). Mas o desafio aqui é maior: em vez de pedir o estado (get) para tomar uma decisão, mande o objeto fazer o que precisa.Don't ask, tell.9. No máximo dois campos de instância por structEssa é a regra mais difícil e polêmica. Ela força você a pensar em alta coesão. Se sua struct precisa de 10 campos, talvez ela deva ser composta por 5 structs menores.Conclusão: Disciplina vs DogmaAplicar as 9 regras ao mesmo tempo em um projeto de produção pode ser contraproducente. No entanto, praticá-las em projetos paralelos ou refatorações pontuais treina seu cérebro para identificar "cheiros de código" (code smells) instantaneamente.O design em Go não é sobre o que a linguagem te obriga a fazer, mas sobre a disciplina que você escolhe ter.