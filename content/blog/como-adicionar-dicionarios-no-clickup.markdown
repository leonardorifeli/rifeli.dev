---
title: "Como adicionar dicionários no ClickUp"
draft: false
date: 2025-10-28T00:00:00.000Z
description: "Aprenda a ativar e configurar dicionários personalizados no ClickUp para evitar erros de digitação e melhorar a comunicação entre equipes."
comments: true
keywords: [
  "boas práticas",
  "gerenciamento de times em startup",
  "alternativa para slack e discord",
  "como ajustar dicionário no clickup"
]
tags:
  - gestão
  - chat
---

<img id="image-custom" src="https://clickup.com/images/clickup-v3/CU_3.0_Task_Types.png" alt="ClickUP Platform" />
<p id="image-legend">ClickUp</p>

## Introdução

Aqui na **Harmo**, migramos do Slack para o Discord em 2022. A mudança parecia ideal no início, afinal, conseguimos liberdade, integração com bots e boa performance.  
Mas, com o tempo, os desafios de **governança, histórico e centralização da informação** começaram a pesar. Precisávamos de uma ferramenta que reunisse tudo: chat, tarefas, docs, dashboards e gestão, sem o custo de um carro por mês.

Foi aí que chegamos ao **ClickUp**.
E não, este artigo não é patrocinado 😄, é apenas o relato de quem usa intensamente a ferramenta e descobriu alguns *truques* úteis, como **ativar dicionários personalizados** para escrever sem erros (e sem perder o português).

Afinal, sempre uso OS em US.

## O ClickUp como central de operações

O ClickUp se posiciona como uma plataforma "tudo-em-um" para produtividade de times.  
A ideia é simples: **um único lugar para conversar, planejar, fazer calls (isso é muit massa), documentar e acompanhar tudo o que acontece** dentro da empresa. Também tendo a opção de conectar tudo isso com modelos LLM.

Na Harmo, usamos o ClickUp como nossa central de operações para praticamente tudo:

- Comunicação assíncrona entre times técnicos e de negócio;
- Reuniões (calls) com o time, sempre com gravação e histórico centralizado;
- Planejamento semanal e roadmaps por área;
- Documentação interna e repositórios de conhecimento;
- Gestão de demandas e integrações automáticas com GitHub, AWS e Google Drive;
- Alertas de engenharia e notificações automáticas (deploys, falhas, métricas);
- Análises semanais com IA, enviadas automaticamente nos canais oficiais de cada área (Suporte, Engenharia,Produto, etc.), trazendo uma retrospectiva visual e interpretável dos principais indicadores.

Mas, ao instalar o aplicativo desktop Linux (o AppImage oficial), percebi um pequeno detalhe: o **dicionário de correção automática** vem apenas em inglês, e não há um menu visível para adicionar outros idiomas.  
Foi o início de uma pequena investigação técnica. Afinal, ele é um Electron rodando a aplicação web 😄.

## O problema: autocorreção em inglês

Se você escreve em português dentro do ClickUp, especialmente em *docs* ou comentários, já deve ter notado:  
> Tudo fica sublinhado em vermelho, inclusive palavras corretas (pra mim é depressivo isso haha).

Isso acontece porque o aplicativo desktop do ClickUp (assim como muitos *Electron apps*) usa o dicionário **do Chromium embutido**, e **não herda automaticamente o dicionário do sistema**.

Ou seja: mesmo que o seu sistema operacional esteja em português, o ClickUp ignora isso.

## A solução: adicionando dicionários manualmente

Depois de algumas horas de experimentos (e erros), chegamos à solução definitiva para o **Linux**, que também funciona com pequenas variações no **Windows** e **macOS**.

#### 🔧 Passo a passo (Linux)

1. **Localize a pasta de configuração do ClickUp:**

```bash
~/.config/ClickUp
```

2. **Crie (ou edite) o arquivo `Preferences`** e adicione a configuração de idioma:

```bash
vim ~/.config/ClickUp/Preferences
```

```json
{
   "migrated_user_scripts_toggle":true,
   "spellcheck":{
      "dictionaries":[
         "en-US",
         "pt-BR"
      ],
      "dictionary":""
   }
}
```

3. **Baixe o dicionário `pt-BR` para Chromium**  

No meu caso, só de instalar o pacote do idioma no OS, já funcionou perfeitamente.

4. **Reinicie o aplicativo.**

Agora o ClickUp reconhecerá automaticamente o novo idioma, e o corretor deixará de marcar todas as palavras em português como erro. E n omeu caso, mantenho o ClickUp em en-US, mas ele consegue validar idioma pt-BR na escrita também.

<img id="image-custom" src="/images/posts/clickup.png" alt="ClickUP Platform" />
<p id="image-legend">ClickUp rodando em en-US, validando pt-BR</p>

## Valores

Aqui, conseguimos diversos contatos no BR para intermediar as assinaturas, mas como não temos tantas assinaturas (30 no total), resolvemos fazer direto com eles. Pagando o pricing atualizado de assinatura mensal.

## Conclusão

Pequenos detalhes fazem grande diferença no dia a dia de times técnicos.  
Ao ativar o dicionário correto no ClickUp, eliminamos ruído visual, reduzimos erros em *docs* e ganhamos agilidade na comunicação escrita, especialmente em empresas com fluxo intenso de documentação, como a Harmo.

Essa configuração simples é um ótimo exemplo de como **ajustes técnicos aparentemente pequenos** refletem **em produtividade e clareza organizacional**.

E se você também vive no ecossistema Linux ou busca uma alternativa mais governável ao Slack/Discord, vale explorar o ClickUp com carinho, com dicionário em português e tudo 😄
