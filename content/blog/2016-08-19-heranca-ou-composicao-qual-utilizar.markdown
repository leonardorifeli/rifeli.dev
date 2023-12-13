---
title: "Herança ou composição? Qual utilizar?"
draft: false
date: 2016-08-19T00:00:00.000Z
description: ""
categories:
  - Desenvolvimento
tags:
  - PHP
---

Olá dev sapiens, desta vez o artigo será mais teórico (comparado ao último: [Web Socket no PHP](https://leonardorifeli.com/development/2016/05/29/socket-no-php.html)) e será sobre dois assuntos que possuem demasiada importância no meio da programação orientada a objetos, a herança e a composição.

Sim, na internet existem vários artigos sobre o assunto, porém, resolvi descrevê-lo do modo como eu os utilizo.

Enquanto escrevo este magnífico artigo, vou ouvindo um set **Progressive House** do **[Progressive House](https://www.youtube.com/watch?v=N7DEv-QP_Zk)** .

Herança ou composição? E agora, José?

# Introdução

Um assunto muito abordado e importante na programação orientada a objetos é a utilização de herança ou composição, porém, é visível que muitos programadores(as) optam por utilizar a herança sem mesmo validar as alternativas dentro de cada contexto.

Pois bem, este artigo tem como objetivo colocar os dois assuntos na balança, com o intuito de que você entenda do que cada um é composto e qual utilizar dentro de cada contexto/relação.

# Função

A herança e a composição são duas abordagens diferentes para obter-se a reutilização de funcionalidades.

# Herança

Na herança, uma classe herda (daí o termo herança) as propriedades e os métodos de sua classe pai, de modo transitivo, ou seja, uma classe pode herdar de outra classe que herda de outra, até uma classe que não possuí uma classe pai.

Com a herança, as propriedades e os métodos podem se comportar de forma diferente na classe filha, por uso da reescrita dos respectivos métodos.

A herença deverá ser utilizada somente quando existir uma relação **“é-um”** no contexto. No exemplo abaixo, no arquivo **Car.java**, a classe **Car** herda a classe **Automobile** e nesse contexto temos uma relação **“é-um”**, ou seja, **Car** é um **Automobile**, em nenhum momento, **Car** deixará de se comportar como **Automobile**.

```java
package com.leonardorifeli.article.inheritance.model;

public class Car extends Automobile {

    public Car(final String color, final Integer quantityPort) {
        this.setColor(color);
        this.setQuantityPort(quantityPort);
    }

    public String getColor() {
        return "perfect "+ this.color;
    }

    public String myColor() {
        return "Color is: "+ this.getColor();
    }

    public String myQuantityPort() {
        return "Quantity port is: "+ this.getQuantityPort();
    }

}
```

Verifique que a classe **Car.java** no exemplo acima, está sobrescrevendo o método **getColor()**, alterando o comportamento herdado da classe pai **Automobile.java**.

```java
package com.leonardorifeli.article.inheritance.model;

public class Automobile {

    private String color;
    private Integer quantityPort;

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public Integer getQuantityPort() {
        return quantityPort;
    }

    public void setQuantityPort(Integer quantityPort) {
        this.quantityPort = quantityPort;
    }
}
```

Por fim, repare que, no contexto exemplificado acima, o ideal é utilizar a herança, pelo fato de ter-se uma relação **“é-um”**, podendo assim, atingir a reutilização dos comportamentos.

Com a evolução, poderíamos ter a classe **Truck.java** que também poderia herdar a classe **Automobile.java**, pelo fato de existir uma relação **“é-um”**, neste outro contexto.

# Composição

Na composição, codificamos pequenos comportamentos, onde uma classe irá apenas instanciar outra classe e utilizar uma propriedade ou um método (claro, os que estão expostos), com isso, podemos usar a composição para comportamentos mais complexos, podendo ainda, alterar a associação entre as classes em tempo de execução da aplicação.

De modo intuitivo, podemos definir a composição como quando uma classe usa um objeto (instância de outra classe) para proporcionar uma parte ou o todo em algum comportamento.

No exemplo abaixo, é utilizado a composição, pelo fato do contexto em questão possuir uma relação **“tem-um”**, onde a classe **Job.java** compoem a classe **People.java**. Neste contexto People pode possuir um Job e iniciá-lo.

Nem sempre uma pessoa irá possuir um emprego, por isso, existe uma relação **“tem-um”**, ou seja, usamos composição e não a herança.

```java
package com.leonardorifeli.article.composition.model;

public class People {

    private String name;
    private boolean hasJob;

    public People(final String name, final boolean hasJob) {
        this.name = name;
        this.hasJob = hasJob;

        if(this.hasJob == true) {
            Job job = new Job(this.name, "Developer", true);

            job.checkAndStartJob();
        }
    }

}
```

Repare que, o método construtor, instancia a classe **Job.java** somente se **People** possuir um emprego, com isso, podemos acionar o método **checkAndStartJob()** para iniciar o **job**.

Aqui temos uma relação **“tem-um”** e por isso utilizamos a composição. No exemplo acima, com a utilização da composição, podemos alterar a classe em tempo de execução.

```java
package com.leonardorifeli.article.composition.model;

public class Job {

    private String name;
    private String service;
    private boolean started = false;

    public Job(final String name, final String service, final boolean started) {
        this.name = name;
        this.service = service;
        this.started = started;
    }

    public String checkAndStartJob() {
        if(this.started == true) {
            return "Job has already started.";
        }

        if(this.started == false) {
            this.startJob();
            return "Job is started";
        }

        return "Job stoped";
    }

    private void startJob() {
        this.started = true;
    }

    private void stopJob() {
        this.started = false;
    }

}
```

Classe **Job.java** e suas propriedades e métodos.

# Importância

A herança e a composição são de extrema importância nas linguagens. Atualmente é raro encontrar linguagens que não as suportem. Caso contrário, seria quase impossível quebrarmos grandes soluções em soluções pequenas/modulares.

Sem a reutilização de comportamentos/funcionalidades não teríamos códigos com responsabilidades únicas, que fazem somente uma coisa e fazem muito bem.

# Qual utilizar?

Avalie qual é a relação de um determinado problema. Em caso que exista uma relação **“é-um”** utilizamos a herança, exemplo: banana É uma fruta, carro É um automóvel, pássaro É uma ave etc.

Em casos que a relação tende a funcionalidades e/ou comportamentos específicos e possui uma relação **“tem-um”** , exemplos: pessoa TEM a possibilidade de trabalhar, avião TEM a possibilidade de freiar etc, nestes casos, utilize a composição, aproveitando apenas uma parte (funcionalidade, responsabilidade etc) de outra classe, utilizando o objeto.

Pergunte-se sempre se em todo o ciclo de vida da aplicação ou do código, aquela relação será constante e imutável. Um exemplo de avaliação: Em domínio onde **People** tem relação com **Employee**, neste caso deve-se utilizar a composição, pelo fato de ser algo mutável. Nem sempre **People** terá relação com **Employee**, e se a pessoa ficar desempregada? Portanto, neste caso, o uso da composição é mais adequado do que a herança.

Não use a herança apenas para obter a reutilização de código se não existe uma relação “é-um”. Nestes casos é mais apropriado utilizar a composição.

# Falando em Java

Apenas para abrir um parêntese no artigo, em Java, toda e qualquer classe possui uma herança, neste caso implicitamente. Toda classe em Java, sempre estenderá Object, com isso, alguns métodos são herdados.

Exemplo de herança com object, sobrescrevendo toString():

```java
package com.leonardorifeli.article.inheritance.model;

public class String {

    @Override
    public String toString() {
        return "Is a new string";
    }

}
```

Alguns métodos herdados da classe Object:

- clone();
- equals();
- toString();
- hashCode();
- entre outros.

Documentação da classe Object: [clique aqui](http://docs.oracle.com/javase/8/docs/api/java/lang/Object.html).

# Referências

- [Post de um amigo, Pedro Augusto](https://medium.com/@pedro.barros/heran%C3%A7a-ou-composi%C3%A7%C3%A3o-eis-a-quest%C3%A3o-7ce11fad4737#.ekombw2sy);
- [Composition vs. Inheritance: How to Choose?](https://www.thoughtworks.com/pt/insights/blog/composition-vs-inheritance-how-choose);