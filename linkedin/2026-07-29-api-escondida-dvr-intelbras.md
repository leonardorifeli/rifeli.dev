# A API HTTP escondida do meu DVR Intelbras

Três variações para o LinkedIn. Post no blog datado 2026-07-29. Link do blog no
primeiro comentário. Primeira linha sempre narrativa, nunca bloco de código.

Primeiro comentário (qualquer variação):

> Post completo: https://rifeli.dev/blog/2026-07-29-api-escondida-dvr-intelbras-mhdx-curl/

---

## Variação 1 — o diagnóstico errado (recomendada)

Fui ver por que uma das quatro câmeras de casa estava com a imagem estranha e quase desisti nos primeiros dois minutos. O ping não respondeu e o curl devolveu `http_code=000`. Conclusão óbvia: não alcanço o aparelho.

Errado nas duas leituras.

Ping sem resposta em DVR é comum, muito aparelho simplesmente não responde ICMP. E `000` não é código HTTP nenhum: é o curl avisando que não chegou a receber resposta. Pode ser timeout, conexão recusada, falta de rota, protocolo errado, qualquer coisa que aconteça antes do servidor responder. Como diagnóstico, `000` sozinho não vale nada. Ele só diz "não deu".

O que vale é pedir pro curl contar o motivo. Do 7.75 em diante dá pra imprimir o exit code e a mensagem de erro no mesmo `-w`:

:: exit 7 é conexão recusada ou sem rota
:: exit 28 é timeout
:: exit 6 é DNS

Aí o `000` deixa de ser beco sem saída e vira frase. No meu caso a resposta era mais simples do que o pânico sugeria: a interface web não estava na porta 80, o aparelho usa uma porta alta customizada.

A lição que eu sempre esqueço: separe "o host está vivo" de "o serviço está na porta que eu chutei". São perguntas diferentes, e o ping responde a errada.

Do outro lado dessa porta tinha uma API CGI inteira, e terminei a tarde com um script lendo e escrevendo a configuração das quatro câmeras pela linha de comando. No post conto o caminho completo, incluindo o que eu não consegui controlar por ela. Link no primeiro comentário.

#Homelab #curl #API #EngenhariaReversa #Linux

---

## Variação 2 — engenharia reversa educada

Meu DVR tem quatro câmeras e uma interface web daquelas: você ajusta um parâmetro, troca de canal, espera recarregar, repete. Com um punhado de coisas pra padronizar, isso é trabalho manual chato e propenso a erro.

A pergunta óbvia pra quem vive em terminal: dá pra fazer por API? Dá. E o caminho até lá é um bom exercício de engenharia reversa educada, do tipo ler antes de escrever.

O aparelho expõe uma interface CGI compatível com a família de APIs da Dahua. Faço a ressalva porque ela importa: eu não abri o firmware nem li strings de build pra saber de quem é o código. O que eu tenho é comportamento observado, e isso já é suficiente pra documentação de Dahua servir de mapa.

A ordem que eu segui, e recomendo:

:: Descobrir a autenticação antes de tentar qualquer coisa. O `401` trouxe um header revelador: Digest, não Basic. Muda a flag do curl e o resto todo.
:: Ler a configuração inteira antes de escrever uma linha. `configManager.cgi` cospe as tabelas, e é ali que você aprende os nomes reais em vez de chutar.
:: Tirar backup antes do primeiro `setConfig`. Não porque eu espero errar, mas porque a config atual é a única referência do que era o estado bom, e esse aparelho não tem desfazer.
:: Perguntar ao próprio aparelho o que ele suporta. `getCaps` respondeu o que nenhuma tentativa de adivinhar nome de tabela ia responder.

Saber o limite da ferramenta é tão valioso quanto saber o que ela faz. Duas leituras de API me pouparam de montar um `setConfig` que o aparelho ia ignorar em silêncio, e de subir numa escada pra caçar um menu que talvez não estivesse lá.

Passo a passo real no post, com o que funcionou e o que não. Link no primeiro comentário.

#Homelab #API #curl #Linux #Automacao

---

## Variação 3 — a parte de segurança

Digest é melhor que Basic porque a senha não viaja em claro: ele faz desafio-resposta com hash em cima do nonce. Isso autentica. Não cifra.

Essa distinção é a parte do meu domingo com DVR que eu mais quero que fique. A conexão continua sendo `http://`, então URL, endpoint, os parâmetros que eu escrevo e a config que volta na resposta ficam todos legíveis pra quem estiver na mesma rede olhando o tráfego. Por isso isso aqui é coisa de rede local controlada, de preferência num segmento isolado só pros bichos de câmera. E por isso DVR não fica publicado na internet.

Duas outras honestidades do mesmo tipo, que eu preferi escrever do que esconder:

:: A senha em arquivo com `umask 077` e permissão restrita resolve o histórico do shell. As aspas simples ali não são decoração: o arquivo é lido com `source`, ou seja é shell de verdade, e senha com espaço, `$` ou crase sem quoting vira expansão ou erro de sintaxe. Você descobre isso na forma de um 401 que não faz sentido.
:: Passar a credencial num array de argumentos do curl ajuda em organização e quoting, mas não esconde nada: no instante em que o curl roda, a senha está na linha de comando visível em `ps` e em `/proc`. Array nenhum conserta isso. Pra rede doméstica eu aceito a troca. Em máquina compartilhada eu não aceitaria.

Senha de DVR é credencial de sistema de segurança física da casa. Não vai pro histórico, não vai pro script versionado, e não vai num post público.

O passo a passo inteiro, com a parte que eu não consegui resolver, está no post. Link no primeiro comentário.

#Seguranca #Homelab #Linux #curl #DevSecOps

---

## Notas operacionais

- Recomendada: Variação 1. Abre com o erro de diagnóstico, que é a war story
  real do post e o tipo de coisa que gera comentário de quem já caiu nela. O
  `http_code=000` é reconhecível pra qualquer pessoa que usa curl.
- Variação 2 é a mais didática, boa pra audiência de engenharia e SRE. Ancora
  no método (ler antes de escrever) mais que no aparelho.
- Variação 3 puxa o ângulo de segurança e é a que mais rende discussão técnica.
  Também é a mais honesta sobre limitação, o que costuma performar bem.
- Cuidado com o enquadramento: o post NÃO afirma que o firmware é OEM da Dahua,
  afirma que a interface é compatível com a família de APIs da Dahua. Não
  reintroduzir a versão forte em nenhuma variação.
- Mesma coisa com exposição e anti-flicker: o post diz que não encontrou caminho
  suportado nos endpoints testados, não que o controle não existe. Manter.
- Todos os detalhes conferidos contra o post em 23/08/2026: MHDX 3004-C,
  firmware 4.001.00IB000, quatro câmeras analógicas, Digest, porta alta
  customizada, exit codes 7/28/6, configManager.cgi, getCaps.
- Primeira linha narrativa. Link no primeiro comentário. Hashtags no fim, 5.
  Sem emoji, sem travessão.
