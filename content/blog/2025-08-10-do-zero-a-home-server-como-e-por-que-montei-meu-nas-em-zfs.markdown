---
title: "De zero a Home Server: como e por que montei meu NAS em ZFS"
draft: false
date: 2025-08-10T00:00:00.000Z
description: "Comecei a programar aos 14 anos com um site de streaming de áudio e um servidor de Tibia. Desde então, soluções self-hosted sempre fizeram parte da minha vida, permitindo aprender e experimentar. Agora, depois de quase dez anos, montei um home server moderno, com NAS em ZFS, Docker e Cloudflare Tunnel."
comments: true
keywords: [
  "Home Server",
  "NAS",
  "ZFS",
  "Ubuntu Server",
  "Cloudflare Tunnel",
  "Portainer",
  "Docker",
  "infraestrutura",
  "servidor local",
  "servidor em casa",
  "self-hosted",
  "storage",
  "armazenamento"
]
tags:
  - infra-estrutura
  - server
  - self-hosted
---

# Introdução

<p align="center">
  <img src="/static/images/posts/home-server/19.png" alt=""><br>
  <em>Sempre em busca da melhor versão</em>
</p>

Comecei a programar aos 14 anos, tendo um site de streaming de áudio e um servidor de Tibia (vulgo OT Server), na época rodando na versão 8.5. Desde cedo, **soluções self-hosted** foram parte essencial do meu aprendizado: de protocolos de comunicação até sistemas de auto-gestão.

Isso se estendeu até em uma solução pessoal para gestão de finanças, também self-hosted, feita em PHP. [Dá um visu aqui](https://github.com/leonardorifeli/morfeu).

Depois de quase dez anos, decidi montar novamente meu próprio **home server** para centralizar arquivos, ter mais controle e segurança, expandir conhecimentos em infraestrutura e substituir serviços pagos por alternativas self-hosted.

**O resultado foi um ambiente poderoso:**

- **NAS em ZFS (5TB)**
- Containers Docker gerenciados via **Portainer**
- Interface web para gestão dos arquivos
- Acesso externo seguro para serviços e SSH via **Cloudflare Tunnel**

---

# O que é NAS e por que usar RAID/ZFS?

Antes de mergulhar na prática, vale entender alguns conceitos fundamentais.

### 📦 O que é NAS?
**NAS (Network Attached Storage)** é basicamente um servidor de arquivos conectado à rede.

- Funciona como uma **central de armazenamento**, acessível de qualquer dispositivo (PC, notebook, celular, TV etc).
- Diferente de um HD externo, o NAS está sempre disponível, seja localmente ou pela internet (no nosso caso, via **Cloudflare Tunnel**).
- É comum em empresas, mas também faz todo sentido em casa, para fotos, vídeos, documentos ou até para hospedar **Nextcloud** ou **Jellyfin/Plex**.

### 🔄 O que é RAID?
**RAID (Redundant Array of Independent Disks)** combina múltiplos discos em um volume lógico, trazendo:
- **Redundância**: se um disco falhar, os dados continuam acessíveis.
- **Performance**: alguns níveis distribuem dados entre discos, acelerando leitura/escrita.

**Exemplos:**
- **RAID 1**: espelhamento — dois discos, um copia o outro.
- **RAID 5**: três ou mais discos, com paridade (suporta falha de 1 disco).
- **RAID 6**: como o RAID 5, mas suporta falha de até 2 discos.

⚠️ **Importante**: RAID não substitui backup. Ele apenas protege contra falhas físicas. (aprendi isso da pior forma 😅)

### 🛡️ E onde entra o ZFS?
O **ZFS (Zettabyte File System)** combina **filesystem + RAID + volume manager** em uma só solução.

Ele oferece:
- **Integridade de dados**: cada bloco tem checksum, evitando corrupções silenciosas.
- **Snapshots e clones**: restauração rápida de versões anteriores.
- **Compressão transparente**: economiza espaço automaticamente.
- **Escalabilidade**: projetado para petabytes de dados (eu sigo com 5TB, por enquanto).

No meu setup, uso **ZFS com RAID-Z** (semelhante ao RAID 5), que equilibra espaço, performance e tolerância a falhas.

---

# O que é Cloudflare e por que usei no meu Home Server

Quando expomos serviços caseiros na internet, temos duas grandes preocupações:
- **Segurança** (não deixar a rede vulnerável)
- **Praticidade** (dispensar configurações complexas de NAT/IP fixo)

É aí que entra o **Cloudflare**.

### 🌍 O que é Cloudflare?
O **Cloudflare** é famoso pelo **CDN** e **proteção contra DDoS**, mas também oferece recursos que facilitam o self-hosting, como o **Cloudflare Tunnel**.

### 🚇 O que é Cloudflare Tunnel?
O **Cloudflare Tunnel** cria um túnel seguro entre meu servidor e a rede Cloudflare.

**Benefícios:**
- Nada de abrir portas no roteador
- Não preciso de IP fixo
- Meus serviços ficam acessíveis via domínio com **HTTPS válido automático**

**Exemplo prático:**
- `https://files.seudominio.com` → File Browser (porta 8080)
- `https://portainer.seudominio.com` → Portainer (porta 9443)

Tudo isso sem precisar configurar NGINX ou Let's Encrypt manualmente.

### 🎯 Por que escolhi o Cloudflare?
- **Facilidade:** poucos comandos e já estava acessível.
- **Segurança:** tráfego criptografado fim a fim.
- **Custo baixo:** plano gratuito cobre bem (o Tunnel avançado custa ~US$10/mês).
- **Escalabilidade:** novos serviços são só uma linha no `config.yml`.

---

# Setup

<p align="center">
  <img src="/static/images/posts/home-server/18.png" alt=""><br>
  <em>Server com AMD-A8-5600k, 16GB RAM e NAS 5TB</em>
</p>

### 🖥️ Servidor
- **CPU**: AMD-A8-5600k
- **RAM**: 16 GB
- **NAS**: pool ZFS de múltiplos HDs (5 TB)
- **SO**: Ubuntu Server 24.10

Os HDs estão ligados via **gaveta hot-swap**, e não diretamente à placa-mãe.

**Vantagens:**
- 🔄 Troca rápida de discos defeituosos
- 📦 Expansão simples (basta adicionar novo HD)
- 🛡️ Perfeito para ZFS/RAID, com reconstrução automática (resilver)

<p align="center">
  <img src="/static/images/posts/home-server/17.png" alt=""><br>
  <em>NAS com gavetas hot-swap</em>
</p>

### ⚡ Gestão de energia
Para mitigar quedas de energia, configurei:
- **Gerador**: 3.75 kVA 3000W
- **Nobreak SMS Lite 1200VA** (~6h autonomia)
- **Nobreak SMS NET 4+ 1400VA** (~8h autonomia)

### 💰 Custo de eletricidade

| Potência média | kWh/mês | Custo/mês (R\$ 1,00/kWh) |
| -------------- | ------: | -----------------------: |
| 80 W           |    57,6 |            **R\$ 57,60** |
| 100 W          |    72,0 |            **R\$ 72,00** |
| 150 W          |   108,0 |           **R\$ 108,00** |
| 200 W          |   144,0 |           **R\$ 144,00** |

No meu caso:
- **Idle/leve**: 80–120 W
- **Carga moderada**: 150–200 W

Em média, gasto **R\$ 60–110/mês**, dependendo da carga e da tarifa.

---

# Arquitetura

<p align="center">
  <img src="/static/images/posts/home-server/flow.jpeg" alt=""><br>
  <em>Arquitetura do Home Server</em>
</p>

### 🔍 Como funciona o fluxo
1. **Usuário** → acessa pelo navegador
2. **Internet** → tráfego normal pela rede pública
3. **Cloudflare Tunnel** → cria ponte segura sem NAT/IP fixo
4. **Servidor (Ubuntu 24.10)** → roda Docker + ZFS
5. **NAS (ZFS Pool)** → armazena dados com redundância e snapshots

### ✅ Benefícios
- **Segurança:** IP residencial não exposto
- **Flexibilidade:** qualquer container pode virar subdomínio
- **Resiliência:** ZFS garante integridade dos dados
- **Simplicidade:** acesso com domínio e SSL válido

---

# 💡 Dicas

### 🔐 Segurança
- **Ative o fail2ban** para proteger o SSH:
  ```bash
  sudo apt install fail2ban -y
  sudo systemctl enable fail2ban
  sudo systemctl start fail2ban
  ```
  Configuração básica:
  ```ini
  [sshd]
  enabled = true
  port    = ssh
  filter  = sshd
  logpath = /var/log/auth.log
  maxretry = 5
  ```
- Use **chave SSH** em vez de senha.
- **Cloudflare Access** (opcional): autenticação em duas etapas para subdomínios.

### ⚡ Eficiência energética
- Configure **spindown** para HDs pouco usados.
- Ajuste CPU para modo `powersave`.

### 🛡️ Resiliência
- Rode `zpool scrub` periodicamente.
- Configure **snapshots automáticos** no ZFS.
- Backup externo continua essencial.

### 🧩 Automação
- Configure o **cloudflared** para iniciar no boot.
- Centralize logs dos containers via **Portainer**.

---

# ✅ Conclusão

Montar esse home server foi mais do que um exercício técnico: foi uma forma de ter **controle total dos meus dados**, aprendendo tecnologias enterprise como **ZFS, Docker e Cloudflare Tunnel** no meu próprio ambiente.

Hoje centralizo arquivos, rodo containers em produção pessoal e acesso tudo de forma **segura e simples pela internet**, sem depender de serviços pagos ou limitados.

Existem desafios (manutenção, energia, configuração), mas o ganho em flexibilidade e aprendizado compensa. E o melhor: é facilmente expansível — seja com mais HDs no ZFS, novos containers ou serviços como Nextcloud e Jellyfin.

No fim, percebi que um **NAS caseiro pode ser tão poderoso quanto soluções comerciais**, com a liberdade de adaptar às minhas necessidades. 🚀

👉 E você, montaria o seu próprio servidor ou prefere uma solução pronta? Comenta aí!

> 🏊‍♂️🚴‍♂️🏃‍♂️ “Good dream is a dream lived” — Avelino, Thiago

---

# 📌 Changelog
- **2025-08-10** → Versão inicial do setup publicada
