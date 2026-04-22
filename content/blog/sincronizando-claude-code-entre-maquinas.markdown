---
title: "Sincronizando Claude Code entre máquinas: o que a Anthropic ainda não faz por você"
draft: false
date: 2026-04-22T00:00:00.000Z
description: "O Claude Code não tem sync nativo entre máquinas. Comparo três abordagens (git + symlinks, chezmoi e Syncthing), mostro o pega das memórias path-encoded e dou uma recomendação pragmática."
comments: true
keywords: [
  "Claude Code",
  "Anthropic",
  "dotfiles",
  "sync entre máquinas",
  "chezmoi",
  "syncthing",
  "git symlinks",
  "backup",
  "settings.json",
  "permissões",
  "memórias",
  "skills",
  "CLI",
  "produtividade",
  "como sincronizar claude code",
  "como fazer backup do claude code",
  "configuração claude code entre máquinas"
]
tags:
  - claude-code
  - anthropic
  - dotfiles
  - produtividade
  - cli
---

# Introdução

Você abre o Claude Code no desktop de trabalho pela primeira vez na semana e percebe que ele não lembra de nada: as skills customizadas que você criou, os slash commands que refinou, as memórias acumuladas sobre cada projeto. O CLI não tem sync nativo do diretório `~/.claude/`. Cada máquina é uma ilha.

# "Mas eu só preciso commitar o `.claude/` do projeto, né?"

Essa é a primeira reação de quem lê o título — e ela ignora o problema. Claude Code guarda config em **dois lugares diferentes**, e só um deles é resolvido versionando o `.claude/` dentro do repo:

**Por projeto (`<repo>/.claude/`)** — mora dentro de cada repositório. Tem o `settings.json` (compartilhável com o time) e o `settings.local.json` (permissões pessoais de tool use). Esse caso é fácil: basta versionar o que for compartilhado e adicionar `settings.local.json` ao `.git/info/exclude` local se você não quiser mesclar permissões com o time.

**Global do usuário (`~/.claude/`)** — mora no seu home, fora de qualquer repo. Inclui:

- Skills customizadas (`~/.claude/plugins/`)
- Slash commands customizados (`~/.claude/commands/`)
- Config global do CLI (`~/.claude/settings.json`)
- Memórias de contexto por projeto (`~/.claude/projects/<path-encoded>/memory/`)

Este artigo é sobre o segundo caso. Versionar o `.claude/` do repo não transfere nenhum dos itens acima, porque eles não vivem dentro do repo — vivem no seu `$HOME`. E é ali que mora o grosso do trabalho de configuração que você acumula ao longo de meses.

# Por que isso importa

Na Harmo adotamos o Claude Code como ferramenta default de AI para o time de engenharia, então essa dor de sync entre máquinas aparece no dia a dia e não é hipotética.

Quem usa Claude Code a sério acumula configuração global rapidamente: skills que você escreveu pra adequar o comportamento do agente ao seu stack, slash commands que automatizam fluxos repetidos, memórias construídas por semanas de conversa sobre cada projeto. Recriar isso manualmente numa segunda máquina custa horas e é o tipo de tarefa que ninguém faz — simplesmente se trabalha pior do outro lado.

O problema é agravado por um detalhe pouco documentado: memórias de projeto são indexadas pelo path absoluto do diretório. Se no laptop o projeto está em `/Users/rifeli/work/harmo` e no desktop em `/home/rifeli/projects/harmo`, as memórias não se transferem mesmo que você copie o diretório `~/.claude/` inteiro.

# Sync também é backup

Mesmo que você use uma máquina só, vale configurar uma das estratégias abaixo. SSD morre, sistema é reinstalado, `rm -rf` acontece na pasta errada. Perder o `~/.claude/` significa perder semanas de memória de contexto acumulada sobre cada projeto, todas as permissões ajustadas, skills customizadas que você foi refinando. É o tipo de estado que você nem lembra que construiu até ele sumir.

A diferença entre um backup que salva sua pele e um que não salva é o que você excluiu dele. Um backup completo de `~/.claude/` inclui `sessions/`, `cache/` e `history.jsonl` — conteúdo pesado, inútil para restauração e que vai fazer você desistir do backup porque leva tempo demais. Os mesmos ignores que você configura para sync servem para backup. Qualquer uma das três abordagens deste artigo te dá backup de graça como efeito colateral.

# O que é portável e o que não é

O `~/.claude/` tem conteúdo misturado. Separar o que faz sentido sincar evita dor de cabeça depois. A tabela abaixo está agrupada por escopo — note que só as duas primeiras linhas são o famoso "basta commitar no repo":

**Escopo por-projeto (dentro do repo):**

| Caminho                                  | Portável?                      | Por quê                                             |
| ---------------------------------------- | ------------------------------ | --------------------------------------------------- |
| `<repo>/.claude/settings.json`           | Sim, via git do próprio repo   | Config compartilhada com o time                     |
| `<repo>/.claude/settings.local.json`     | Sincar por repo                | Permissões pessoais, ignorar no git do time         |

**Escopo global (`~/.claude/`, fora de qualquer repo):**

| Caminho                                  | Portável?         | Por quê                                             |
| ---------------------------------------- | ----------------- | --------------------------------------------------- |
| `~/.claude/settings.json`                | Sincar            | Config global do CLI, estável entre máquinas        |
| `~/.claude/plugins/`                     | Sincar            | Skills customizadas                                 |
| `~/.claude/commands/`                    | Sincar            | Slash commands customizados                         |
| `~/.claude/projects/<path>/memory/`      | Sincar com cuidado| Path-encoded, ver seção dedicada                    |
| `~/.claude/cache/`                       | Nunca             | Dados locais pesados e efêmeros                     |
| `~/.claude/sessions/`                    | Nunca             | Estado de conversa ativa                            |
| `~/.claude/history.jsonl`                | Nunca             | Log local, não faz sentido mesclar                  |
| `~/.claude/shell-snapshots/`             | Nunca             | Snapshots de shell específicos da máquina           |
| `~/.claude.json` (credentials)           | Nunca             | Token expira, risco de vazamento                    |
| `~/.claude/statsig/`                     | Nunca             | Telemetria/feature flags locais                     |

A regra prática: sincar o que você configurou conscientemente, ignorar o que o CLI gerou para si próprio. E, importante, o problema deste artigo é o segundo grupo — o primeiro já é resolvido pelo fluxo normal de git do repo.

# Três abordagens

## 1. Git repo privado + symlinks

A solução mais simples e auditável. Funciona bem se você não precisa de sync em tempo real e gosta de controlar o que vai versionado.

```bash
# Na primeira máquina: criar o repo
mkdir -p ~/dotfiles/claude
cd ~/dotfiles

git init
cat > .gitignore <<'EOF'
claude/cache/
claude/sessions/
claude/history.jsonl
claude/shell-snapshots/
claude/statsig/
claude/.credentials.json
claude/todos/
EOF

# Mover os arquivos reais para o repo e deixar symlinks no lugar
mv ~/.claude/settings.json       ~/dotfiles/claude/settings.json
mv ~/.claude/plugins             ~/dotfiles/claude/plugins
mv ~/.claude/commands            ~/dotfiles/claude/commands 2>/dev/null || true

ln -s ~/dotfiles/claude/settings.json ~/.claude/settings.json
ln -s ~/dotfiles/claude/plugins       ~/.claude/plugins
ln -s ~/dotfiles/claude/commands      ~/.claude/commands

git add . && git commit -m "initial claude config"
git remote add origin git@github.com:seu-user/dotfiles.git
git push -u origin main
```

Na segunda máquina:

```bash
git clone git@github.com:seu-user/dotfiles.git ~/dotfiles

# Fazer backup de qualquer config existente antes de linkar
mv ~/.claude/settings.json ~/.claude/settings.json.bak 2>/dev/null

ln -s ~/dotfiles/claude/settings.json ~/.claude/settings.json
ln -s ~/dotfiles/claude/plugins       ~/.claude/plugins
ln -s ~/dotfiles/claude/commands      ~/.claude/commands
```

**Vantagens:** histórico completo, rollback trivial, code review antes de propagar mudanças.
**Desvantagem:** você precisa lembrar de `git pull` e `git push`. Não é automático.

Para o `settings.local.json` de cada repo, a abordagem é diferente — esse arquivo mora dentro do projeto e é gitignored por padrão. Se você confia no time, basta adicionar `.claude/settings.local.json` ao `.git/info/exclude` local e versionar `.claude/settings.json` (versão compartilhada) no repo principal.

## 2. chezmoi (ou yadm) com suporte a segredos

O `chezmoi` resolve dois problemas que o git puro não trata bem: templates por máquina (o path do home no macOS é `/Users/rifeli`, no Linux é `/home/rifeli`) e segredos encriptados.

```bash
# Instalar chezmoi
sh -c "$(curl -fsLS get.chezmoi.io)"

chezmoi init
chezmoi add ~/.claude/settings.json
chezmoi add ~/.claude/plugins
chezmoi add ~/.claude/commands

# Editar o arquivo de ignorar no source state
chezmoi edit-config
```

Adicione ao `~/.local/share/chezmoi/.chezmoiignore`:

```
.claude/cache
.claude/sessions
.claude/history.jsonl
.claude/shell-snapshots
.claude/statsig
.claude/.credentials.json
.claude/todos
```

Para config que varia entre máquinas, transforme o arquivo em template. Renomeie `dot_claude/settings.json` para `dot_claude/settings.json.tmpl` e use:

```json
{
  "model": "sonnet",
  "env": {
    "EDITOR": "{{ if eq .chezmoi.os \"darwin\" }}cursor{{ else }}code{{ end }}"
  }
}
```

Na segunda máquina:

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply seu-user
```

Se você tem chaves que precisam viajar junto (API keys de outras ferramentas referenciadas no settings), integre com `age` ou `gpg`:

```bash
chezmoi add --encrypt ~/.claude/some-secret-config
```

**Vantagens:** template-aware, integração nativa com secret managers, um comando para aplicar tudo.
**Desvantagem:** curva de aprendizado maior que git puro; se você nunca usou, é uma ferramenta nova para dominar só para isso.

## 3. Syncthing / Dropbox / iCloud com symlinks seletivos

Sync em tempo real, sem `git commit`. A diferença crítica em relação aos outros: se você não configurar os ignores corretamente, vai sincar cache, sessões ativas, e eventualmente corromper arquivos com escritas concorrentes.

Usando Syncthing como exemplo (mais seguro que Dropbox para arquivos ativamente escritos porque tem versioning e resolução de conflito explícita):

```bash
# Criar diretório de sync
mkdir -p ~/Sync/claude-config

# Mover apenas os arquivos seguros
mv ~/.claude/settings.json ~/Sync/claude-config/
mv ~/.claude/plugins       ~/Sync/claude-config/
mv ~/.claude/commands      ~/Sync/claude-config/ 2>/dev/null

ln -s ~/Sync/claude-config/settings.json ~/.claude/settings.json
ln -s ~/Sync/claude-config/plugins       ~/.claude/plugins
ln -s ~/Sync/claude-config/commands      ~/.claude/commands
```

No Syncthing, adicione `~/Sync/claude-config` como pasta compartilhada entre as máquinas. **Não sincronize o `~/.claude/` inteiro** — é tentador e vai te morder.

Com Dropbox ou iCloud o princípio é o mesmo, mas evite ativamente:

- **Sincar `sessions/` ou `history.jsonl`**: o CLI escreve neles durante uso e sync em tempo real gera conflitos.
- **Sincar `cache/`**: pode ficar pesado e gerar upload infinito.
- **Confiar na resolução automática de conflitos**: Dropbox cria arquivo `(conflicted copy).json` silenciosamente, e o Claude Code não sabe o que fazer com isso.

**Vantagens:** zero ação manual após setup.
**Desvantagens:** sem histórico acionável, risco alto se a lista de ignore estiver errada, e se as duas máquinas estiverem online simultaneamente e você editar de um lado, o outro lado pode ver estado inconsistente.

# O pega da memória path-encoded

Memórias vivem em `~/.claude/projects/<path-encoded>/memory/`, onde `<path-encoded>` é o path absoluto do projeto com separadores trocados por hífens. Um projeto em `/Users/rifeli/work/harmo` vira `-Users-rifeli-work-harmo`. Em `/home/rifeli/projects/harmo` vira `-home-rifeli-projects-harmo`. Mesmo repo, duas chaves diferentes, memórias órfãs.

Duas soluções, escolha uma:

**Opção A: padronizar o path em todas as máquinas.** A mais limpa. Adote `~/projects/<repo>` como convenção e crie symlinks se o path real for diferente:

```bash
# No desktop, se o repo real está em /mnt/data/work/harmo
mkdir -p ~/projects
ln -s /mnt/data/work/harmo ~/projects/harmo

# Sempre abrir o Claude Code via ~/projects/harmo
cd ~/projects/harmo && claude
```

**Opção B: script de renomeio pós-sync.** Útil quando padronizar não é viável (diferenças de SO, ou times onde cada dev tem layout próprio). Depois de puxar as memórias, renomeie os diretórios:

```bash
#!/bin/bash
# remap-memory.sh — rodar após sync para remapear path-encoded dirs

SOURCE_MACHINE_PATH="-Users-rifeli-work-harmo"
TARGET_MACHINE_PATH="-home-rifeli-projects-harmo"

cd ~/.claude/projects

if [ -d "$SOURCE_MACHINE_PATH" ] && [ ! -d "$TARGET_MACHINE_PATH" ]; then
  cp -r "$SOURCE_MACHINE_PATH" "$TARGET_MACHINE_PATH"
  echo "Remapped $SOURCE_MACHINE_PATH -> $TARGET_MACHINE_PATH"
fi
```

Dá pra integrar isso como hook do chezmoi (`run_after_remap-memory.sh.tmpl`) ou como `post-merge` hook do git no repo de dotfiles.

# Decisão rápida

- Se você quer o mínimo de ferramentas novas e confia em `git pull`: **git + symlinks**.
- Se você sincroniza mais do que só Claude Code (zshrc, nvim, etc) e quer templates por SO: **chezmoi**.
- Se você odeia comandar sync manualmente e topa o risco: **Syncthing com ignores rigorosos**. Não Dropbox, não iCloud, por causa do comportamento de conflito.
- Se você trabalha em dois SOs diferentes (mac + linux): **chezmoi**, pelo suporte a template.
- Se você precisa versionar segredos junto da config: **chezmoi + age**.

# Limitações honestas

Nada disso resolve:

- **Token de auth.** `~/.claude/.credentials.json` expira e não vale o risco de espalhar entre máquinas. Faça login em cada uma separadamente.
- **Sessões ativas.** Se você está no meio de uma conversa no laptop e abre a mesma no desktop, elas não se encontram. Sessão é local.
- **Cache e downloads de modelo.** Claude Code usa a API; não há modelo local para sincar. Mas se você tem ferramentas que cacheiam respostas, essas caches são por máquina.
- **Estado de permissões no meio de uma run.** Se você aprovou "sempre permitir" para uma tool no laptop durante uma sessão e sincou, pode ser que na outra máquina a aprovação só apareça na próxima reinicialização do CLI.

# Comparação final

| Critério                      | Git + symlinks | chezmoi                        | Syncthing              |
| ----------------------------- | -------------- | ------------------------------ | ---------------------- |
| Facilidade de setup           | Alta           | Média                          | Média                  |
| Segurança de segredos         | Nenhuma nativa | age/gpg integrados             | Criptografia de trânsito |
| Histórico / rollback          | Completo       | Via git (chezmoi usa git)      | Versioning limitado    |
| Sync em tempo real            | Não            | Não                            | Sim                    |
| Suporte a templates           | Não            | Sim                            | Não                    |
| Risco de corromper estado     | Baixo          | Baixo                          | Médio-alto             |
| Curva de aprendizado          | Baixa          | Média                          | Baixa                  |

# Conclusão

A recomendação pragmática para a maioria: **git + symlinks para config estável**, e **padronizar os paths dos projetos** para resolver a questão das memórias. Passa para chezmoi só quando a dor do manual vira maior que a dor de aprender a ferramenta.

**💬 E você, como tem sincronizado sua configuração do Claude Code?**

Usa dotfiles, sync em nuvem, ou simplesmente aceita a duplicação e reconfigura do zero? Conta nos comentários como você lida com isso no dia a dia.
