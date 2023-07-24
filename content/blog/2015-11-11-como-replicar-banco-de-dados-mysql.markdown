+++
date = "2015-11-11"
title = "Como replicar banco de dados MySQL"
tags = ["tips"]
+++

Saudações, atuo como desenvolvedor Full-Stack em uma empresa de Araraquara (SP), a wab.com.br. Não sou um expert em servidores e aplicações atuando como tal. Porém gosto de estudar, então pratiquei sobre o assunto a qual os escrevo.

Iremos abordar os seguintes tópicos:

1. Introdução
2. Funcionamento da replicação (teoria)
3. Como iremos replicar (esquema)
4. Replicando um banco de dados MySQL (prática)

# Introdução

A replicação de bancos de dados tem como principal objetivo a **redundância**, onde torna-se uma aplicação mais segura contra falhas e **indisponibilidades de outras aplicações (como o respectivo banco de dados)** e por sua vez um backup online dos dados (em tempo real). Nos tópicos abaixo estaremos abordando todos os processos de replicação.

# Como funciona a replicação?

O **MySQL** possui um recurso de comunicação (onde ocorrerá a replicação) modo **Master-Slave**. Sendo assim, um servidor poderá possuir um banco de dados MySQL rodando como **Master** e **N** bancos de dados atuando como **Slave** (em diferentes servidores).

O servidor atuando em modo **Master** irá gravar todas as alterações efetuadas no banco de dados, em um arquivo de **log binário**. Onde o servidor atuando em modo **Slave** irá requisitar o log binário do **Master** e alterará o próprio arquivo de log binário deixando-o idêntico, onde o MySQL atual aplicando as alterações em si.

Segue abaixo um esquema de replicação **Master-Slave**:

![https://rifeli.me/img/posts/2015-11-01-mysql-replication.jpg](https://rifeli.me/img/posts/2015-11-01-mysql-replication.jpg)

**Figura 1.1 - Fonte: Google Images**

# Como iremos replicar (esquema)

Para a replicação do **MySQL**, será utilizado três instâncias **t2.micro** no **Amazon AWS**, conforme abaixo:

![https://rifeli.me/img/posts/2015-11-01-amazon-aws.png](https://rifeli.me/img/posts/2015-11-01-amazon-aws.png)

**Instâncias - Figura 1.2**

**Observação:** Pode-se analisar na **Figura 1.2** (acima) que as três instâncias encontram-se no mesmo datacenter, porém a replicação também funciona em datacenters diferentes.

Onde os respectivos atuarão em modo:

1. **leonardorifeli-001:** Master
2. **leonardorifeli-002:** Slave
3. **leonardorifeli-003:** Slave

Conforme esquema abaixo:

![https://rifeli.me/img/posts/2015-11-01-server-aws-mysql-replication.png](https://rifeli.me/img/posts/2015-11-01-server-aws-mysql-replication.png)

**Figura 1.3**

**PS**: Não entrarei em detalhes sobre o Amazon AWS.

# Replicando um banco de dados MySQL

Vamos ao tão esperado tópico.

As instâncias especificadas na **Figura 1.2** estão rodando com o sistema operacional **Ubuntu Server 14.04 LTS (HVM), SSD Volume Type**, disponibilizado pelo Amazon AWS.

Para a replicação do banco de dados **MySQL** será necessário a instalação da respectiva aplicação (óbvio). Neste post foi utilizado o **mysql-server-5.6**. [Tutorial de instalação](http://sharadchhetri.com/2014/05/07/install-mysql-server-5-6-ubuntu-14-04-lts-trusty-tahr/)

Iremos aplicar os seguintes passos:

1. **Servidor Master:** Configurar o servidor Master (arquivo my.cnf)
2. **Servidor Master:** Criar o usuário de replicação e conceder as devidas permissões
3. **Servidores Slaves:** Configurar o servidor (arquivo my.cnf)
4. **Servidores Slaves:** Informar qual será o servidor **Master**

### 1. Configuração do servidor Master

Após a instalação com sucesso do **MySQL Server 5.6** nas instâncias especificadas na **Figura 1.2**, vamos as respectivas configurações na instância **leonardorifeli-001** que atuará em modo **Master**.

Configurando:

`$ cd /etc/mysql
$ nano my.cnf`

Será necessário editar o arquivo **my.cnf**, ficando da seguinte maneira:

`[mysqld]
server-id = 1
log-bin = mysql-bin
bind-address = 0.0.0.0`

Indicamos que o respectivo servidor será o **Master** (pelo server-id). Após editar, executamos o comando abaixo (para reiniciar o servidor MySQL):

`$ service mysql restart`

### 2. Criar usuário de replicação e conceder as permissões

Agora, iremos criar o usuário para utilizarmos na replicação e conceder para tal as devidas permissões.

Acessando o **MySQL** com usuário root e informando a senha (informado na instalação).

`$ mysql -u root -p`

`CREATE USER slave IDENTIFIED BY "user-rifeli";
GRANT replication SLAVE, replication CLIENT ON *.* TO slave@'IP-LEONARDORIFELI-002' IDENTIFIED BY 'user-rifeli';
GRANT replication SLAVE, replication CLIENT ON *.* TO slave@'IP-LEONARDORIFELI-003' IDENTIFIED BY 'user-rifeli';
FLUSH PRIVILEGES;`