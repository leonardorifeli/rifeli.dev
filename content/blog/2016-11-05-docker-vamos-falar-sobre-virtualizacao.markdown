---
title: "Docker: Vamos falar sobre virtualização?"
draft: false
date: 2016-11-05T00:00:00.000Z
description: ""
categories:
  - Desenvolvimento
tags:
  - Docker
---


No desenvolvimento de aplicações, podemos optar por usar máquinas virtuais (VMs) para facilitar o gerenciamento e provisionamento de serviços. Para isso, podemos citar o Vagrant. Mas, o provisionamento de máquinas virtuais demanda grande quantidade de tempo, além do fato do consumo demasiado de espaço em disco, recursos em geral da máquina que será o host.

# Sumário

- Introdução;
- Um pouco sobre virtualização;
- O que é Docker;
- O que é um contêiner;
- Namespaces;
- Algumas vantagens do Docker;
- Principais funcionalidades;
- Docker image;
- Dockerfile;
- Docker compose;
- Referências;
- Conclusão.

# Introdução

Sim, eu fiquei alguns meses sem escrever! Sorry!

Sem ressentimentos, o assunto deste artigo é muito importante. Falaremos sobre virtualização, isso mesmo. Sim, eu sei que se fôssemos descrevê-lo em muitos detalhes, levaríamos longos e diversos artigos. Portanto, o objetivo deste artigo é trazer um “resumão” sobre este assunto. Falarei sobre **virtualização tradicional**, **virtualização por contêineres** e apresentarei o **[Docker](https://www.docker.com/)** (caso não o conheça).

O objetivo deste artigo é descrever as teorias por volta do tema, farei um segundo artigo, que será um **na prática** com o Docker.

Sem mais delongas, chega mais que vai ser muito foda!

# Pegue um café

Corre lá e pegue um pouco de café, o assunto será bem interessante.

![https://rifeli.me/img/posts/2016/11/03/get-coffee.gif](https://rifeli.me/img/posts/2016/11/03/get-coffee.gif)

# Um pouco sobre Virtualização

No desenvolvimento de aplicações, podemos optar por usar máquinas virtuais (VMs) para facilitar o gerenciamento e provisionamento de serviços. Para isso, podemos citar o [Vagrant](https://www.vagrantup.com/). Mas, o provisionamento de máquinas virtuais demanda grande quantidade de tempo, além do fato do consumo demasiado de espaço em disco, recursos em geral da máquina que será o host.

Assim surgiu o [LXC](https://en.wikipedia.org/wiki/LXC). O Linux Container, ou LXC, foi lançado em 2008 e é uma tecnologia que permite a criação de múltiplas instâncias isoladas de um determinado sistema operacional. Ou seja, uma maneira de virtualizar aplicações dentro de uma máquina (hospedeira) usando todos os recursos disponíveis no mesmo Kernel da máquina hospedeira.

Tendo como precursor, o comando [chroot](https://en.wikipedia.org/wiki/Chroot), que foi lançado em 1979 pelo [Unix V7](https://en.wikipedia.org/wiki/Version_7_Unix), como intuito de segregar acessos de diretórios e evitar que os usuários possam acessar à estrutura raiz **(/)**. Este conceito evoluiu alguns anos, com o lançamento do comando [jail](https://www.freebsd.org/cgi/man.cgi?query=jail&sektion=8&manpath=freebsd-release-ports), no SO [FreeBSD 4](https://www.freebsd.org/releases/4.0R/announce.html).

Com relação à virtualização, a diferença está no fato do **LXC** não necessitar de uma camada de sistema operacional para cada aplicação. Como você pode verificar na imagem abaixo.

![https://rifeli.me/img/posts/2016/11/03/c-structure.png](https://rifeli.me/img/posts/2016/11/03/c-structure.png)

Ao compararmos o **LXC** com a **virtualização tradicional**, fica mais claro que uma aplicação sendo executada em um LXC demanda muito menos recursos, consumindo menos espaço em disco e com um nível de portabilidade muito mais abrangente.

# O que é o Docker?

![https://rifeli.me/img/posts/2016/11/03/docker.png](https://rifeli.me/img/posts/2016/11/03/docker.png)

Nasceu como um projeto da [DotCloud](https://cloud.docker.com/), uma empresa **PaaS** (Platform as a Service).

Basicamente, Docker é uma plataforma open-source, escrita em **Go**, tendo como finalidade, criar e gerenciar ambientes isolados para aplicações. O Docker garante que, cada contêiner tenha tudo que uma aplicação precisa para ser executada.

Em outras palavras, o Docker é uma ferramenta de empacotamento de uma aplicação e suas dependências em um contêiner virtual que pode ser executado em um servidor linux.

# Então, Docker é uma VM?

Não, contêineres docker possuem uma arquitetura diferente que permite maior portabilidade e eficiência.

![https://rifeli.me/img/posts/2016/11/03/docker-system.png](https://rifeli.me/img/posts/2016/11/03/docker-system.png)

# Tecnologias e ideias utilizadas

Cara, contêiner não é nada novo, Docker surgiu para facilitar o uso deles. Abaixo um resumo de tecnologia e o ano da primeira versão:

![https://rifeli.me/img/posts/2016/11/03/technologies-year.png](https://rifeli.me/img/posts/2016/11/03/technologies-year.png)

# O que é um contêiner?

Vamos fazer uma comparação prática. Contêiner nada mais é que uma caixa de metal, onde é colocado tudo o que couber. Contêineres possuem dimensões e interfaces comuns, onde guindastes e guinchos podem ser acoplados para colocá-los em navios ou caminhões.

Beleza e, no contexto do artigo?

A virtualização em contêineres é muito mais leve, onde, temos cada contêiner como uma instância isolada em um kernel de sistema operacional. Os contêineres possuem interfaces de redes virtuais, processos e sistemas de arquivos independentes.

Algumas características de um contêiner Docker:

- Dependente de uma imagem (falaremos logo abaixo);
- Geram novas imagens;
- Conectividade com o host e outros contêineres;
- Execuções controladas, CPU, RAM, I/O, etc.

# Namespaces

O Docker utiliza os recursos de [Namespaces](https://en.wikipedia.org/wiki/Namespace) para dispor um espaço de funcionamento isolado para os contêineres. Contudo, quando um contêiner é criado, também é criado um conjunto de namespaces e este, por sua vez, cria uma camada para isolamento para os grupos de processos. Abaixo seguem os tipos de namespaces:

- **PID:** isolamento de processos.
- **NET:** controle de interfaces de rede.
- **IPC:** controle dos recursos de IPC (InterProcess Communication).
- **MNT:** gestão de pontos de montagem.
- **UTC (Unix Timesharing System):** provém todo o isolamento de recursos do kernel (justamente a camada de abstração como mostra a imagem).

# Algumas Vantagens do Docker

- Baixo overhead e tempo de boot;
- Kernel compartilhado com o Host;
- Contêineres rodam isoladamente;
- Facilidade de configuração do ambiente de desenvolvimento para novos membros do time;
- Acabar com a história do “na minha máquina funcionava”.

# Principais Funcionalidades

- **Versionamento**: o Docker permite que você versione as alterações de um contêiner. Isto permite verificar as diferenças entre versões, fazer commit de novas versões e até mesmo fazer rollback (isso é muito importante haha).
- **Compartilhamento de imagens**: sim, existe um repositório de contêineres. O **Docker Hub**. Ele possui milhares de imagens com as mais diversas aplicações. Você pode rapidamente criar sua aplicação com uma base já desenvolvida e ainda criar sua base e compartilhá-la na comunidade.
- **Licença open-source**: licenciado como **Apache License 2.0**, mantém os códigos fonte disponíveis para facilitar o desenvolvimento colaborativo.
- **Hardware**: exige poucos recursos de processos, memória e espaço em disco.
- **Comunicação entre contêineres**: conectar contêineres via mapeamentos de porta **TCP/IP** não é a única forma de disponibilizar recursos entre eles.

E uma das principais:

![https://rifeli.me/img/posts/2016/11/03/dependency-hell.png](https://rifeli.me/img/posts/2016/11/03/dependency-hell.png)

- **Evita Dependency Hell**: um dos maiores problemas que os desenvolvedores de software convivem, é o gerenciamento de dependências. O Docker evita problemas neste gerenciamento.

# Docker Image

Uma imagem Docker nada mais é que, um arquivo inerte, imutável, que é essencialmente instanciado por um contêiner. As imagens são criadas com o comando **build** (entrarei em mais detalhes na segunda parte do artigo) e elas serão consumidas por um contêiner, ou seja, um contêiner é a instância de uma imagem. Como as imagens podem ser muito grandes, as imagens são projetadas para serem compostas por camadas de outras imagens.

Basicamente, uma imagem é um conjunto de camadas que você descreve e, quando você inicia uma imagem, você terá um contêiner em execução desta imagem e você pode ter muitos contêineres da mesma imagem. Portanto, uma imagem em execução é um contêiner.

E como criar uma imagem, ou seja, como descrever as camadas de uma imagem? Chega mais…