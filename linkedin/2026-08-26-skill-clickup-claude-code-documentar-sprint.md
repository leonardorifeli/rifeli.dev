# Ensinei o Claude Code a documentar minha sprint no ClickUp

Três variações para o LinkedIn. Post no blog datado 2026-08-26. Link do blog no
primeiro comentário. Primeira linha sempre narrativa, nunca bloco de código.

Primeiro comentário (qualquer variação):

> Post completo: https://rifeli.dev/blog/2026-08-26-skill-clickup-claude-code-documentar-sprint/

---

## Variação 1 — o loop que fecha sozinho (recomendada)

No fim de uma sessão de trabalho, a ferramenta que eu tinha acabado de construir abriu a última task do board sozinha. Não porque eu mandei criar aquela task. Porque a conversa chegou numa decisão, e ela registrou.

Foi o fecho de uma tarde que saiu assim: 15 tasks pontuadas, 11 subtasks reestimadas e dois pull requests, sem eu abrir o ClickUp uma única vez.

O que me interessa aqui não é a produtividade. É o que aparece no caminho quando você dá a uma ferramenta o poder de escrever num sistema que o time inteiro usa.

Trabalho de infraestrutura quase sempre acontece antes da burocracia. Você investiga um custo, mexe num cluster, prepara um upgrade, e só depois lembra que aquilo precisava virar registro. O registro fica pra trás, a sprint não reflete o que foi feito, o esforço some. Abrir task no meio do trabalho dá preguiça porque dá trabalho de verdade: título, escopo, pontos, épico, sprint certa, atribuição. Multiplica por quinze e ninguém faz.

A virada foi parar de tratar documentação como segunda jornada e passar a tratar como subproduto. Eu converso enquanto faço o trabalho de verdade, e no fim peço pra documentar.

E aí começa a parte de engenharia. Descobri que o ClickUp tem dois campos de ponto, o custom field do board e o Sprint Points nativo, que são independentes e alimentam coisas diferentes. Preencher só um deixa o relatório de velocity mentindo pra você, e você só descobre isso uma semana depois olhando um gráfico que não bate.

No post conto as três decisões que sobraram dessa construção, incluindo a que quase me passou a perna. Link no primeiro comentário.

#ClaudeCode #IA #Produtividade #EngenhariaDeSoftware #ClickUp

---

## Variação 2 — o default que não cheirava bem

Eu tinha um bloco de subtasks pra pontuar e o campo de pontos já vinha preenchido. Todas com 8.

Parei antes de mandar seguir em frente. Oito é o teto da escala do nosso board, que vai de 1 a 8. Ou seja: não era estimativa, era o máximo carimbado em tudo, o padrão clássico de quem aplicou um valor em lote e seguiu a vida.

Se eu tivesse pedido pro modelo "só copiar o que já está lá", ele teria propagado aquilo com a maior cara de competência. Nenhum erro de execução, nenhum aviso, nenhum número fora da faixa. Só um dado ruim replicado com confiança.

Em vez disso pedi pra reestimar feature a feature. Saíram pontos variados, e a soma ficou bem abaixo do bloco de oito em tudo.

A lição não é sobre ClickUp nem sobre IA. É que ferramenta nenhuma substitui o seu julgamento sobre o tamanho das coisas. Ela acelera o registro, não a decisão. E ela é especialmente perigosa justamente quando o dado errado já está no sistema, porque aí ela não está inventando nada: está sendo fiel a uma bobagem que alguém escreveu antes.

Isso vale muito além de story point. Todo default que ninguém revisou vira verdade no momento em que uma automação começa a copiar ele.

Escrevi a história inteira, de como isso virou uma skill do Claude Code que fala com a API do ClickUp até o limite que eu mantive no controle humano. Link no primeiro comentário.

#IA #Engenharia #Agile #Estimativas #ClaudeCode

---

## Variação 3 — quem aperta o botão final

Quando uma IA só lê e responde, um erro dela é um parágrafo errado. Quando ela escreve num sistema que o time usa, um erro vira ruído no board, número torto na velocity e decisão tomada em cima de dado falso.

Essa mudança de natureza é o que me fez desenhar a ferramenta de um jeito específico, e eu recomendo os três cuidados pra qualquer automação que toque o mundo externo:

:: Segredo nunca no código. O token vive em variável de ambiente, com fallback pro secrets manager na hora da chamada. Quando o próprio modelo sugeriu salvar o token num arquivo pra facilitar, eu recusei. Credencial em texto puro versionada é dívida que volta pra te morder, e construir ferramenta nova não é desculpa pra repetir o erro que a gente passa a vida pedindo pros outros não cometerem.

:: Nada definitivo sem revisão humana. Ela monta a lista de tasks com título, escopo, pontos e épico, e me apresenta antes de subir. Eu aprovo ou ajusto. A diferença entre uma ferramenta que te ajuda e uma que te assombra é quem aperta o botão final.

:: Procedência marcada. Toda task que ela abre sai com um PS dizendo que foi aberta automaticamente. Quem abrir o board daqui a seis meses não precisa adivinhar de onde veio aquele registro.

O ganho de velocidade é real e mensurável. Mas ele só é seguro com essas três coisas no lugar, e nenhuma delas custa caro de implementar. O que custa caro é descobrir que faltavam.

Conto a construção inteira no post, com as decisões técnicas que apareceram no caminho. Link no primeiro comentário.

#IA #DevSecOps #Governanca #Automacao #EngenhariaDeSoftware

---

## Notas operacionais

- Publicar só depois que o post estiver no ar. Na data desta escrita o arquivo
  está com `draft: false` mas o commit não foi feito, e o deploy é CI no push.
- Recomendada: Variação 1. Abre com a imagem forte do loop fechando sozinho,
  entrega o número absoluto cedo (15 tasks, 11 subtasks, dois PRs) e guarda a
  parte técnica pro post. É a que mais convida a clicar.
- Variação 2 é a de maior potencial de comentário. Estimativa é assunto que
  todo mundo tem opinião, e o gancho do "teto da escala carimbado em tudo" é
  reconhecível pra qualquer pessoa que já olhou board alheio.
- Variação 3 é a de audiência mais sênior, CTO e head de engenharia. É também a
  que melhor sustenta discussão sobre governança de agente com acesso de
  escrita, tema que está quente.
- NÃO citar em nenhuma variação os nomes reais das subtasks que aparecem no
  post, porque isso é roadmap interno e ainda está pendente de decisão do autor
  no próprio artigo. Aqui elas já saíram, manter assim.
- Não citar IDs de field, de lista, de time, nem o endpoint interno. O post
  público usa placeholders e o LinkedIn não precisa nem disso.
- Primeira linha narrativa. Link no primeiro comentário. Hashtags no fim, 5.
  Sem emoji, sem travessão.
