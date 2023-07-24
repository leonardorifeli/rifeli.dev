+++
date = "2016-01-22"
title = "Implementando annotations com doctrine annotation reader em PHP"
tags = ["php","tips"]
+++

Saudações méros mortais, primeiro, peço desculpas pelo período sem trazer novidades para vocês (estive em uma excursão pela galáxia), em breve escreverei um artigo sobre essa viagem. Neste artigo mostrarei sobre **annotations** (é claro, está no título).

Como disse meu amigo [Guilherme Diego](https://medium.com/@guidiego) no artigo [Código Limpo é uma Responsabilidade — Blocos](https://medium.com/@guidiego/c%C3%B3digo-limpo-%C3%A9-uma-responsabilidade-blocos-5be1fdd8d341#.gbx5keq0s):

![https://rifeli.me/img/posts/2016-01-custom-annotations/ler-curtir-compartilhar.png](https://rifeli.me/img/posts/2016-01-custom-annotations/ler-curtir-compartilhar.png)

Enquanto escrevo, vou ouvindo o álbum [As Daylight Dies](https://open.spotify.com/album/6iJEtgHTEbVlSS5isIS71z) da banda Killswitch Engage, é um banda muito bacana.

Enfim, vamos ao que interessa, vem comigo.

# Introdução

Em um projeto recente do qual participei do processo de **refactoring**, o que me auxiliou bastante, foi a implementação de **annotations**, onde foi possível segregar informações estáticas e até atingir algumas práticas de **clean code**, salientando que isso foi uma solução que funcionou bem no respectivo projeto.

Neste artigo eu não discutirei se é o correto, ou não, apenas demonstrarei como implementar **custom annotations** com o **doctrine reader**. Fica sobre teu critério meu chapa!

# Escopo

No exemplo que mostrarei, utilizaremos os seguintes arquivos:

1. **compose.json**: Dependência e informações do projeto;
2. **PeopleAnnotation.php**: Será a nossa annotation, utilizaremos os atributos para receber valores de quem irá consumir a **annotation**;
3. **People.php**: Iremos consumir nossa annotation e informar os respectivos valores para segregarmos informações;
4. **ReaderAnnotation.php**: Neste arquivo iremos juntar tudo e fazer uma sopa de letrinhas.

Irei demonstrar os códigos no artigo, caso necessário, você poderá verificar no [Gist](https://gist.github.com/leonardorifeli/9c12f94b109cb7859ca9).

# Dependência, sim você precisará dela.

Para trabalhar com o **Doctrine Annotation Reader**, será necessário possuir a dependência **“doctrine/common”**, conforme o arquivo **composer.json** abaixo:

```json
{
    "name": "working-annotation",
    "license": "MIT",
    "type": "project",
    "description": "Using annotations",
    "require":
    {
        "doctrine/common": "*"
    },
    "authors": [
        {
            "name": "Leonardo Rifeli",
            "email": "leonardorifeli@gmail.com",
            "homepage": "http://leonardorifeli.com",
            "role": "Back-end Developer"
        }
    ]
}
```

# Desenvolvendo a classe da annotation.

Resumindo, esta classe será responsável pela **annotation**, ou seja, os atributos **públicos** da classe armazenarão informações que poderão ser informadas por quem irá consumir a **annotation** em questão. Segue abaixo o arquivo **PeopleAnnotation.php**, é a nossa annotation:

```php
<?php

/**
* @Annotation
*/
class PeopleAnnotation {

    public $description;
    public $type;

}
```

Repare que, a classe em questão possui uma **annotation**, sendo ela **@Annotation**, isto é necessário para informar ao **Doctrine Annotation Reader** que a classe em questão, realmente é uma **annotation**.

# Consumindo a annotation

Nesta etapa, iremos consumir a annotation **PeopleAnnotation** e informaremos os valores que a annotation disponibiliza.

Salientando, é possível consumir a annotation em:

- classes;
- atributos;
- métodos.

No exemplo abaixo, temos a classe **People**, que comsumirá a **PeopleAnnotation**:

```php
<?php

/**
* @PeopleAnnotation(description="Get all information about a people", type="class")
*/
class People {

    /**
    * @PeopleAnnotation(description="Use to people name", type="attribute")
    */
    private $name;

    /**
    * @PeopleAnnotation(description="Use to people birth date", type="attribute")
    */
    private $birthDate;

    /**
    * @PeopleAnnotation(description="Get people name", type="method")
    */
    public function getName() {
        return $this->name;
    }

    /**
    * @PeopleAnnotation(description="Get people birth date", type="method")
    */
    public function getBirthDate() {
        return $this->birthDate;
    }

}
```

Repare que, a classe **People** está consumindo a **annotation** tanto na respectiva classe, quanto nos atributos e métodos.

# Vamos verificar a **People**. Finalizando a sopa de letrinhas

Nesta etapa final, iremos instanciar a classe **AnnotationReader** para lermos as **annotations** extraídas da classe **People** (que está consumindo a **PeopleAnnotation**).

Classes nativas utilizadas no exemplo:

- **[ReflectionClass()](http://php.net/manual/pt_BR/class.reflectionclass.php)**;
- **[ReflectionObject()](http://php.net/manual/pt_BR/class.reflectionobject.php)**;
- **[ReflectionProperty()](http://php.net/manual/pt_BR/class.reflectionproperty.php)**;
- **[ReflectionMethod()](http://php.net/manual/pt_BR/class.reflectionmethod.php)**.

Abaixo o exemplo:

```php
<?php

require_once 'vendor/autoload.php';
require_once 'PeopleAnnotation.php';
require_once 'People.php';

use Doctrine\Common\Annotations\AnnotationReader;

$annotationReader = new AnnotationReader();

$reflectionClass = new ReflectionClass('People');
$classAnnotations = $annotationReader->getClassAnnotations($reflectionClass);
echo "CLASS ANNOTATIONS:";
var_dump($classAnnotations);
echo '<hr/>';

$people = new People();
$reflectionObject = new ReflectionObject($people);
$objectAnnotations = $annotationReader->getClassAnnotations($reflectionObject);
echo "OBJECT ANNOTATIONS:";
var_dump($objectAnnotations);
echo '<hr/>';

$reflectionProperty = new ReflectionProperty('People', 'name');
$propertyAnnotations = $annotationReader->getPropertyAnnotations($reflectionProperty);
echo "PROPERTY ANNOTATION NAME:";
var_dump($propertyAnnotations);
echo '<hr/>';

$reflectionProperty = new ReflectionProperty('People', 'birthDate');
$propertyAnnotations = $annotationReader->getPropertyAnnotations($reflectionProperty);
echo "PROPERTY ANNOTATION BIRTH DATE";
var_dump($propertyAnnotations);
echo '<hr/>';

$reflectionMethod = new ReflectionMethod('People', 'getName');
$methodAnnotations = $annotationReader->getMethodAnnotations($reflectionMethod);
echo "Method ANNOTATIONS getName:";
var_dump($propertyAnnotations);
echo '<hr/>';

$reflectionMethod = new ReflectionMethod('People', 'getBirthDate');
$methodAnnotations = $annotationReader->getMethodAnnotations($reflectionMethod);
echo "Method ANNOTATIONS getBirthDate: ";
var_dump($propertyAnnotations);
```

# Resultados

```php
CLASS ANNOTATIONS:
array (size=1)
  0 =>
    object(PeopleAnnotation)[11]
      public 'description' => string 'Get all information about a people' (length=34)
      public 'type' => string 'class' (length=5)
OBJECT ANNOTATIONS:
array (size=1)
  0 =>
    object(PeopleAnnotation)[15]
      public 'description' => string 'Get all information about a people' (length=34)
      public 'type' => string 'class' (length=5)
PROPERTY ANNOTATION NAME:
array (size=1)
  0 =>
    object(PeopleAnnotation)[18]
      public 'description' => string 'Use to people name' (length=18)
      public 'type' => string 'attribute' (length=9)
PROPERTY ANNOTATION BIRTH DATE
array (size=1)
  0 =>
    object(PeopleAnnotation)[19]
      public 'description' => string 'Use to people birth date' (length=24)
      public 'type' => string 'attribute' (length=9)
Method ANNOTATIONS getName:
array (size=1)
  0 =>
    object(PeopleAnnotation)[19]
      public 'description' => string 'Use to people birth date' (length=24)
      public 'type' => string 'attribute' (length=9)
Method ANNOTATIONS getBirthDate:
array (size=1)
  0 =>
    object(PeopleAnnotation)[19]
      public 'description' => string 'Use to people birth date' (length=24)
      public 'type' => string 'attribute' (length=9)
```

# Referências

1. [Artigo sobre o assunto em inglês](http://masnun.com/2012/08/12/using-annotations-in-php-with-doctrine-annotation-reader.html)
2. [Doctrine - Documentação oficial](http://doctrine-common.readthedocs.org/en/latest/reference/annotations.html)
3. [Documentação oficial PHP.net](http://php.net/)

# Conclusão

A utilização de **annotation** pode facilitar diversas condições, salientando que, a necessidade de implementar **custom annotation** varia de situação. Use o bom senso de programador.

Quaisquer feedbacks serão bem-vindos, fique à vontade para comentar e/ou implementar alguma informação.

Até breve méros mortais e eternos aprendizes (todos somos).