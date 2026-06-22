# Slash commands no Claude Code: como construí o /save-session

Três variações para o LinkedIn. Post no blog datado 2026-06-17, publicação no LinkedIn em 2026-06-18 de manhã. Link do blog no primeiro comentário.

Primeiro comentário (qualquer variação):

> Post completo: https://rifeli.dev/blog/2026-06-17-slash-command-save-session-claude-code/

---

## Variação 1 — war story / dor primeiro (recomendada)

180 sessões dentro do Claude Code em pouco mais de um mês, em duas máquinas. E em todas elas, no fechamento, o contexto morria.

As decisões de arquitetura, as preferências de escrita que eu tinha validado, os "não faz mais X assim". Tudo ia pro lixo quando eu fechava a sessão. Na seguinte, eu re-explicava do zero.

O Claude Code já tem auto-memory: ele salva fatos sozinho, quando "decide" que vale. O problema é exatamente esse "decide". Às vezes salvava, às vezes não. E quando eu queria forçar, ficava digitando "salva isso na memória" como quem instrui estagiário.

Então construí um slash command: /save-session. Eu invoco no fim da sessão, ele extrai o que vale carregar pra frente, filtra o que é código (que já é fonte da verdade) e grava na memória do projeto. Próxima sessão abre já me conhecendo.

A peça que destravou de verdade não foi o comando. Foi versionar ele no dotfiles e symlinkar nas duas máquinas. Skill é código. Código você versiona.

Escrevi o passo a passo completo, com o SKILL.md inteiro, no blog. Link no primeiro comentário.

#ClaudeCode #AI #DevTools #Anthropic #Produtividade

---

## Variação 2 — insight contrário / "automático não basta"

Toda ferramenta de IA hoje promete memória automática. Usei a do Claude Code por 180 sessões e aprendi que automático tem um furo: a passividade.

O modelo só salva o que ele julga digno. O problema é que o julgamento dele não é o meu. Uma preferência de escrita que eu validei em três posts seguidos? Às vezes entrava, às vezes não. E eu não tinha controle sobre o bar de "isso vale guardar".

A solução não foi brigar com o automático. Foi adicionar um modo explícito por cima dele. Construí o /save-session: um comando que eu disparo quando EU decido que aquela sessão tem algo que precisa sobreviver. O bar de relevância passa a ser meu, codificado no skill, não implícito no modelo.

A diferença entre "uso a ferramenta" e "operacionalizo a ferramenta" mora exatamente aí: no dia que você para de aceitar o comportamento padrão e codifica o seu.

Tutorial completo com o código no blog. Link nos comentários.

#ClaudeCode #AI #DevTools #Anthropic

---

## Variação 3 — builder / direto ao "como"

Se você usa Claude Code com regularidade e ainda não tem nenhum slash command custom rodando, esse post é o seu empurrão.

Construí um chamado /save-session. No fim de qualquer conversa eu digito o comando e ele faz quatro coisas: lê a memória que já existe pra não duplicar, varre a sessão atrás do que vale carregar, filtra fora código e números voláteis, e grava estruturado por tipo (decisão, preferência, referência). Leva 20 a 40 segundos e a próxima sessão abre com tudo isso já em contexto.

O SKILL.md inteiro tem 50 linhas. Frontmatter declarando o comando, corpo em prosa com o procedimento. É menos código do que parece.

O detalhe que quase todo mundo esquece: skill é código, então mora no meu repositório de dotfiles versionado e vai symlinkado pras duas máquinas que uso. Edito numa, dou pull na outra, e o comando é idêntico em todo lugar.

Passo a passo pra montar o seu no blog. Link no primeiro comentário.

#ClaudeCode #AI #DevTools #Anthropic #Dotfiles

---

## Notas operacionais

- Recomendada: Variação 1. Número absoluto cedo (180), war story concreta, fecha na lição forte ("skill é código").
- Variação 2 puxa pelo ângulo contrário (automático não basta). Boa pra audiência sênior que já usa IA.
- Variação 3 é a mais tutorial. Boa pra quem ainda não construiu skill custom.
- Primeira linha é hook narrativo, nunca bloco de código.
- Link no primeiro comentário. Hashtags no final, 4 a 5.
- Sem emoji. Sem hífen como travessão.
