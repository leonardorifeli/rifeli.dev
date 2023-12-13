---
title: "Princípios SOLID: LSP e sopa de letrinhas"
draft: false
date: 2017-12-30T00:00:00.000Z
description: ""
categories:
  - Desenvolvimento
tags:
  - SOLID
---

Este é o terceiro post de uma série onde abordaremos todos os cinco princípios do SOLID. Neste, falaremos sobre “Liskov substitution principle”, abreviado por LSP, e significa literalmente “Princípio da substituição de Liskov”.

- O primeiro post foi sobre “Single responsibility principle”, abreviado por SRP, e você pode [ler aqui](http://leonardo.rifeli.tech/development/2017/03/20/principios-solid-srp-e-sopa-de-letrinhas.html).
- O segundo post foi sobre “Open closed principle”, abreviado por OCP, e você deve [ler aqui](http://leonardo.rifeli.tech/development/2017/12/05/principios-solid-ocp-e-sopa-de-letrinhas.html).

Para começar: falar de SOLID é falar de programação orientada a objetos e design (OOD). Tendo isso em mente, o princípio de substituição de Liskov traz outra perspectiva importante: classes filhas nunca deveriam inflingir as definições de tipo da classe pai.

# **Contexto histórico**

Este conceito foi apresentado por [Barbara Liskov](https://pt.wikipedia.org/wiki/Barbara_liskov) numa conferência em 1987, e depois foi publicado em um artigo científico, com o nome `[Family Values: A Behavioral Notion of Subtyping](http://reports-archive.adm.cs.cmu.edu/anon/1999/CMU-CS-99-156.ps)`, junto de [Jeannette Wing](https://en.wikipedia.org/wiki/Jeannette_Wing), em 1993. Com a seguinte definição original:

> Se q(x) é uma propriedade demonstrável dos objetos x de tipo T. Então q(y) deve ser verdadeiro para objetos y de tipo S onde S é um subtipo de T.

E após a publicação do livro [Agile Software Development, Principles, Patterns, and Practices](https://www.amazon.com/dp/0135974445/), está definição ficou conhecida como Princípio de Substituição de Liskov. O que nos leva para a definição de Uncle Bob:

> Subclasses devem ser substituíveis pelas classes base.

Simples, uma subclasse deve poder sobrescrever os métodos da classe base, de modo com que não quebre suas funcionalidades, do ponto de vista do cliente.

# **Problemas da violação do LSP**

- Geração de problemas na classe cliente (pariticipante que está consumindo outro participante);
- Comportamentos inesperados no software por suposições equivocadas;
- Quebra de outros princípios.

# **Exemplo**

Seguindo o mesmo padrão do primeiro e segundo post, os exemplos (com exceções de alguns participantes) serão exibidos somente com as assinaturas, para reforçar a ideia que Uncle Bob traz, de que a implementação dos métodos é irrelevante para a análise. Somente com as assinaturas, conseguimos perceber se existe (ou não) a violação do princípio.

Usaremos o clássico exemplo do `quadrado` e do `retângulo`.

### Exemplo do quadrado e retângulo

No participante abaixo, temos a classe **`Rectangle`** e ela compõe as propriedades `width` (largura) e `height` (altura).

```php
<?php

namespace Leonardo\Rifeli\Article; 

class Rectangle
{

    private $width;
    private $height;

    public function getWidth() { }
    public function getHeight() { }
    public function setWidth($width) { }
    public function setHeigth($heigth) { }

}
```

Abaixo temos a classe **`RectangleArea`**, responsável por efetuar o cálculo da área de um retângulo.

```php
<?php

namespace Leonardo\Rifeli\Article; 

use Leonardo\Rifeli\Article\Rectangle;

class RectangleArea
{

    // calc rectangle area: $rectangle->getWidth() * $rectangle->getHeight().
    public function calc(Rectangle $rectangle) { }

}
```

Até aqui tudo dentro do esperado. Temos dois participantes (**`Rectangle`** e **`RectangleArea`**) e eles funcionam como esperado, pelo menos por enquanto.

Vamos escrever agora um teste para nossos participantes (neste caso teremos implementação para as coisas não ficarem tão abstratas).

```php
<?php

namespace Leonardo\Rifeli\Article\Test; 

use Leonardo\Rifeli\Article\Rectangle;
use Leonardo\Rifeli\Article\RectangleArea;

class TestRectangleArea
{

    const WIDTH = 10;
    const HEIGHT = 5;

    public function testCalc(Rectangle $rectangle) 
    {
        $rectangle->setWidth(self::WIDTH);
        $rectangle->setHeight(self::HEIGHT);

        $rectangleArea = new RectangleArea();

        if($rectangleArea->calc($rectangle) !== (self::WIDTH * self::HEIGHT))
            throw new \Exception('Violated LSP.');
    }

}
```