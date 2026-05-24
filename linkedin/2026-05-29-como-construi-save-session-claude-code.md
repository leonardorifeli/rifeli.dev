# Como construí o /save-session no Claude Code: skill + hook diagnóstico

Três variações para o LinkedIn. Mesmo título do post no blog. Link do blog no primeiro comentário.

---

## Variação 1 — decisão honesta / hook diagnóstico

Antes de escrever o hook real do meu /save-session, escrevi um hook DIAGNÓSTICO.

Função única: rodar no SessionEnd e dumpar tudo que o harness do Claude Code expõe (env vars, args, stdin, cwd) em um log. Não chamava Claude. Não fazia nada produtivo. Só revelava o que estava disponível para o hook real depois.

Por que? Porque adivinhar o que um hook recebe é como adivinhar schema de API. Você fica preso a bugs que só aparecem em produção. Trinta linhas de bash me pouparam uma sessão inteira de retrabalho.

Tutorial completo do skill, do hook diagnóstico e da decisão por essa ordem no rifeli.dev.

Link no primeiro comentário.

#ClaudeCode #DevTools #Engineering #Hooks

---

## Variação 2 — construção / dois componentes

Construí um slash command no Claude Code que destila o que aprendi em uma sessão antes de fechar.

Dois componentes.

Skill define o procedure: localizar memória, ler MEMORY.md antes de escrever qualquer coisa, aplicar filtros (sem código, sem números efêmeros, sem nada derivável do git), salvar arquivos novos, atualizar o índice.

Hook dispara o skill no SessionEnd. Mas comecei pelo hook diagnóstico, não pelo real. Antes de codificar o que o hook faz, descobri o que o harness expõe para ele. Inversão simples que evita retrabalho.

Memória entre sessões é o gap mais subestimado de ferramentas de IA agentic. Sem ela, cada conversa começa do zero, e o investimento de contexto evapora.

Tutorial no rifeli.dev. Link no primeiro comentário.

#ClaudeCode #AI #DevTools #Memory

---

## Variação 3 — produtividade / multi-projeto

Opero 13 projetos no Claude Code, entre Harmo e pessoais.

Cada um com seu próprio histórico de decisões, gotchas de infra, padrões de código, war stories. Lembrar tudo é impossível. Documentar tudo é caro.

Construí um /save-session que extrai só o que vale carregar para a próxima conversa: aprendizados não óbvios, preferências validadas, coordenadas estáveis de infraestrutura. Ignora código, números efêmeros e qualquer coisa que o git já guarda.

Implementação tem skill (procedure puro, sem mágica) e hook (ainda em modo diagnóstico, explico no post por que essa ordem importa).

Tutorial completo no rifeli.dev. Link no primeiro comentário.

#ClaudeCode #AI #DevTools #Productivity #CTO

---

## Notas operacionais

- Recomendo Variação 1 para LinkedIn primário: ângulo de decisão técnica honesta, abre conversa com quem constrói ferramentaria.
- Variação 2 é a mais "tutorial". Boa para audiência sênior técnica.
- Variação 3 puxa pelo lado de produtividade e multi-projeto. Boa para gestor técnico ou outro CTO.
- Link no primeiro comentário. Hashtags no final, 4 a 5.
- Sem emoji. Sem hífen como travessão.
- Esse post depende de você me passar a war story do gatilho real (o que te fez construir isso?) antes da versão final do blog.
