---
title: "A API HTTP escondida do meu DVR Intelbras: ajustando 4 câmeras pela linha de comando"
draft: false
date: 2026-07-29T00:00:00.000Z
description: "Meu DVR Intelbras MHDX 3004-C expõe uma API CGI no estilo Dahua que ninguém documenta direito. Em vez de clicar canal por canal numa interface web pesada, li e ajustei a configuração das câmeras com curl e autenticação Digest. Conto o passo a passo real: como achei a porta, como autentiquei, como li as tabelas de config antes de escrever qualquer coisa, o que dá pra controlar (encoder, cor, redução de ruído) e o que eu não consegui controlar por ela (exposição e anti-flicker), e como mantive a senha fora do histórico."
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

Comecei a tarde de domingo querendo só arrumar uma câmera que estava com a imagem estranha e terminei com um script que lê e escreve a configuração das quatro câmeras do meu DVR direto pela linha de comando. No caminho descobri que o Intelbras MHDX 3004-C expõe uma interface CGI compatível com a família de APIs da Dahua, coisa que quase ninguém documenta em português. Faço a ressalva porque ela importa: eu não abri o firmware nem li strings de build pra saber de quem é o código. O que eu tenho é comportamento observado. A autenticação, os caminhos em `/cgi-bin/` e os nomes das tabelas seguem o mesmo padrão da Dahua, o que já é suficiente pra documentação de Dahua servir de mapa aqui. Origem do firmware é outra afirmação, bem mais forte, e essa eu não posso fazer.

A interface web do aparelho é aquela coisa pesada, cheia de combobox, em que você ajusta um parâmetro, troca de canal, espera recarregar, repete. Com quatro câmeras e um punhado de parâmetros pra padronizar, isso é trabalho manual chato e propenso a erro. A pergunta óbvia pra quem vive em terminal: dá pra fazer isso por API? Dá. E o caminho até lá é um bom exercício de engenharia reversa educada, do tipo ler antes de escrever.

Este post documenta o que funcionou de verdade no meu aparelho: MHDX 3004-C, firmware `4.001.00IB000`, build de agosto de 2024, com as quatro câmeras analógicas que estão ligadas nele. Fora desse conjunto exato eu não garanto nada. Nome de tabela, índice, faixa de valor, capability anunciada, resposta de erro e teto de FPS mudam entre modelo, revisão de hardware e versão de firmware. É exatamente por isso que a primeira metade do trabalho é descobrir, não chutar, e é por isso que não vale ler isso aqui como receita pra linha Intelbras inteira nem pra qualquer aparelho Dahua.

# Achando a porta

Primeiro fato: o DVR estava na mesma rede que a máquina de onde eu trabalho. Peguei o IP local dele na própria tela de rede do aparelho (ele estava em DHCP, o que por si só já é um problema que comento no final). O teste inicial de alcance foi direto:

```bash
ping -c2 "$DVR_IP"
curl -s -o /dev/null -w "%{http_code}\n" "http://$DVR_IP"
```

O ping não recebeu nenhuma resposta, e o `curl` devolveu `http_code=000`. Quase desisti achando que não alcançava o aparelho. Estava errado nas duas leituras.

Ping sem resposta em DVR é comum, muito aparelho simplesmente não responde ICMP. E `000` não é um código HTTP: é o `curl` avisando que não chegou a receber resposta HTTP nenhuma. Pode ser timeout, conexão recusada, falta de rota, protocolo errado, qualquer coisa que aconteça antes do servidor responder. Como diagnóstico, `000` sozinho não vale nada, ele só diz "não deu".

O que vale é pedir pro `curl` contar o motivo. Do 7.75 em diante dá pra imprimir o exit code e a mensagem de erro no mesmo `-w`, e com `-sS` o erro para de ficar escondido:

```bash
curl -sS --connect-timeout 3 \
  -o /dev/null \
  -w 'http=%{http_code} exit=%{exitcode} erro=%{errormsg}\n' \
  "http://$DVR_IP"
```

Aí o `000` deixa de ser beco sem saída e vira frase: exit 7 é conexão recusada ou sem rota, exit 28 é timeout, exit 6 é DNS. Em `curl` mais velho que 7.75 esses dois campos não existem, e o equivalente é olhar o `$?` do shell e deixar o stderr aparecer. Não guardei a saída da tentativa original, então não vou dizer aqui qual exit code apareceu naquele domingo.

A parte que eu descobri em seguida: a interface web não estava na 80. O aparelho usa uma porta HTTP customizada, alta. Com a porta certa:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" "http://$DVR_IP:$PORT"
# 200
```

Lição que sempre esqueço: separe "o host está vivo" de "o serviço está na porta que eu chutei". Ping testa resposta a ICMP e nada mais, não diz se tem HTTP escutando em algum lugar. São perguntas diferentes, e eu tinha feito a errada duas vezes seguidas.

# A autenticação é Digest, não Basic

Com a web respondendo, fui bater na API CGI. O padrão Dahua expõe tudo em `/cgi-bin/`. O primeiro probe é pedir o tipo do aparelho:

```bash
curl -sS -i "http://$DVR_IP:$PORT/cgi-bin/magicBox.cgi?action=getDeviceType"
```

A resposta foi um `401 Unauthorized` com um header revelador:

```
WWW-Authenticate: Digest realm="Login to ...", qop="auth", nonce="...", opaque=""
```

`Digest`, não `Basic`. Isso muda o `curl`: tem que usar `--digest`, senão a credencial nem é negociada direito. O `curl` faz o desafio-resposta de Digest sozinho, então na prática é só trocar a flag:

```bash
curl -sS --digest -u "$DVR_USER:$DVR_PASS" \
  "http://$DVR_IP:$PORT/cgi-bin/magicBox.cgi?action=getDeviceType"
# type=MHDX 3004-C
```

Funcionou. A partir daqui é tudo `configManager.cgi`.

Uma ressalva que precisa vir junto: Digest é melhor que Basic porque a senha não viaja em claro, ele faz desafio-resposta com hash em cima do nonce. Mas isso autentica, não cifra. A conexão continua sendo `http://`, então URL, endpoint, parâmetros que eu escrevo e a config que volta na resposta ficam todos legíveis pra quem estiver na mesma rede olhando o tráfego. Por isso isso aqui é coisa de rede local controlada, de preferência num segmento isolado só pros bichos de câmera, e por isso DVR não fica publicado na internet. Se o firmware do teu oferecer HTTPS de forma confiável, prefira HTTPS.

# Mantendo a senha fora do histórico

Antes de seguir, um parêntese que pra mim não é negociável. Senha de DVR é credencial de sistema de segurança física da minha casa. Ela não vai pro histórico do shell, não vai pro corpo de um script versionado, e não vai num post público. O padrão que usei foi um arquivo de credenciais com permissão restrita, que os scripts apenas carregam:

```bash
umask 077
cat > ~/.dvr_creds <<'EOF'
DVR_USER='admin'
DVR_PASS='troque aqui'
EOF
chmod 600 ~/.dvr_creds
```

As aspas simples não são decoração. Esse arquivo vai ser lido com `source`, ou seja, é shell de verdade: senha com espaço, `$`, crase ou aspas duplas sem quoting vira expansão ou erro de sintaxe, e você descobre isso na forma de um 401 que não faz sentido. Aspas simples resolvem tudo menos a própria aspa simples; se a tua senha tiver uma, escapa com `'\''` ou troca a senha.

E todo script começa com:

```bash
source ~/.dvr_creds
AUTH=(--digest -u "${DVR_USER}:${DVR_PASS}")
```

O array ajuda em organização e quoting, mantém a credencial como um argumento só e evita que ela se espalhe pela linha em cada chamada. Mas vale ser honesto sobre o que ele não faz: no instante em que o `curl` roda, os argumentos já foram expandidos pro processo, e a senha está na linha de comando visível em `ps` e em `/proc`. Array nenhum conserta isso. Pra rede doméstica controlada eu aceito essa troca. Em máquina compartilhada eu não aceitaria, e o caminho seria `--netrc` ou um cofre de verdade. Fica registrado que eu não validei o `--netrc` contra esse DVR, então não estou recomendando como testado, e vale saber que a entrada do `.netrc` casa por host, não por porta, o que importa justamente aqui porque o aparelho não está na 80.

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

E tem um campo de ganho de imagem em `VideoInOptions[canal].Gain`, com uma variante `NightOptions.Gain` pro modo noturno. Esse eu não decifrei. O valor do `Gain` na API não bate número a número com o slider "Ganho imagem" da UI, e mais pra frente o `getCaps` do canal ainda me devolveu `caps.Gain=false`. Um campo que existe na tabela de config e uma capability negada pelo canal aparentemente não são a mesma coisa, provavelmente camadas diferentes, processamento no gravador de um lado e ganho nativo da câmera do outro, ou um parâmetro legado que ficou na tabela. Não fechei isso com o que o aparelho me devolveu, então fica registrado como não esclarecido em vez de explicado por chute. Na prática, mais um motivo pra testar num canal e conferir no preview antes de replicar.

# O que a API NÃO deixa fazer

Aqui vem a parte honesta, e a mais importante de um post de engenharia reversa: nem tudo está exposto. A câmera que eu queria consertar tinha listras horizontais, o clássico flicker de iluminação, em que uma lâmpada LED pulsando bate com o obturador eletrônico da câmera. O ajuste pra isso é o anti-flicker, que vive na exposição. Fui ler a tabela de exposição:

```bash
curl -s "${AUTH[@]}" \
  "http://$DVR_IP:$PORT/cgi-bin/configManager.cgi?action=getConfig&name=VideoInExposure"
# Error
# Bad Request!
```

`Bad Request`. O que isso me autoriza a dizer é modesto: o firmware não aceitou `VideoInExposure` por esse endpoint e nesse formato. `Bad Request` cobre várias coisas, nome de tabela diferente, formato de requisição inválido, permissão do usuário, endpoint que não é esse. Não é prova de que a tabela não existe. Varri os nomes prováveis (`VideoInAntiFlicker`, `VideoInDayNight`, `VideoInNR`) e todos voltaram vazios, o que aumenta a suspeita mas continua sendo ausência de resposta útil, não demonstração de ausência.

Pra não parar no "não achei a tabela", fui perguntar ao próprio aparelho o que ele suporta naquele canal, com `devVideoInput.cgi?action=getCaps`:

```bash
curl -g -s "${AUTH[@]}" \
  "http://$DVR_IP:$PORT/cgi-bin/devVideoInput.cgi?action=getCaps&channel=2"
# caps.Gain=false
# caps.VideoInDenoise.2D.Support=true
# caps.ImageEnhancement.Support=true
# ... nenhuma linha de shutter, exposure, antiflicker ou WDR
```

Isso é mais forte que o `Bad Request`, mas ainda não é onisciência. O que os dois juntos sustentam: as tabelas que eu procurei não foram aceitas, e o canal não anunciou capability de shutter, exposição, antiflicker ou WDR nos endpoints que eu testei. Ou seja, **com os endpoints e as capabilities expostos por esse conjunto de DVR, firmware e câmera, eu não encontrei um caminho suportado pra controlar o anti-flicker**. Isso não é a mesma coisa que dizer que o controle não existe em nenhum canto da API, nem que a câmera não tem esse ajuste por outro caminho, nem que outro firmware não exporia. Não testei tudo, e não tenho como testar tudo.

O palpite informado, e eu marco que é palpite, é que são câmeras analógicas HDCVI simples, de exposição automática. Nessa família, quando o ajuste existe, costuma morar no menu OSD da câmera, navegado por sinal coaxial, e não na config do gravador. O `coaxialControlIO.cgi` respondeu (consegui ler status de speaker e luz branca), então o canal de controle pra câmera existe. Só não achei do outro lado dele o botão que eu queria.

Saber o limite da ferramenta é tão valioso quanto saber o que ela faz. Eu poderia ter perdido uma hora montando um `setConfig` de anti-flicker que o aparelho ia ignorar em silêncio, ou pior, subido numa escada pra caçar um menu OSD que talvez não esteja lá. Duas leituras de API me pouparam as duas coisas em segundos.

# Backup antes da primeira escrita

Regra que eu não quebro nem em casa: antes do primeiro `setConfig`, tira um retrato do que está lá. Não porque eu espero errar, mas porque a config atual é a única referência do que era o estado bom, e esse aparelho não tem desfazer.

Aqui também muda a natureza dos comandos. Até agora eu estava explorando na mão, e podia ler a saída de cada um. Daqui pra frente é automação, e automação precisa de timeout e de erro visível:

```bash
source ~/.dvr_creds
CURL=(-sS -g --digest -u "${DVR_USER}:${DVR_PASS}"
      --connect-timeout 3 --max-time 15)
BASE="http://$DVR_IP:$PORT/cgi-bin"
```

O `-sS` cala a barra de progresso mas deixa o erro aparecer, o `--connect-timeout` e o `--max-time` evitam que um script fique pendurado a madrugada inteira num aparelho que travou. Do `curl` 7.76 em diante existe também o `--fail-with-body`, que faz o exit code refletir status HTTP de erro sem jogar o corpo da resposta fora. Só não bota ele no probe de descoberta que espera justamente um `401` pra revelar o esquema Digest, senão você transforma o resultado desejado em falha.

Com isso, o backup:

```bash
BKP="$HOME/dvr-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BKP" && chmod 700 "$BKP"

for t in VideoColor VideoInDenoise VideoInOptions Encode; do
  curl "${CURL[@]}" "$BASE/configManager.cgi?action=getConfig&name=$t" \
    > "$BKP/$t.txt" || echo "FALHOU: $t" >&2
done

{
  date -Iseconds
  curl "${CURL[@]}" "$BASE/magicBox.cgi?action=getDeviceType"
  curl "${CURL[@]}" "$BASE/magicBox.cgi?action=getSoftwareVersion"
} > "$BKP/contexto.txt"

chmod 600 "$BKP"/*
```

Modelo, versão de firmware e data no mesmo diretório das tabelas, porque dump de config sem saber de que firmware ele veio é quase inútil daqui a um ano. E não existe, pelo menos não que eu tenha achado nesse firmware, endpoint de restore em massa que engula esse arquivo de volta. Então trata o dump pelo que ele é: referência recuperável pra reaplicar valor por valor com `setConfig` se algo sair errado. Ele também é a configuração do sistema de segurança da tua casa, então mora com a mesma disciplina do arquivo de credencial, permissão fechada e longe de qualquer repositório.

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

Com o `-g`, a resposta vira `OK` e os valores pegam.

Antes de seguir, o aviso que falta nessa linha: `-g` resolve o colchete, não resolve encoding. Os valores que eu escrevo aqui são números, então passam limpos. No dia em que o valor tiver espaço ou caractere reservado, e tem, o `TimeSection` é literalmente `1 00:00:00-24:00:00`, ele precisa ir codificado. Pensei em montar tudo com `--get --data-urlencode`, que seria o jeito canônico, e não fui: nessa forma o `curl` codifica também o nome do parâmetro, e `VideoColor%5B0%5D%5B0%5D.Brightness` pode ou não ser aceito por esse CGI. Como eu não testei, fico com o `-g` que eu vi funcionando e digo o que não sei, em vez de recomendar por elegância. Mesma coisa pra POST: não confirmei que esse CGI aceita, então não converti.

Detalhe que vale ouro: foi a **leitura de volta** que denunciou a falha silenciosa. Se eu tivesse confiado no `OK` ausente sem reler, teria saído achando que apliquei quando não apliquei nada. O método pra padronizar as quatro câmeras vira um laço sobre os índices de canal, aplicando o mesmo conjunto de valores. Mas a disciplina aqui é a mesma de qualquer mudança em produção: **aplica em um canal, confere no preview ao vivo, e só então replica pros outros**. Num sistema de segurança eu não faço fan-out de uma mudança não verificada.

E o aparelho me deu mais um motivo pra reler tudo: ao padronizar o stream extra em 10fps, o `setConfig` respondeu `OK` nos quatro canais, mas a leitura de volta mostrou três deles travados em 7fps. O DVR aceitou o comando e **clampou o valor em silêncio** num teto de hardware do stream secundário. Nesse firmware, `OK` confirma que a requisição foi aceita, não que cada valor foi persistido exatamente como pedido. A única fonte de verdade é reler a config depois de escrever e comparar campo a campo. O que é uma coisa boba de automatizar, e que eu devia ter feito desde o começo:

```bash
check() { # check <tabela> <chave> <esperado>
  local got
  got=$(curl "${CURL[@]}" "$BASE/configManager.cgi?action=getConfig&name=$1" \
        | grep -F "table.$2=" | cut -d= -f2-)
  if [ "$got" = "$3" ]; then
    echo "ok        $2=$got"
  else
    echo "DIVERGIU  $2: pedi $3, gravou ${got:-<vazio>}" >&2
    return 1
  fi
}

check Encode 'Encode[0].ExtraFormat[0].Video.FPS' 10
```

Com isso o 7fps aparece como divergência na cara, não como um `OK` que eu li rápido. O ciclo que eu sigo agora é sempre esse: escreve, relê, compara pedido com persistido, e só então replica pros outros canais. É o tipo de detalhe que separa "achei que configurei" de "configurei".

# O que levo desse domingo

Três coisas ficam.

A primeira é que muito equipamento doméstico de prateleira tem uma API perfeitamente utilizável, e não documentada, atrás de uma interface ruim. Não que o fabricante esteja escondendo: é o mesmo endpoint que a interface web dele consome, só sem manual em português. DVR, roteador, nobreak, impressora. Vale o probe.

A segunda é o método: alcance, autenticação, leitura, mapeamento, e só no fim a escrita. A leitura não é só reconhecimento, é o que transforma chute em certeza e revela o que o aparelho não expõe.

A terceira é uma pendência que esse exercício escancarou: o DVR está em DHCP. Toda essa automação aponta pra um IP que pode mudar quando o roteador resolver. Próximo passo é reservar um IP fixo pra ele no DHCP do roteador, pra que o script não quebre sozinho numa madrugada qualquer. Endereço de infraestrutura que você automatiza não pode ser volátil, e isso vale tanto pra um DVR de casa quanto pra qualquer serviço que a gente opera em produção.

No fim das contas, a câmera com listra não tem conserto por API, pelo menos não por um caminho que eu tenha achado. A luz que causa o flicker é de um poste da rua, apagar não é opção. O conserto de software seria o anti-flicker, que sincroniza o tempo de exposição com a frequência da rede ou com a pulsação efetiva da iluminação. Numa rede de 60Hz o LED pode piscar em 60 ou em 120Hz dependendo do driver dele, e é por isso que não dá pra recomendar número mágico de shutter sem conhecer a câmera, a luz e os modos que o firmware oferece. De todo jeito é conversa teórica aqui: nem o `getConfig` das tabelas de exposição nem o `getCaps` do canal me deram um caminho suportado pra chegar nesse ajuste. Então sobra o físico: tirar o poste do enquadramento direto e pôr um capuz na lente pra cortar a luz que entra reta no sensor. Anticlimático, mas é a verdade que a investigação entregou, e descobri isso sem subir escada nenhuma. Saí com as quatro câmeras padronizadas em segundos em vez de meia hora de clique, e com um mapa da API que vou reusar toda vez que precisar mexer nelas.
