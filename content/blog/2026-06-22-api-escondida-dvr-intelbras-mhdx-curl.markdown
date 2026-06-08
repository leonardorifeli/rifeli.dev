---
title: "A API HTTP escondida do meu DVR Intelbras: ajustando 4 câmeras pela linha de comando"
draft: true
date: 2026-06-22T00:00:00.000Z
description: "Meu DVR Intelbras MHDX 3004-C expõe uma API CGI no estilo Dahua que ninguém documenta direito. Em vez de clicar canal por canal numa interface web pesada, li e ajustei a configuração das câmeras com curl e autenticação Digest. Conto o passo a passo real: como achei a porta, como autentiquei, como li as tabelas de config antes de escrever qualquer coisa, o que dá pra controlar (encoder, cor, redução de ruído) e o que NÃO dá (exposição e anti-flicker), e como mantive a senha fora do histórico."
comments: true
keywords: [
  "Intelbras MHDX",
  "API Dahua",
  "configManager.cgi",
  "DVR API curl",
  "HDCVI",
  "autenticacao digest curl",
  "Intelbras 3004-C",
  "como configurar dvr por api",
  "VideoColor Dahua",
  "Encode Dahua API",
  "VideoInDenoise",
  "anti-flicker camera"
]
tags:
  - intelbras
  - dahua
  - dvr
  - api
  - curl
  - homelab
  - engenharia-reversa
---

<img id="image-custom" src="/images/posts/7c4e6bdc-21e4-4dde-8a66-73a75ee47222.png" alt="" />
<p id="image-legend"></p>

# Introdução

Comecei a tarde de domingo querendo só arrumar uma câmera que estava com a imagem estranha e terminei com um script que lê e escreve a configuração das quatro câmeras do meu DVR direto pela linha de comando. No caminho descobri que o Intelbras MHDX 3004-C, como boa parte da linha, roda firmware OEM da Dahua e expõe uma API HTTP CGI que quase ninguém documenta em português.

A interface web do aparelho é aquela coisa pesada, cheia de combobox, em que você ajusta um parâmetro, troca de canal, espera recarregar, repete. Com quatro câmeras e um punhado de parâmetros pra padronizar, isso é trabalho manual chato e propenso a erro. A pergunta óbvia pra quem vive em terminal: dá pra fazer isso por API? Dá. E o caminho até lá é um bom exercício de engenharia reversa educada, do tipo ler antes de escrever.

Este post documenta o que funcionou de verdade no meu aparelho. Firmware `4.001.00IB000`, build de agosto de 2024. Em outras versões os nomes de tabela podem mudar, e é exatamente por isso que a primeira metade do trabalho é descobrir, não chutar.

# Achando a porta

Primeiro fato: o DVR estava na mesma rede que a máquina de onde eu trabalho. Peguei o IP local dele na própria tela de rede do aparelho (ele estava em DHCP, o que por si só já é um problema que comento no final). O teste inicial de alcance foi direto:

```bash
ping -c2 "$DVR_IP"
curl -s -o /dev/null -w "%{http_code}\n" "http://$DVR_IP"
```

Ping zerado e `http_code=000`. Quase desisti achando que não alcançava. Mas ping zerado em DVR é comum, muito aparelho bloqueia ICMP, e o `000` só dizia que a porta 80 não respondia. A interface web não estava na 80: o aparelho usava uma porta HTTP customizada, alta. Com a porta certa:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "http://$DVR_IP:$PORT"
# 200
```

Lição que sempre esqueço: separe "o host está vivo" de "o serviço está na porta que eu chutei". São perguntas diferentes e o ping responde a errada.

# A autenticação é Digest, não Basic

Com a web respondendo, fui bater na API CGI. O padrão Dahua expõe tudo em `/cgi-bin/`. O primeiro probe é pedir o tipo do aparelho:

```bash
curl -s -i "http://$DVR_IP:$PORT/cgi-bin/magicBox.cgi?action=getDeviceType"
```

A resposta foi um `401 Unauthorized` com um header revelador:

```
WWW-Authenticate: Digest realm="Login to ...", qop="auth", nonce="...", opaque=""
```

`Digest`, não `Basic`. Isso muda o `curl`: tem que usar `--digest`, senão a credencial nem é negociada direito. O `curl` faz o desafio-resposta de Digest sozinho, então na prática é só trocar a flag:

```bash
curl -s --digest -u "$USER:$PASS" \
  "http://$DVR_IP:$PORT/cgi-bin/magicBox.cgi?action=getDeviceType"
# type=MHDX 3004-C
```

Funcionou. A partir daqui é tudo `configManager.cgi`.

# Mantendo a senha fora do histórico

Antes de seguir, um parêntese que pra mim não é negociável. Senha de DVR é credencial de sistema de segurança física da minha casa. Ela não vai pro histórico do shell, não vai pro corpo de um script versionado, e não vai num post público. O padrão que usei foi um arquivo de credenciais com permissão restrita, que os scripts apenas carregam:

```bash
umask 077 && cat > ~/.dvr_creds <<'EOF'
DVR_USER=admin
DVR_PASS=trocar_aqui
EOF
chmod 600 ~/.dvr_creds
```

E todo script começa com:

```bash
source ~/.dvr_creds
AUTH=(--digest -u "${DVR_USER}:${DVR_PASS}")
```

Usar um array pro `curl` mantém a senha como uma variável só, sem espalhar pela linha de comando em cada chamada. Não é perfeito (a senha ainda aparece na tabela de processos durante a chamada, via `/proc`), mas pra rede doméstica controlada é um equilíbrio sensato entre praticidade e higiene. Se eu fosse rodar isso num ambiente compartilhado, partiria pra `--netrc` ou um cofre de verdade.

# Ler antes de escrever

Aqui está o princípio que separa mexer com confiança de quebrar o sistema às cegas: **a primeira coisa que a API faz é leitura, não escrita**. Os nomes dos parâmetros variam entre versões de firmware, e eu não ia descobrir o nome certo escrevendo e torcendo. O `configManager.cgi` lê qualquer tabela com `action=getConfig&name=<Tabela>`.

A configuração de codificação fica em `Encode`:

```bash
curl -s "${AUTH[@]}" \
  "http://$DVR_IP:$PORT/cgi-bin/configManager.cgi?action=getConfig&name=Encode" \
  | grep -E '^table\.Encode\[0\]'
```

A saída é um formato chave-valor plano, com índices entre colchetes. O canal 0 da API é o canal 1 do aparelho. Cada canal tem `MainFormat[0]` (o stream principal, que grava) e `ExtraFormat[0]` (o stream extra, leve, pra ver remoto):

```
table.Encode[0].MainFormat[0].Video.Compression=H.265
table.Encode[0].MainFormat[0].Video.resolution=1920x1080
table.Encode[0].MainFormat[0].Video.FPS=15
table.Encode[0].MainFormat[0].Video.BitRateControl=VBR
table.Encode[0].MainFormat[0].Video.BitRate=3072
table.Encode[0].MainFormat[0].Video.Quality=6
table.Encode[0].MainFormat[0].AudioEnable=false
table.Encode[0].ExtraFormat[0].Video.resolution=704x480
table.Encode[0].ExtraFormat[0].Video.FPS=10
table.Encode[0].ExtraFormat[0].Video.BitRate=512
```

Esse dump é o mapa. A partir dele eu sei exatamente o nome de cada campo que vou querer escrever, sem adivinhação.

# As tabelas que importam

Lendo as tabelas relevantes, montei o mapeamento entre o que a interface gráfica chama de uma coisa e o que a API chama de outra. Esse foi o pulo do gato, porque os nomes não batem:

A tabela `VideoColor` guarda brilho, contraste, saturação, matiz e, surpresa, a nitidez (que a UI chama de "Nitidez" e a API chama de `Acutance`). Ela é indexada por canal e por período de tempo, `VideoColor[canal][periodo]`. O período `[0]` é o perfil ativo (seção de tempo habilitada, `00:00-24:00`); o `[1]` é uma segunda faixa que no meu caso estava desabilitada. Ou seja, eu só escrevo no período `[0]`:

```
table.VideoColor[0][0].Brightness=50
table.VideoColor[0][0].Contrast=50
table.VideoColor[0][0].Saturation=50
table.VideoColor[0][0].Hue=50
table.VideoColor[0][0].Acutance=5
table.VideoColor[0][0].TimeSection=1 00:00:00-24:00:00
```

Ler `VideoColor` de todos os canais de uma vez também serviu pra confirmar o mapeamento de índice, batendo brilho e contraste com o que eu via na tela canal a canal. Conferir o mapa contra a realidade antes de escrever evitou que eu sobrescrevesse o canal errado.

E aqui um dado me corrigiu. Minha ideia inicial era padronizar tudo em 50, ponto neutro de uma escala 0-100. Funciona pra brilho, contraste e saturação. Mas a leitura mostrou que a `Acutance` (nitidez) das câmeras estava em 1 a 5, e a câmera que eu achava a melhor de todas rodava em 1. Numa escala 0-100, esses valores são quase nada de realce, e por bom motivo: nitidez alta à noite só amplifica grão do infravermelho. Se eu tivesse cravado 50 no automático, teria deixado as quatro super-realçadas e cheias de ruído. Padronizei em 5. A lição vale além do DVR: "valor neutro" presumido não é "valor bom", e só a leitura do que o aparelho já usava me mostrou a diferença.

A "Redução de ruído" da interface não está em `VideoColor` nem no `VideoInOptions`. Demorei a achar: ela vive em `VideoInDenoise`, com controle 2D e 3D separados:

```
table.VideoInDenoise[0][0].2DEnable=true
table.VideoInDenoise[0][0].2DLevel=100
table.VideoInDenoise[0][0].3DAutoType.AutoLevel=40
```

E o ganho de imagem fica em `VideoInOptions[canal].Gain`, com uma variante `NightOptions.Gain` pro modo noturno. Detalhe interessante: o valor do `Gain` na API nem sempre bate número a número com o slider "Ganho imagem" da UI, sinal de que a interface aplica alguma transformação ou agrega campos. Mais um motivo pra testar num canal e conferir o resultado no preview antes de replicar.

# O que a API NÃO deixa fazer

Aqui vem a parte honesta, e a mais importante de um post de engenharia reversa: nem tudo está exposto. A câmera que eu queria consertar tinha listras horizontais, o clássico flicker de iluminação, em que uma lâmpada LED pulsando bate com o obturador eletrônico da câmera. O ajuste pra isso é o anti-flicker, que vive na exposição. Fui ler a tabela de exposição:

```bash
curl -s "${AUTH[@]}" \
  "http://$DVR_IP:$PORT/cgi-bin/configManager.cgi?action=getConfig&name=VideoInExposure"
# Error
# Bad Request!
```

`Bad Request`. A tabela `VideoInExposure` não existe nesse firmware. Varri os nomes prováveis (`VideoInAntiFlicker`, `VideoInDayNight`, `VideoInNR`) e todos voltaram vazios. A conclusão, com evidência e não com achismo: **exposição, shutter e anti-flicker não são controláveis pela API neste DVR**.

Pra não parar no "não achei a tabela", fui perguntar ao próprio aparelho o que ele suporta naquele canal, com `devVideoInput.cgi?action=getCaps`:

```bash
curl -g -s "${AUTH[@]}" \
  "http://$DVR_IP:$PORT/cgi-bin/devVideoInput.cgi?action=getCaps&channel=2"
# caps.Gain=false
# caps.VideoInDenoise.2D.Support=true
# caps.ImageEnhancement.Support=true
# ... nenhuma linha de shutter, exposure, antiflicker ou WDR
```

Isso fecha a questão de um jeito mais forte que o `Bad Request`: não é que a API esconde o anti-flicker, é que **essa câmera não tem esse controle pra expor**. Faz sentido. São câmeras analógicas HDCVI baratas, exposição automática e ponto. Quando esse controle existe, em geral mora no menu OSD da câmera, navegado por sinal coaxial, não na config do gravador. O `coaxialControlIO.cgi` respondeu (consegui ler status de speaker e luz branca), então o canal de controle pra câmera até existe, só não tem o botão que eu queria do outro lado.

Saber o limite da ferramenta é tão valioso quanto saber o que ela faz. Eu poderia ter perdido uma hora montando um `setConfig` de anti-flicker que o aparelho ia ignorar em silêncio, ou pior, subido numa escada pra caçar um menu OSD que essa câmera nem tem. Duas leituras de API mataram as duas ilusões em segundos.

# Escrevendo a configuração (e a pegadinha do glob)

Com o mapa na mão, escrever deveria ser trivial. O `setConfig` aceita múltiplos campos numa chamada, separados por `&`. Montei a primeira escrita, mandei, e o servidor respondeu com uma linha em branco. Sem `OK`, sem erro. E a leitura de volta mostrava os valores antigos, intocados.

O motivo me custou alguns minutos: o `curl` interpreta `[` e `]` como **globbing de URL** (aquele recurso que expande `http://site/arq[1-10].jpg`). Os índices `[0][0]` dos nomes de parâmetro caíam direto nessa armadilha e a requisição saía mangled. A correção é uma flag, `-g` (ou `--globoff`):

```bash
curl -g -s "${AUTH[@]}" \
  "http://$DVR_IP:$PORT/cgi-bin/configManager.cgi?action=setConfig\
&VideoColor[0][0].Brightness=50\
&VideoColor[0][0].Contrast=50\
&VideoColor[0][0].Saturation=50\
&VideoColor[0][0].Acutance=5"
```

Com o `-g`, a resposta vira `OK` e os valores pegam. Detalhe que vale ouro: foi a **leitura de volta** que denunciou a falha silenciosa. Se eu tivesse confiado no `OK` ausente sem reler, teria saído achando que apliquei quando não apliquei nada. O método pra padronizar as quatro câmeras vira um laço sobre os índices de canal, aplicando o mesmo conjunto de valores. Mas a disciplina aqui é a mesma de qualquer mudança em produção: **aplica em um canal, confere no preview ao vivo, e só então replica pros outros**. Num sistema de segurança eu não faço fan-out de uma mudança não verificada.

E o aparelho me deu mais um motivo pra reler tudo: ao padronizar o stream extra em 10fps, o `setConfig` respondeu `OK` nos quatro canais, mas a leitura de volta mostrou três deles travados em 7fps. O DVR aceitou o comando e **clampou o valor em silêncio** num teto de hardware do stream secundário. `OK` não significa "gravei o que você pediu", significa "recebi". A única fonte de verdade é reler a config depois de escrever. Esse é o tipo de detalhe que separa "achei que configurei" de "configurei".

# O que levo desse domingo

Três coisas ficam.

A primeira é que muito equipamento doméstico de prateleira esconde uma API perfeitamente utilizável atrás de uma interface ruim. DVR, roteador, nobreak, impressora. Vale o probe.

A segunda é o método: alcance, autenticação, leitura, mapeamento, e só no fim a escrita. A leitura não é só reconhecimento, é o que transforma chute em certeza e revela o que o aparelho nem suporta.

A terceira é uma pendência que esse exercício escancarou: o DVR está em DHCP. Toda essa automação aponta pra um IP que pode mudar quando o roteador resolver. Próximo passo é reservar um IP fixo pra ele no DHCP do roteador, pra que o script não quebre sozinho numa madrugada qualquer. Endereço de infraestrutura que você automatiza não pode ser volátil, e isso vale tanto pra um DVR de casa quanto pra qualquer serviço que a gente opera em produção.

No fim das contas, a câmera com listra não tem conserto por API. A luz que causa o flicker é de um poste da rua, apagar não é opção. O conserto de software seria o anti-flicker, travando o obturador num múltiplo do ciclo de 60Hz da rede pra pulsação somar zero, mas o próprio aparelho me disse, via `getCaps`, que essa câmera não tem esse controle. Então sobra o físico: tirar o poste do enquadramento direto e pôr um capuz na lente pra cortar a luz que entra reta no sensor. Anticlimático, mas é a verdade que a investigação entregou, e descobri isso sem subir escada nenhuma. Saí com as quatro câmeras padronizadas em segundos em vez de meia hora de clique, e com um mapa da API que vou reusar toda vez que precisar mexer nelas.
