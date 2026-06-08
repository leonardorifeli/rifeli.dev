---
title: "Slash commands no Claude Code: como construí o /save-session e por que ele virou ritual de fim de sessão"
draft: true
date: 2026-06-10T00:00:00.000Z
description: "Tutorial prático de slash command custom no Claude Code, com o caso real do /save-session. Por que precisei criar, como funciona o auto-memory que o Claude Code já dá de fábrica, o que o /save-session adiciona, e como compartilhar o skill entre múltiplas máquinas via dotfiles."
comments: true
keywords: [
  "Claude Code",
  "slash command",
  "save-session",
  "skill custom",
  "auto-memory",
  "dotfiles claude",
  "Anthropic",
  "ferramentaria de dev",
  "como criar slash command Claude Code",
  "como compartilhar skill Claude entre máquinas",
  "memória persistente Claude Code"
]
tags:
  - claude-code
  - ai
  - dev-tools
  - tutorial
  - anthropic
---

<img id="image-custom" src="" alt="" />
<p id="image-legend"></p>

# Introdução

Em 30 dias rodando dentro do Claude Code, atravessei 68 sessões. Em todas elas, no fechamento, o contexto morria. As decisões, as preferências reforçadas, os "não faz mais X assim" e os "esse padrão funcionou, repete depois" iam todos pro lixo. Na sessão seguinte, eu re-explicava. Sessenta e oito vezes.

Em um post anterior dessa série, sobre os [30 dias dentro do Claude Code](/blog/2026-05-29-30-dias-claude-code-usd-8k-plano-fixo/), deixei pendente a história do slash command que entrou pra resolver esse problema. Esse aqui é ele. Te conto a necessidade que me fez construir, como funciona, e te ensino a montar o seu próprio. No fim, falo de compartilhar entre máquinas, que foi a peça que destravou pra valer.

# A necessidade

O Claude Code já tem um sistema de memória persistente que roda no fundo. É o que a Anthropic chama de auto-memory: durante a conversa, o modelo pode decidir salvar fatos relevantes em arquivos no diretório `~/.claude/projects/<encoded-cwd>/memory/`. Esses arquivos viram contexto carregado em conversas futuras no mesmo projeto. É bom, é automático, e cobre o caso óbvio.

O problema é a passividade. O modelo só salva quando "decide" que algo é digno. Coisas que pra mim eram óbvias de carregar (uma decisão de arquitetura específica, uma preferência de escrita validada em três posts seguidos, o nome do nosso parceiro AWS que aparece em postmortems) ele às vezes salvava, às vezes não. E quando eu queria forçar, ficava digitando "salva isso na sua memória" no fim da sessão, sentindo como se estivesse instruindo um estagiário em três etapas.

A necessidade era simples: um comando que eu invocasse explicitamente no fim de qualquer sessão, com o entendimento de que naquele momento eu *quero* salvar, e o bar de "vale a pena guardar" pode ser mais baixo do que o automático. Esse é o `/save-session`.

# O que é um slash command no Claude Code

Antes de ir pro código, contexto pra quem nunca construiu. Slash commands no Claude Code são skills custom que você invoca digitando `/<nome>` na conversa. O Claude detecta o comando, carrega as instruções daquele skill, e executa o procedimento descrito. Skills vivem em duas hierarquias possíveis:

- `~/.claude/skills/<nome>/SKILL.md` — disponível em todas as conversas, em todas as pastas do seu sistema.
- `<projeto>/.claude/skills/<nome>/SKILL.md` — disponível só quando o Claude Code abre dentro daquele projeto.

Pra um comando utilitário como `/save-session`, que faz sentido em qualquer sessão, a hierarquia certa é a global em `~/.claude/skills/`.

A estrutura mínima de um SKILL.md é frontmatter YAML mais corpo em markdown. O frontmatter declara o comando, o que ele faz e como o usuário interage. O corpo é o procedimento: a instrução em linguagem natural que o Claude vai executar quando você invocar.

```markdown
---
name: meu-comando
description: O que ele faz, em uma frase
argument-hint: [opcional, ajuda de argumento que aparece no prompt]
disable-model-invocation: true
---

# meu-comando

Instruções em prosa do que o Claude deve fazer quando o usuário digitar /meu-comando.
```

O campo `disable-model-invocation: true` é importante: ele impede que o modelo invoque seu skill por conta própria sem o usuário ter digitado o comando. Pra um skill com efeito colateral (escrita de arquivo, leitura de memória, qualquer coisa que altera estado), isso é essencial.

# Anatomia do /save-session

O SKILL.md inteiro do `/save-session` tem cerca de 50 linhas. Vou mostrar o esqueleto e comentar as decisões.

```markdown
---
name: save-session
description: Extract durable, non-obvious learnings from the current conversation and persist them to the project memory system. Filters out code, ephemeral numbers, and anything derivable from the repo or git history. Use when the user wants to "save", "remember", or "salvar na memória" the current session, or just runs `/save-session`.
argument-hint: [optional scope hint, e.g. "só sobre Redis"]
disable-model-invocation: true
---

# save-session

Triggered explicitly by the user to capture what's worth carrying into future conversations.

## Procedure

1. Locate the memory directory at `~/.claude/projects/<encoded-cwd>/memory/`.
2. Read existing memories first. Update or remove before writing new ones.
3. Review the conversation for four memory types: user, feedback, project, reference.
4. Apply filters: do NOT save code patterns, file paths, ephemeral numbers.
5. Honour the scope hint if the user passed one.
6. Write the files with frontmatter (name, description, type) plus body.
7. Update MEMORY.md as an index (one line per memory, under 150 chars).
8. Report back: created, updated, skipped.
```

Três decisões valem comentar.

A primeira é o **description em inglês cobrindo aliases naturais em PT-BR**: "salvar na memória", "remember", "save the session". Quando o modelo é treinado nativamente em inglês mas a conversa pode estar em português, o description que abraça os dois ajuda na detecção do trigger.

A segunda é o **argument-hint**. Você pode passar `/save-session só sobre Redis` e o skill respeita esse escopo, filtrando o que extrai. Sem isso, fica tudo-ou-nada.

A terceira é a **disciplina de filtros explícitos no procedure**. O auto-memory também filtra, mas o `/save-session` adiciona pressão: "do NOT save code patterns, file paths, ephemeral numbers". O bar de relevância sobe, porque o usuário pediu — então o que entra precisa valer a pena ser carregado em todas as conversas futuras desse projeto.

# Como ele funciona em uma sessão real

Quando você digita `/save-session` no fim de uma conversa, o Claude faz quatro coisas em ordem:

Primeiro, descobre o diretório de memória do projeto atual (`~/.claude/projects/<encoded-cwd>/memory/`) e lê o `MEMORY.md` mais os arquivos de memória existentes. Isso é regra mandatória, porque a primeira coisa que o skill precisa garantir é que ele não vai duplicar nem reescrever memória já registrada.

Segundo, revisa a conversa em busca de candidatos divididos em quatro tipos: **user** (perfil, expertise, perspectiva), **feedback** (correções e validações com o `Why` e o `How to apply`), **project** (estado de trabalho com `Why` e `How to apply`), e **reference** (apontadores pra sistemas externos, URLs, hostnames).

Terceiro, aplica os filtros. Coisas que estão no código não viram memória, porque o código é a fonte da verdade. Datas relativas viram absolutas. Numerose financeiros voláteis (vão mudar em semanas) ficam de fora.

Quarto, escreve os arquivos novos, atualiza os existentes que precisam, e atualiza o índice `MEMORY.md`. No fim, reporta o que criou, o que mexeu, o que deixou de fora.

O efeito prático é que a próxima conversa que eu abrir nesse projeto vai carregar como contexto inicial todas as preferências, decisões e referências que valeram a pena. Sem precisar re-explicar. Sem precisar copiar e colar texto antigo. O modelo me trata como alguém que ele já conhece.

# Compartilhando o skill entre máquinas

Eu rodo Claude Code em duas máquinas ativas, desktop e notebook, conforme já contei no [post sobre 30 dias dentro do Claude Code](/blog/2026-05-29-30-dias-claude-code-usd-8k-plano-fixo/). Se eu criasse o skill só em uma delas, perderia metade do benefício.

A solução foi simples: o SKILL.md vive no meu repositório de **dotfiles** versionado, em `~/projects/personal/dotfiles/.claude/skills/save-session/SKILL.md`. Aí, em cada máquina, eu rodo um stow ou um script de symlink que conecta `~/.claude/skills/save-session` ao arquivo dentro de dotfiles.

Na prática, vira algo assim:

```bash
# uma vez por máquina, no setup
mkdir -p ~/.claude/skills
ln -s ~/projects/personal/dotfiles/.claude/skills/save-session ~/.claude/skills/save-session
```

Resultado: editar o skill em uma máquina, comitar no repo de dotfiles, dar pull na outra, e o `/save-session` está disponível com a mesma definição em todos os lugares. Mesma lógica vale pra outros skills que eu desenvolvi (scripts de stats, hooks de diagnóstico, custom commands de fluxo). Todos centralizados, todos versionados, todos sincronizados.

Esse é o passo que muita gente esquece: skill é código, e código você versiona. Se você está construindo um slash command que vai mexer com memória, com arquivos, com qualquer estado real, vale tratá-lo com a mesma seriedade que você trata qualquer parte da sua ferramentaria.

# Cinco aprendizados do uso

- **Bar de "vale salvar" deve ser explícito no skill, não implícito**. Auto-memory deixa o bar implícito no julgamento do modelo. Slash command explícito permite codificar regras de inclusão/exclusão. Use isso.
- **Memória boa é estruturada por tipo, não por ordem cronológica**. Separe user, feedback, project, reference. Quando você for buscar algo em três meses, vai querer encontrar por categoria, não por "quando aconteceu".
- **Índice (`MEMORY.md`) precisa ser índice**. Uma linha por memória, descrição curta. Não escreve conteúdo no índice. Conteúdo vai pros arquivos individuais. Senão você acaba com um único arquivo gigante que o modelo ignora por sobrecarga de contexto.
- **Salve o "Why", não só o "What"**. Uma feedback memory que diz "evitar emoji em posts" é fraca. Uma que diz "evitar emoji em posts porque o público é C-level sênior e emoji destrói credibilidade na primeira leitura" é forte. O `Why` permite julgamento em casos novos.
- **Versione o skill em dotfiles desde o dia um**. Antes mesmo de ele ficar bom. Você vai iterar, e cada iteração precisa estar visível em todas as máquinas. Skill que mora em uma máquina só é skill que vai morrer no próximo backup que você esquecer de fazer.

# Fechamento

O `/save-session` virou ritual de fechamento de cada sessão de trabalho importante. Antes de fechar o Claude Code, eu digito ele. Levam uns 20 a 40 segundos, e o que entra em memória ali volta na próxima sessão como contexto pronto, sem que eu precise pensar.

Construir slash commands custom no Claude Code é a fronteira que separa "uso a ferramenta" de "operacionalizo a ferramenta". Auto-memory te dá o caminho fácil. Skills custom te dão a alavanca: você codifica seu próprio processo dentro do agente, e ele passa a executar do seu jeito, com seus filtros, com seus padrões.

Se você usa Claude Code com regularidade e ainda não tem nenhum skill custom rodando, esse é o ponto natural pra começar. Não precisa ser save-session. Pode ser qualquer ritual repetitivo que você executa hoje à mão. Codifica ele em um SKILL.md, joga no dotfiles, symlinka pra `~/.claude/skills/`, e a partir da próxima sessão é só digitar `/`.
