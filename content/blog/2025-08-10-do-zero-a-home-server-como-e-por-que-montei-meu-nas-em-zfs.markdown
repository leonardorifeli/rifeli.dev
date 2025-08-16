---
title: "De zero a Home Server: como e por que montei meu NAS em ZFS"
draft: false
date: 2025-08-10T00:00:00.000Z
description: "Comecei a programar aos quatorze anos, tendo um site de streaming de áudio e um servidor de Tibia (vulgo OT Server), na época rodando na versão 8.5. Ter soluções self-hosted, sempre foi algo que gostei muito e foi onde consegui estudar e aprender muito. Andei em diversas esféras, de protocolos de comunicação até soluções personalizadas para auto gestão."
comments: true
keywords: [
  "Software",
  "Develop",
  "Setup DEV",
  "rifeli",
  "Software Developer",
  "Data Science",
  "CTO Harmo",
  "scalable architectures",
  "data engineering",
  "cloud solutions",
  "carreira desenvolvedor",
  "kubernets",
  "gerenciamento de cluster k8s",
  "home-server",
  "servidor local",
  "servidor em casa"
]
tags:
  - infra-estrutura
  - server
---

# Introdução

<p align="center">
  <img src="/static/images/posts/home-server/19.png" alt=""><br>
  <em>Sempre em busca da melhor versão</em>
</p>

Comecei a programar aos quatorze anos, tendo um site de streaming de áudio e um servidor de Tibia (vulgo OT Server), na época rodando na versão 8.5. Ter soluções self-hosted, sempre foi algo que gostei muito e foi onde consegui estudar e aprender muito. Andei em diversas esféras, de protocolos de comunicação até soluções personalizadas para auto gestão.

Isso se extendeu até em uma solução para gestão de finanças pessoais, rodando em self-hosted, feito em PHP. [Dá um visu aqui](https://github.com/leonardorifeli/morfeu).

E depois de quase dez anos, decidi montar novamente meu próprio **home server** para centralizar arquivos, ter mais controle e segurança, expandir meus conhecimentos sobre infraestrutura e claro, visando substituir serviços pagos por soluções self-hosted.

**O resultado foi um ambiente poderoso:**

- **ZFS para o meu NAS (5TB)**;
- Containers Docker gerenciados via **Portainer**;
- Interface web para gestão dos arquivos do NAS;
- Acesso externo seguro para os serviços e SSH, via Cloudflare.

# O que é NAS e por que usar RAID/ZFS?

Antes de mergulhar na parte prática, vale entender alguns conceitos fundamentais, para você poder aproveitar o melhor deste artigo:

### 📦 O que é NAS?

**NAS (Network Attached Storage)** é basicamente um servidor de arquivos conectado à rede.

Ele funciona como uma central de armazenamento, onde você pode salvar, organizar e acessar dados de qualquer dispositivo (PC, notebook, celular, TV etc).

Diferente de um HD externo plugado no computador, o NAS fica sempre disponível na rede, podendo ser acessado localmente ou até pela internet (no nosso caso, com ajuda do **Cloudflare Tunnel**).

É muito usado em empresas para centralizar backups, mas também faz todo sentido em casa para armazenar fotos, vídeos, documentos e até hospedar serviços como **Nextcloud** ou **Plex/Jellyfin**.

### 🔄 O que é RAID?

**RAID (Redundant Array of Independent Disks)** é uma forma de combinar vários discos em um único volume lógico, com foco em:

- **Redundância**: se um disco falhar, os dados continuam acessíveis;
- **Performance**: em alguns níveis de RAID, os dados são distribuídos entre os discos, acelerando leitura e escrita.

**Exemplos:**

- **RAID 1**: espelhamento, dois discos iguais, um é cópia do outro;
- **RAID 5**: três ou mais discos, com paridade, permite perder um sem perder dados;
- **RAID 6**: semelhante ao **RAID 5**, mas suporta falha de até dois discos.

⚠️ **Importante**: RAID não substitui backup. Ele apenas protege contra falha física de disco. (eu sofri da pior forma \o/)

### 🛡️ E onde entra o ZFS?

O **ZFS (Zettabyte File System)** é um sistema de arquivos avançado que combina funções de RAID + volume manager + filesystem em uma única tecnologia.

**Ele oferece:**

- **Integridade de dados**: cada bloco armazenado tem checksum, detectando e corrigindo corrupções;
- **Snapshots e clones**: criar "fotos" instantâneas do estado do sistema, úteis para backup e rollback;
- **Compressão transparente**: economiza espaço automaticamente;
- **Escalabilidade absurda**: projetado para lidar com petabytes de dados (vou continuar em 5TB no máximo).

No meu setup, uso **ZFS com RAID-Z** (semelhante ao RAID 5), que oferece um bom equilíbrio entre espaço, performance e tolerância a falhas.

# O que é Cloudflare e por que usei no meu Home Server

Quando falamos em expor serviços caseiros para a internet, surgem logo duas preocupações:

- Segurança (não deixar a rede interna vulnerável);
- Praticidade (evitar configurações complicadas de roteador, NAT ou IP fixo).

É aí que entra o Cloudflare.

### O que é Cloudflare?

O **Cloudflare** é uma empresa que oferece serviços de rede e segurança para aplicações na internet. Eles são muito conhecidos pelo **CDN (Content Delivery Network)** e pelo proteção contra ataques **DDoS**, mas também oferecem recursos que facilitam a vida de quem roda serviços self-hosted, como o **Cloudflare Tunnel** (sim, é pago).

### O que é Cloudflare Tunnel?

O **Cloudflare Tunnel** cria um túnel seguro entre o servidor e a rede da Cloudflare.

**Isso significa que:**

- Não é necessário abrir portas no roteador;
- Não precisa ter IP fixo contratado;
- Os serviços locais ficam acessíveis pela internet através de um domínio com HTTPS válido.

**Exemplo prático:**

- https://files.seudominio.com → aponta para o algum container rodando local em alguma porta (ex 8080).
- https://portainer.seudominio.com → aponta para o algum container rodando local em alguma porta (ex 9443).

Tudo isso acontece com certificados **SSL automáticos**, sem precisar configurar NGINX (é uma mega diversão, recomendo).

### 🎯 Por que escolhi o Cloudflare?

- **Facilidade**: em poucos comandos meu home server já estava acessível pela internet;
- **Segurança**: todo o tráfego passa pelo túnel criptografado e protegido;
- **Custo baixo**: o plano gratuito do Cloudflare já cobre bem, mas o Tunnel é pago ($10/mês);
- **Escalabilidade**: se eu quiser expor mais serviços (ex.: Nextcloud, Jellyfin), basta adicionar no config.yml.

# Setup

Bom, depois de falarmos muito sobre questões teóricas, bora que vou te mostrar todo setup do meu **Home Server**.

<p align="center">
  <img src="/static/images/posts/home-server/18.png" alt=""><br>
  <em>Server with AMD-A8-5600k, with 16GB of ram, and NAS with 5TB</em>
</p>

### Servidor

Para montar esse home server, utilizei uma máquina com AMD-A8-5600k, com 16GB de RAM, e NAS com 5TB, rodando Ubuntu Server 24.10.

- **Servidor:** AMD-A8-5600k, with 16GB of ram, and NAS with 5TB;
- **NAS:** com ZFS consegui ter um pool com vários HDs;

O diferencial é que os HDs não estão ligados diretamente à placa-mãe, mas em um hardware de gaveta (hot-swap bay).

**Isso me dá algumas vantagens:**

- 🔄 **Troca rápida de discos**: se um HD apresentar falha, consigo removê-lo e colocar outro sem precisar abrir o servidor inteiro;
- 📦 **Expansão simples**: basta adicionar um novo HD na gaveta para expandir o pool (no caso, consigo trocar HD se precisar);
- 🛡️ **Perfeito para ZFS/RAID**: quando um disco é removido, o ZFS identifica e permite resilver (reconstruir os dados) no novo disco automaticamente.

Na prática, essa escolha trouxe a flexibilidade de um **NAS comercial** com a liberdade de um **home server** montado por conta própria.

<p align="center">
  <img src="/static/images/posts/home-server/17.png" alt=""><br>
  <em>NAS com as gavetas</em>
</p>

### Gestão de energia:

Aqui é um ponto que muitas pessoas acabam tendo dúvidas, e claro, é interessante ter um recurso de backup para energia

- Gerador: 3.75 kVA 3000W 4-Stroke Electric Start;
- Nobreak SMS lite 1200VA (autonomia de ~6h);
- Nobreak SMS NET 4+ 1400VA (autonomia de ~8h).

### Custo de eletricidade

| Potência média | kWh/mês | Custo/mês (R\$ 1,00/kWh) |
| -------------- | ------: | -----------------------: |
| 80 W           |    57,6 |            **R\$ 57,60** |
| 100 W          |    72,0 |            **R\$ 72,00** |
| 150 W          |   108,0 |           **R\$ 108,00** |
| 200 W          |   144,0 |           **R\$ 144,00** |

No meu caso. o consumo típico é:

- **Idle/leve:** ~80–120 W
- **Carga moderada:** ~150–200 W

Se meu setup ficar a maior parte do tempo em idle com ZFS e 2–4 HDDs girando, é algo entre **~R$60 e R$ 110/mês** (80–150 W médios), variando um pouco devido a tarifa e quantos serviços/containers ficam ativos.

# Arquitetura

Para entender como tudo se conecta, montei um diagrama simples da minha arquitetura:

<p align="center">
  <img src="/static/images/posts/home-server/flow.jpeg" alt=""><br>
  <em>Arquitetura completa</em>
</p>

### Como funciona o fluxo

- **Usuário (eu)** → acesso os serviços a partir de qualquer computador ou celular usando um navegador;
- **Internet** → a conexão é roteada normalmente pela rede pública;
- **Cloudflare Tunnel** → aqui entra a mágica: o tráfego passa pelo túnel seguro da Cloudflare, que cria uma ponte entre meu domínio na internet e o servidor dentro de casa, sem precisar abrir portas no roteador ou usar IP fixo;
- **Servidor (em casa)** → máquina principal rodando Ubuntu Server 24.10, containers Docker e o ZFS como camada de armazenamento;
- **NAS (ZFS Pool)** → todos os dados ficam armazenados em múltiplos HDs organizados pelo ZFS, com redundância, snapshots e integridade de dados.

### Benefícios dessa arquitetura

- **Segurança:** não exponho meu IP residencial diretamente. O tráfego chega pela Cloudflare já criptografado;
- **Flexibilidade:** qualquer serviço que eu rodar em containers (File Browser, Portainer, Nextcloud, Jellyfin) pode ser publicado facilmente com um subdomínio;
- **Resiliência:** o ZFS garante que meus dados fiquem protegidos contra falhas de disco;
- **Simplicidade:** para acessar meus arquivos ou gerenciar containers, só preciso abrir o navegador e digitar o domínio configurado.

# Dicas

Durante a configuração, percebi alguns pontos que fazem bastante diferença no dia a dia. Aqui estão minhas principais dicas:

### 🔐 Segurança em primeiro lugar

- **Ativar o fail2ban:** ele monitora os logs do SSH (e de outros serviços) e bloqueia automaticamente IPs que tentam forçar senha.

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**Arquivo básico de configuração:**

```bash
[sshd]
enabled = true
port    = ssh
filter  = sshd
logpath = /var/log/auth.log
maxretry = 5
```

Assim, ataques de força bruta são mitigados de forma simples. E sim, eles acontecem e muito.

- **Use autenticação por chave SSH:** desative login por senha no SSH (PasswordAuthentication no).
- **Cloudflare Access (opcional):** além do túnel, você pode adicionar autenticação em duas etapas diretamente na Cloudflare para acessar os subdomínios.

### ⚡ Eficiência energética

- Configure spindown para os HDs menos usados (economiza energia e ruído);
- Ajuste o governor da CPU para powersave quando não precisar de alto desempenho contínuo.

### 🛡️ Resiliência e backups

- Configure **scrubs** periódicos no ZFS para verificar a integridade dos dados;
- Use snapshots automáticos no ZFS para recuperar versões anteriores de arquivos.

**Lembre-se:** RAID/ZFS não substitui backup. Tenha uma cópia em outro lugar (outro HD, nuvem, etc).

### 🧩 Automação

- Configure o cloudflared tunnel para iniciar no boot;
- Centralize logs dos containers no Portainer para facilitar troubleshooting (é importante).

# Conclusão

Montar novamente meu home server foi mais do que um exercício técnico. foi uma forma de ter controle total sobre meus dados e ao mesmo tempo aprimorar o conhecimento de tecnologias de nível enterprise, como **ZFS**, **Advanced Docker** e **Cloudflare Tunnel**, dentro de casa.

Hoje consigo centralizar arquivos, rodar containers em produção pessoal e acessar tudo de forma segura e simples pela internet, sem depender de serviços pagos ou limitações de soluções prontas.

Claro que existem desafios (manutenção, consumo de energia, configurações manuais), mas a flexibilidade e o aprendizado compensam. Além disso, posso expandir facilmente: seja adicionando mais HDs ao ZFS, novos containers via Portainer ou até serviços completos como Nextcloud e Jellyfin.

No fim, esse projeto me mostrou que um NAS caseiro pode ser tão poderoso quanto soluções comerciais, e ainda me dá a liberdade de adaptar conforme minhas necessidades. 🚀

👉 E você? Montaria o seu próprio servidor ou prefere uma solução pronta? Comenta aí!

> 🏊‍♂️🚴‍♂️🏃‍♂️ “Good dream is a dream lived” — Avelino, Thiago

# Changelog

Pretendo deixar esse artigo atualizado, abaixo um changelog com as modificações.

2025-08-10 - Adicionado a v0 do setup