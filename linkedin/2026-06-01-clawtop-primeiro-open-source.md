# clawtop: meu primeiro projeto open source

Três variações para o LinkedIn. Post no blog datado 2026-06-01. Link do blog no
primeiro comentário. Primeira linha sempre narrativa, nunca bloco de código.

Primeiro comentário (qualquer variação):

> Post completo: https://rifeli.dev/blog/2026-06-01-clawtop-meu-primeiro-open-source/
> Repositório: https://github.com/leonardorifeli/clawtop

---

## Variação 1 — a pergunta que travou três dias (recomendada)

Mostrei uma ferramenta que eu tinha acabado de construir pra um amigo. Ele olhou cinco segundos e disparou: "era só dar `/usage` e boa, não?".

Esse comentário me travou três dias. Não porque ele estivesse errado, mas porque estava parcialmente certo, e eu precisava saber em que parte exatamente ele não estava antes de continuar escrevendo código.

Fui investigar o que já existia. Tem bastante coisa boa, e nenhuma resolvia o meu problema, que só aparece quando você usa Claude em mais de uma máquina. Eu uso em três: workstation, laptop de trabalho e o home-server. Quando eu rodava `/usage` numa delas, via só o que aquela máquina sabia. O total da minha conta estava esparramado em três lugares.

A sacada que tornou o projeto não redundante foi perceber uma assimetria: o rate limit da Anthropic é por conta, o breakdown por projeto e por modelo é por máquina. Os três daemons veem o mesmo percentual de utilização, mas cada um sabe só do que rodou ali.

O valor não está em coletar. Está no merge. O dashboard pega o rate limit mais fresco, soma os tokens por projeto e por modelo, e preserva a atribuição por host: `rifeli.dev 874k` no total, com uma sub-linha discreta dizendo `omen 800k · notebook 74k`. Pra quem roda numa máquina só, o merge de um elemento é identidade e tudo funciona igual. Pra quem roda em três, é a diferença entre ter três relatórios separados e ter resposta pra "onde foi minha cota essa semana, e em qual máquina".

Esse é o clawtop, meu primeiro projeto open source de verdade. A investigação inteira, incluindo o que ficou de fora e por quê, está no post. Link no primeiro comentário.

#OpenSource #Golang #DevTools #TUI #ClaudeCode

---

## Variação 2 — a decisão de arquitetura que veio da segurança

O OAuth do Claude vive num arquivo local, `~/.claude/.credentials.json`. Esse arquivo é o portão da conta: se vaza, o atacante usa a tua subscription até o token expirar.

Toda ferramenta que eu olhei assume que quem lê esse arquivo e quem renderiza o dashboard rodam no mesmo lugar. Pra quem trabalha no laptop e olha o dashboard nesse mesmo laptop, isso não importa. Pra quem quer ver num servidor, importa muito: o meu tem tunnel aberto, mais superfície de ataque, mais gente com SSH eventual. Não me deu vontade de copiar o credencial pra lá.

Foi essa restrição que definiu a arquitetura, e não o contrário. O sistema virou duas peças:

:: `clawtopd`, o daemon, roda em cada máquina onde o credencial existe. Ele nunca sai de lá.
:: `clawtop`, o TUI, roda no servidor de visualização e nunca vê credencial nenhum.

A comunicação entre as duas é a parte de que eu mais gosto, porque é a mais chata: o daemon empurra um JSON pequeno via SSH, com escrita atômica em `tmp` e `mv` no final. Sem porta exposta, sem endpoint custom, sem autenticação pra eu errar. A pergunta que eu me fiz foi qual é a menor superfície que resolve, e SSH que eu já tenho configurado ganhou de qualquer coisa que eu fosse inventar.

Restrição de segurança tratada como requisito no começo costuma dar arquitetura mais simples do que a mesma restrição tratada como problema no fim.

Como cada peça funciona e os tradeoffs que eu assumi estão no post. Link no primeiro comentário.

#Seguranca #Arquitetura #OpenSource #Golang #DevTools

---

## Variação 3 — publicar mesmo tendo alternativa

Já existe ferramenta pra acompanhar consumo de subscription do Claude. Publiquei a minha mesmo assim, e acho que essa é a parte que vale conversar.

O caminho foi esse. Esbarrei num projeto charmoso que mostra o consumo num display AMOLED de duas polegadas com sprites pixel-art, controlado por ESP32. Quis fazer, não tinha ESP32 sobrando, e o que eu tinha era um home-server com mais ciclos ociosos do que eu uso. A primeira versão nasceu só pra trocar o hardware por um TUI.

Aí veio a pergunta do amigo, "era só dar `/usage`?", e eu parei três dias pra investigar o que já existe. Descobri que o display nunca era o problema interessante. O problema interessante era o que ele mostrava, e em quantas máquinas ele conseguia ver.

Duas coisas que eu levo dessa história:

:: Comparar com o que existe antes de continuar não mata o projeto, define ele. Foi o levantamento das alternativas que me mostrou onde eu tinha algo diferente pra oferecer, e onde eu estava só reimplementando.
:: "Já existe" e "resolve o meu caso" são perguntas separadas. A segunda é a que decide se vale publicar.

O clawtop é meu primeiro open source de verdade, e ele existe porque eu respondi a segunda pergunta com honestidade em vez de desistir na primeira.

A investigação completa, com o comparativo honesto contra as alternativas, está no post. Link no primeiro comentário.

#OpenSource #DevTools #Golang #Engenharia #ClaudeCode

---

## Notas operacionais

- Recomendada: Variação 1. Abre com a fala do amigo, que é diálogo real e
  primeira linha narrativa forte, e chega no insight técnico (rate limit por
  conta, breakdown por máquina) sem enrolar. Fecha no valor concreto do merge
  com atribuição por host.
- Variação 2 é a de arquitetura e segurança. Boa pra audiência sênior. O ângulo
  "a restrição definiu o desenho" é o mais reaproveitável.
- Variação 3 é a mais pessoal e a que puxa mais comentário, porque toca numa
  dúvida comum: vale publicar tendo alternativa. Boa se o objetivo for
  conversa, não alcance.
- Duas menções que valem manter, porque dão crédito: o projeto que inspirou
  (Clawdmeter, ESP32 com display AMOLED) na Variação 3, e o repositório no
  primeiro comentário junto do link do post.
- O post é sobre projeto pessoal e ferramenta de terceiro. Não misturar com
  números ou posicionamento da Harmo.
- Detalhes conferidos contra o post em 23/08/2026: três máquinas, daemon
  clawtopd por máquina, TUI no servidor, JSON via SSH com escrita atômica,
  rate limit por conta, breakdown por máquina, exemplo rifeli.dev 874k com
  omen 800k e notebook 74k.
- Primeira linha narrativa. Link no primeiro comentário. Hashtags no fim, 5.
  Sem emoji, sem travessão.
