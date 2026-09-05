---
title: "O termo de fronteira da regra de Leibniz"
draft: false
date: 2026-09-02T00:00:00.000Z
description: "Derivar sob o sinal da integral quando os limites também se movem é a regra de Leibniz, e quase todo mundo que aplica ela esquece o termo de fronteira. Num caso que eu conferi numericamente, esquecer esse termo erra a resposta em 4,5 de 11,385, quase 40% do valor. Este post deriva os três termos a partir da regra da cadeia, dá as hipóteses que a troca de derivada com integral exige, mostra onde ela quebra em domínio infinito e no suporte de uma distribuição, e investiga a parte incômoda da história: o que Leibniz de fato escreveu não é a regra que hoje leva o nome dele."
comments: true
keywords: [
  "regra de Leibniz",
  "derivação sob o sinal da integral",
  "termo de fronteira",
  "limites variáveis de integração",
  "teorema fundamental do cálculo",
  "truque de Feynman",
  "convergência dominada",
  "score function estimator",
  "cálculo",
  "Leibniz",
  "história da matemática",
  "análise real"
]
tags:
  - matemática
  - educação
---

## Introdução

A conta dava 6,885. O valor certo era 11,385. A diferença, 4,5 exatos, não era erro de arredondamento nem de quadratura: era um termo inteiro que eu tinha deixado de escrever. Quase 40% da resposta desaparecida porque a derivada de uma integral tem três pedaços e eu só tinha somado dois.

Derivar integral de limites fixos é entediante: $\int_0^1 g(\tau) d\tau$ é um número, e derivada de número é zero. Fica interessante quando o $t$ que você está derivando aparece em mais de um lugar dentro da integral. O Teorema Fundamental do Cálculo cobre o caso em que ele aparece só no limite. A regra de Leibniz cobre também o caso em que ele aparece dentro do integrando, e os dois ao mesmo tempo, que é o que acontece de verdade quando você modela acumulação com memória.

Na forma geral:

<div class="formula">
$$ \frac{d}{dt}\int_{a(t)}^{b(t)} g(t,\tau)\,d\tau = g\big(t,b(t)\big)\,b'(t) - g\big(t,a(t)\big)\,a'(t) + \int_{a(t)}^{b(t)} \frac{\partial g}{\partial t}(t,\tau)\,d\tau $$
</div>
<p class="formula-nota">Os dois primeiros termos são fronteira: eles medem o efeito de mexer a região de integração. O terceiro é interior: mede o efeito de a curva inteira mudar de altura.</p>

Não vale decorar isso. Vale ver de onde sai, porque de onde sai é regra da cadeia, e aí os três termos param de ser arbitrários.

## Parte I: os três termos são a regra da cadeia disfarçada

O truque é parar de ver a integral como função de $t$ e ver ela como função de três argumentos independentes. Define

<div class="formula">
$$ H(t,u,v) = \int_u^v g(t,\tau)\,d\tau $$
</div>

e repara que o que você quer é a derivada de $H(t, a(t), b(t))$, uma composição. A cadeia entrega direto:

<div class="formula">
$$ \frac{dH}{dt} = \frac{\partial H}{\partial v}\,b'(t) + \frac{\partial H}{\partial u}\,a'(t) + \frac{\partial H}{\partial t} $$
</div>

Agora os três pedaços, um por um. $\partial H/\partial v = g(t,v)$ é Teorema Fundamental do Cálculo puro: mexer o limite de cima acrescenta área na borda direita, e a taxa com que ela entra é a altura da curva ali. $\partial H/\partial u = -g(t,u)$ é o mesmo TFC com o sinal trocado, porque subir o limite de baixo tira área. Nenhum dos dois é novidade: você já sabia os dois antes de ouvir falar em Leibniz.

O único pedaço que é teorema de fato é o terceiro, $\partial H/\partial t = \int_u^v \partial_t g(t,\tau) d\tau$. Ele diz que dá pra trocar a ordem de duas operações de limite, derivar e integrar, e essa troca é justamente o que precisa de hipótese pra valer. É esse pedaço que se chama derivar sob o sinal da integral. A regra de Leibniz é ele mais dois termos de fronteira que já vinham de graça. E isso não é atalho didático meu: é assim que a prova é montada nas notas de Keith Conrad, com a versão de limites variáveis saindo como corolário da versão de limites fixos, aplicando a regra da cadeia exatamente a essa função de três argumentos.

A intuição geométrica fecha o assunto. Entre $t$ e $t+dt$ a integral muda por dois motivos independentes. A região de integração cresce, e nasce uma tira fina de área na borda, de largura $dt$ e altura igual ao integrando naquele ponto. E a curva inteira sobe ou desce, em todo ponto do interior, porque o integrando também depende de $t$. Pensa numa piscina que fica ao mesmo tempo mais comprida e mais funda: o volume novo é a fatia que entrou na ponta mais o que subiu no resto do fundo. Somar os dois efeitos é a regra.

<figure class="diagrama">
<svg viewBox="0 0 400 210" role="img" aria-labelledby="diagrama-titulo diagrama-desc" xmlns="http://www.w3.org/2000/svg">
  <title id="diagrama-titulo">De onde vêm os três termos da regra de Leibniz</title>
  <desc id="diagrama-desc">Uma curva desenhada sobre um eixo horizontal, com a região de integração delimitada pelos limites a de t, à esquerda, e b de t, à direita. Quando t cresce, três coisas acontecem ao mesmo tempo. O limite de baixo anda para a direita e uma tira estreita de área sai da região: contribuição negativa. O limite de cima anda para a direita e uma tira estreita de área entra: contribuição positiva. E a curva inteira sobe entre os dois limites, indicada por uma segunda curva tracejada acima da primeira, acrescentando uma banda de área no interior: contribuição também positiva.</desc>
  <path class="area-base" d="M 95 103.1 L 113.8 96.7 132.5 91.1 151.2 86.5 170 83 188.8 80.9 207.5 80 226.2 80.5 245 82.3 263.8 85.4 282.5 89.7 301.2 95.1 320 101.3 L 320 170 L 95 170 Z"/>
  <path class="area-int" d="M 95 89.7 L 113.8 82 132.5 75.3 151.2 69.8 170 65.6 188.8 63 207.5 62 226.2 62.6 245 64.8 263.8 68.5 282.5 73.7 301.2 80.1 320 87.6 L 320 101.3 301.2 95.1 282.5 89.7 263.8 85.4 245 82.3 226.2 80.5 207.5 80 188.8 80.9 170 83 151.2 86.5 132.5 91.1 113.8 96.7 95 103.1 Z"/>
  <path class="area-sai" d="M 95 103.1 L 106.5 99.1 118 95.3 L 118 170 L 95 170 Z"/>
  <path class="area-entra" d="M 320 101.3 L 332.5 105.9 345 110.7 L 345 170 L 320 170 Z"/>
  <path class="guia" d="M 95 103.1 L 95 170 M 320 101.3 L 320 170"/>
  <path class="curva" d="M 40 125 L 61.2 116.2 82.5 107.8 103.8 100 125 93.2 146.2 87.6 167.5 83.4 188.8 80.9 210 80 231.2 80.9 252.5 83.4 273.8 87.6 295 93.2 316.2 100 337.5 107.8 358.8 116.2 380 125"/>
  <path class="curva-nova" d="M 95 89.7 L 113.8 82 132.5 75.3 151.2 69.8 170 65.6 188.8 63 207.5 62 226.2 62.6 245 64.8 263.8 68.5 282.5 73.7 301.2 80.1 320 87.6"/>
  <path class="eixo" d="M 30 170 L 385 170"/>
  <path class="seta" d="M 97 181 L 116 181 M 112 178 L 116 181 L 112 184"/>
  <path class="seta" d="M 322 181 L 343 181 M 339 178 L 343 181 L 339 184"/>
  <text class="sinal sinal-sai" x="106.5" y="140" text-anchor="middle">−</text>
  <text class="sinal sinal-entra" x="332.5" y="142" text-anchor="middle">+</text>
  <text class="sinal sinal-int" x="207.5" y="77" text-anchor="middle">+</text>
  <text class="rotulo" x="95" y="199" text-anchor="middle">a(t)</text>
  <text class="rotulo" x="320" y="199" text-anchor="middle">b(t)</text>
</svg>
<figcaption>Os dois limites andam para a direita e a curva sobe. O limite de baixo subindo <em>tira</em> área, e é daí que vem o sinal negativo de \(-g(t,a(t))a^{\prime}(t)\); o limite de cima subindo <em>põe</em> área; e a banda entre as duas curvas é o termo interior, \(\int \partial_t g\), o único dos três que precisa de hipótese pra existir.</figcaption>
</figure>

## As hipóteses, e onde continuidade deixa de bastar

A versão suficiente pra quase tudo é curta: se $g$ e $\partial g/\partial t$ forem contínuas num retângulo que contenha a região de integração, e $a$ e $b$ forem diferenciáveis, a fórmula vale. Num retângulo fechado a continuidade já dá limitação de graça, e é isso que faz a demonstração andar.

Em domínio infinito, continuidade não basta, e o contraexemplo é curto o suficiente pra caber numa linha:

<div class="formula">
$$ I(t) = \int_0^\infty t\,e^{-tx}\,dx $$
</div>

Para todo $t > 0$ isso vale exatamente 1, e você confere na mão: a primitiva é $-e^{-tx}$, avaliada de 0 a infinito dá 1, e o $t$ cancela. Em $t = 0$ o integrando é identicamente zero, então $I(0) = 0$. O integrando é suave em $t$ para cada $x$ fixo, e mesmo assim $I$ é descontínua na origem. Derivar sob o sinal ali não produz erro pequeno, produz besteira: a função nem é contínua no ponto.

A massa fugiu. Conforme $t$ diminui, a exponencial se espalha e fica baixinha, mas a área não muda, só migra pra longe. Nenhuma função integrável fixa segura a família toda por cima, e é exatamente isso que a dominação pede. No enunciado que o Conrad usa, pra derivar num ponto $t_0$: $g$ e $\partial_t g$ contínuas, e cotas $|g(t,\tau)| \le A(\tau)$ e $|\partial_t g(t,\tau)| \le B(\tau)$ independentes de $t$, com $A$ e $B$ integráveis. Repara no detalhe que muda tudo na prática: essas cotas são pedidas só para $t$ num intervalo em volta de $t_0$. A dominação é local no parâmetro, não é um contrato que você assina para todo $t$ do universo.

E é condição suficiente, não necessária. A versão de Lebesgue, que sai da convergência dominada, cobra menos: basta $g(\cdot,t)$ integrável para um $t$ e a cota integrável em cima da derivada, $|\partial_t g(t,\tau)| \le B(\tau)$, numa vizinhança de $t_0$. A cota em $g$ você não precisa trazer, ela cai do teorema do valor médio aplicado à própria derivada. Fica a regra de bolso: em retângulo compacto a continuidade compra a dominação; em domínio infinito você traz a dominação de casa, e traz menos do que parece.

## Um caso inteiro, com o erro medido

Pega um acumulador com memória logarítmica, que é a forma que aparece quando o passado pesa cada vez menos mas nunca zera:

<div class="formula">
$$ A(t) = A_0 + \int_0^t F(\tau)\,\log_2\!\big(2+t-\tau\big)\,d\tau $$
</div>
<p class="formula-nota">O parâmetro \(t\) aparece nos dois lugares que interessam: no limite de cima e dentro do núcleo. É o caso completo da regra, com um dos termos de fronteira ativo.</p>

Identificando as peças: $a(t) = 0$ com $a^{\prime} = 0$, o que mata o termo de fronteira de baixo; $b(t) = t$ com $b^{\prime} = 1$; e $g(t,\tau) = F(\tau)\log_2(2+t-\tau)$.

O termo de fronteira de cima é $g(t,t) \cdot 1 = F(t)\log_2 2 = F(t)$. Ele saiu redondo por construção: o núcleo vale exatamente 1 na diagonal. A derivada parcial do núcleo é $\partial_t \log_2(2+t-\tau) = 1/((2+t-\tau)\ln 2)$, e escrevendo $c = 1/\ln 2$:

<div class="formula">
$$ A'(t) = F(t) + c\int_0^t \frac{F(\tau)}{2+t-\tau}\,d\tau $$
</div>

A regularidade aqui é confortável: $g$ e $\partial_t g$ são contínuas no triângulo compacto $\lbrace 0 \le \tau \le t \le T\rbrace $ e o denominador nunca desce abaixo de 2. Nada perto de explodir, nenhuma dominação pra negociar.

Sobrou uma integral do mesmo formato, então aplica Leibniz de novo. O novo termo de fronteira é o núcleo na diagonal, $F(t)/2$, e a parcial do novo núcleo ganha um sinal negativo:

<div class="formula">
$$ A''(t) = F'(t) + c\left[\frac{F(t)}{2} - \int_0^t \frac{F(\tau)}{(2+t-\tau)^2}\,d\tau\right] $$
</div>

Agora a parte que interessa: conferir. Com $F(\tau) = 1 + \tau/2$ e $t = 7$, comparando a expressão de Leibniz contra a derivada numérica da integral obtida por quadratura de Simpson e diferença finita central:

| | numérico | fórmula de Leibniz | erro |
|---|---|---|---|
| $A^{\prime}(7)$ | 11,385154864385 | 11,385154864821 | 4,4e-10 |
| $A^{\prime\prime}(7)$ | 1,745261940300 | 1,745261949709 | 9,4e-09 |

Os dois erros são do método, não da fórmula. A coluna de Leibniz bate com a forma fechada da integral na décima quinta casa, então o que a tabela mostra é erro da derivada numérica, e ele erra pelo motivo esperado. Variando o passo, aparece o desenho de sempre: o erro da diferença central cai como $h^2$ até perto de $h = 10^{-4}$ e depois volta a subir como $1/h$, quando subtrair dois números quase iguais passa a custar mais do que a aproximação ganha. A diferença segunda faz a mesma curva, só que o ramo de arredondamento sobe como $1/h^2$. É por isso que os dois passos da tabela são diferentes, cada um perto do fundo da curva do seu método, e por isso a segunda linha erra mais mesmo usando passo cem vezes maior.

Todas as contas deste post estão num script de verificação em Python, só biblioteca padrão, que imprime método, discretização, valor esperado, valor obtido, erro absoluto e tolerância, e sai com código diferente de zero se qualquer verificação passar da tolerância justificada pro método dela: [verificacao.py](/code/2026-09-02-termo-de-fronteira-regra-de-leibniz/verificacao.py). São 21 verificações e roda em um segundo e meio.

E o número que abriu o post: esquecendo o termo de fronteira, $A^{\prime}(7)$ daria 6,885154864821 em vez de 11,385154864821. A diferença é 4,5 exatos, que é exatamente $F(7)$, o termo que ficou de fora. Não é erro pequeno, é 39,5% da resposta. E não podia ser pequeno: o termo de fronteira vale $g(t,b(t))b^{\prime}(t)$, uma quantidade da ordem do próprio integrando. Quem esquece ele não perde precisão, perde o resultado.

A segunda armadilha é mais boba e mais comum: usar a mesma letra para a variável de integração e para o parâmetro. Escrever $\int_0^t F(t) dt$ não é notação relaxada, é expressão sem sentido, e o efeito colateral pior é apagar a possibilidade de aplicar a regra. Se as duas coisas têm o mesmo nome, você não consegue nem perguntar qual está variando.

## Onde isso aparece em computação

Nada disso é exclusividade de integral com primitiva fechada. A regra aparece em lugares que qualquer pessoa que escreve código encontra, e em dois dos três casos abaixo o termo de fronteira não é detalhe: é a resposta inteira.

O primeiro é a janela deslizante, que é o agregado mais comum de qualquer sistema de observabilidade. Soma dos últimos $W$ minutos é uma integral com os dois limites andando junto com o tempo:

<div class="formula">
$$ A(t) = \int_{t-W}^{t} f(\tau)\,d\tau \qquad\Longrightarrow\qquad A^{\prime}(t) = f(t) - f(t-W) $$
</div>
<p class="formula-nota">O integrando não depende de $t$, então o termo interior é zero e sobra fronteira pura: o que entra na janela menos o que sai dela.</p>

Conferi numericamente e bate na décima primeira casa. A consequência é conhecida de quem já pôs alarme em cima da variação de uma métrica de janela: cada pico produz dois eventos, um quando entra e outro, exatamente $W$ depois, quando sai. A queda que aparece uma janela inteira depois do incidente não é o sistema melhorando, é o segundo termo de fronteira entrando na conta com sinal trocado. O gráfico está certo e a leitura é que erra, porque a intuição trata a curva como se fosse o sistema quando ela é o sistema convolvido com a janela.

O segundo é o gradiente de uma esperança, que é o que treina boa parte de machine learning moderno. Otimizar a esperança de $f(X)$ sob uma densidade $p_\theta$, em relação a $\theta$, é derivar uma integral cujo parâmetro está na densidade, e a pergunta de sempre é se dá pra empurrar a derivada pra dentro. Quando o suporte não depende de $\theta$, dá, e o que sobra é a identidade que sustenta os estimadores de gradiente por amostragem, o mesmo movimento que aparece em policy gradient:

<div class="formula">
$$ \nabla_\theta \int f(x)\,p_\theta(x)\,dx = \int f(x)\,\nabla_\theta \log p_\theta(x)\,p_\theta(x)\,dx $$
</div>
<p class="formula-nota">Essa identidade não é universal, e vale saber o que ela está cobrando: suporte independente de \(\theta\), regularidade suficiente pra trocar derivada com integral, e \(f\) sem dependência direta do parâmetro. Se o custo também depender, \(f_\theta\), aparece um segundo termo, \(\mathbb{E}[\nabla_\theta f_\theta(X)]\). A primeira das três hipóteses é a que quebra no exemplo seguinte.</p>

Conferi com $X \sim N(\mu,1)$, $f(x)=x^3$ e $\mu = 1{,}7$: a identidade e a derivada numérica dão as duas 11,67, que é o valor fechado $3(\mu^2+1)$, com erro de $5{,}3 \times 10^{-15}$ e $2{,}2 \times 10^{-10}$.

Agora o caso em que o suporte depende do parâmetro, que é onde a coisa fica interessante. Tome $X \sim \mathrm{Uniforme}(0,\theta)$ e $f(x) = x^2$. A esperança sai na mão, e a derivada dela também:

<div class="formula">
$$ \mathbb{E}[X^2] = \int_0^\theta \frac{x^2}{\theta}\,dx = \frac{\theta^2}{3} \qquad\Longrightarrow\qquad \frac{d}{d\theta}\,\mathbb{E}[X^2] = \frac{2\theta}{3} $$
</div>

Em $\theta = 3$ isso vale 2, e esse é o número a bater. Agora aplique a identidade de cima do jeito ingênuo: derive só a densidade, com $x$ fixo, esquecendo que o suporte também é função de $\theta$. No interior a densidade é $1/\theta$, então $\partial_\theta(1/\theta) = -1/\theta^2$, e a conta fecha em outro lugar:

<div class="formula">
$$ \underbrace{\int_0^\theta x^2\left(-\frac{1}{\theta^2}\right) dx}_{\text{interior}} = -\frac{\theta}{3}, \qquad \underbrace{f(\theta)\,p_\theta(\theta)}_{\text{fronteira}} = \frac{\theta^2}{\theta} = \theta, \qquad -\frac{\theta}{3} + \theta = \frac{2\theta}{3} $$
</div>
<p class="formula-nota">O interior sozinho dá \(-1\) em \(\theta = 3\): não é imprecisão, é sinal trocado. Os 3 que faltam são o termo de fronteira, o limite de cima andando junto com o parâmetro. Somados, os dois devolvem o gradiente certo.</p>

Vale desfazer uma confusão que eu mesmo já fiz aqui. É tentador culpar "autodiff ingênuo", mas o autodiff não tem opinião: ele deriva o que você entregou. Se o que você entregou foi a densidade, e você derivou ela ignorando que o domínio se move, erra. Se o que você entregou foi o programa de amostragem, $X = \theta U$ com $U \sim \mathrm{Uniforme}(0,1)$, acerta, e acerta por um motivo que é o assunto deste post: a mudança de variável $x = \theta u$ tira o parâmetro da fronteira e coloca no integrando.

<div class="formula">
$$ \mathbb{E}[f(X)] = \int_0^1 f(\theta u)\,du $$
</div>

Com os limites presos em 0 e 1, não sobra fronteira nenhuma pra esquecer, o termo interior dá conta de tudo sozinho, e derivar $f(\theta u)$ é regra da cadeia de primeiro semestre. Esse é o gradiente pathwise, o truque de reparametrização. A diferença entre ele e o score function não é esperteza de implementação: é onde cada um deixa o parâmetro. O score function deixa $\theta$ na medida, e aí a fronteira móvel vira problema dele. O pathwise empurra $\theta$ pro integrando, e o problema deixa de existir.

Esse caso é o exemplo padrão da falha na literatura. Mohamed, Rosca, Figurnov e Mnih usam a mesma $\mathrm{Uniforme}(0,\theta)$, com $f(x)=x$, no survey de estimação de gradiente por Monte Carlo, e o diagnóstico deles é mais preciso do que "esqueceu um termo": o score function assume continuidade absoluta, que $p_{\theta+h}$ seja positiva onde $p_\theta$ é, e essa hipótese quebra na borda exatamente quando o parâmetro define o suporte. Na conta deles o gradiente verdadeiro é $1/2$ e o estimador devolve $-1/2$. E quando eles refazem a mesma esperança por derivada de medida, a separação que aparece é literalmente a regra de Leibniz: $f(\theta)/\theta$ na fronteira, menos $(1/\theta^2)\int_0^\theta f$ no interior.

O terceiro é rendering diferenciável, e é o exemplo mais bonito porque a fronteira ali é literalmente uma silhueta. A cor de um pixel é uma integral, e o termo de visibilidade torna o integrando descontínuo: um ponto está atrás do objeto ou não está. A posição dessa descontinuidade depende dos parâmetros da cena, então derivar em relação à geometria produz uma contribuição concentrada na borda. Quem ignora essa contribuição consegue treinar cor e material, e não consegue mover geometria, porque o gradiente que empurraria a silhueta é justamente o que ficou de fora. O trabalho que virou referência na área ataca isso de frente, com um algoritmo de amostragem de arestas que, nas palavras dos autores em tradução minha, "diretamente amostra as funções delta de Dirac introduzidas pelas derivadas do integrando descontínuo".

Some os três e o padrão fica claro. Na integral fechada da seção anterior, esquecer a fronteira custou um pedaço da ordem do próprio integrando. No suporte móvel, custa o sinal. No rendering, custa a capacidade de otimizar geometria. O termo que ninguém precisa provar continua sendo o que mais cobra.

## O parâmetro que você inventa

A mesma regra sustenta um truque que parece mágica na primeira vez: introduzir um parâmetro que não existia no problema, só pra derivar em relação a ele. O exemplo clássico cabe em três linhas.

<div class="formula">
$$ I(a) = \int_0^1 \frac{x^a - 1}{\ln x}\,dx $$
</div>

Essa integral não tem primitiva elementar. A derivada dela tem, e é trivial: derivar sob o sinal mata o logaritmo do denominador, porque $\partial_a x^a = x^a \ln x$. Sobra $I^{\prime}(a) = \int_0^1 x^a dx = 1/(a+1)$, e como $I(0) = 0$, integrando de volta vem $I(a) = \ln(a+1)$, válido para $a > -1$. Conferi em quatro valores de $a$ e o erro fica em $1{,}1 \times 10^{-7}$ nos quatro, todo ele de quadratura junto às pontas, onde $x^a$ tem derivada de ordem alta ilimitada e o Simpson deixa de valer $O(h^4)$. Mas a troca de derivada com integral, essa não fica no ar: a integral é a seção 8 das notas do Conrad, e a tabela-resumo dele já traz as dominantes prontas. Para $0 < a < c$ vale $|f| \le (1-x^c)/\lvert\log x\rvert$ e $|\partial_a f| = x^a \le 1$, as duas integráveis em $(0,1]$. É o caso raro em que a hipótese não precisa ser negociada no olho, porque alguém já tabelou.

É esse movimento que ficou conhecido como truque de Feynman. E é aqui que o post vira outro post, de propósito. Até agora eu tratei a regra como ferramenta, e ferramenta se julga por funcionar. Daqui pra frente eu trato ela como atribuição, e atribuição se julga por ser verdadeira. A segunda pergunta tem uma resposta bem pior do que eu esperava quando comecei a procurar.

## Parte II: o que Leibniz de fato escreveu

Gottfried Wilhelm Leibniz nasceu em 1 de julho de 1646 em Leipzig e morreu em 14 de novembro de 1716 em Hannover. Ele não era matemático de formação: doutorou-se em direito em Altdorf, em fevereiro de 1667, e ganhou a vida como secretário, advogado, bibliotecário e conselheiro de corte. A matemática entrou por via diplomática. Foi a Paris em 1672 numa missão política, ficou até 1676, estudou com Christiaan Huygens no outono de 1672 e, por indicação dele, foi ler Saint-Vincent sobre soma de séries.

A notação é a parte da herança que ninguém disputa. Em 29 de outubro de 1675, num manuscrito não publicado chamado *Analyseos tetragonisticae pars secunda*, ele escreveu a frase que vale a pena ler no original: "Utile erit scribi ∫ pro omnia, ut ∫l = omn. l, id est summa ipsorum l". Será útil escrever ∫ em vez de *omnia*, isto é, a soma dos próprios $l$. O símbolo é um S alongado de *summa*, e ele nasceu como abreviação de uma palavra que Leibniz estava cansado de escrever. Duas semanas depois, em 11 de novembro de 1675, no manuscrito *Methodi tangentium inversae exempla*, aparecem $dx$, $dy$ e $dy/dx$. E um detalhe de rodapé sobre como as datas escorregam: a biografia de Leibniz no MacTutor dá 21 de novembro de 1675 para a primeira aparição de $\int f(x)dx$, enquanto a página de primeiras ocorrências de símbolos, no mesmo arquivo, data de 11 de novembro o manuscrito em que ele pela primeira vez pôs $dx$ depois do símbolo de integral, que é o mesmo evento descrito com outras palavras. As duas páginas não batem. O que dá pra dizer é que elas não têm o mesmo lastro: a segunda cita Cajori, volume 2, página 204, e a primeira não cita fonte. Isso não resolve, mas diz onde se resolve, e eu deixo o endereço: os dois manuscritos estão na edição crítica da Academia, série VII, volume 5, páginas 288 a 295 e 321 a 331.

O artigo de 1684 na *Acta Eruditorum*, o *Nova methodus pro maximis et minimis*, é a primeira publicação do cálculo diferencial. Ele traz a notação $d$ e as regras de derivada de potência, produto e quociente, e não traz demonstração nenhuma. Os resultados de cálculo integral saíram em 1684 e 1686 com o nome de *calculus summatorius*; a expressão cálculo integral foi sugestão de Jacob Bernoulli, em 1690. E o símbolo $\int$, inventado em 1675, só apareceu impresso em 1686.

A disputa de prioridade com Newton rende um parágrafo, e ele é bom. Em 1711 Leibniz leu um artigo de Keill acusando ele de plágio e recorreu à Royal Society. Newton, que era presidente da Royal Society, nomeou um comitê "imparcial" para decidir se o inventor do cálculo era ele ou Leibniz, escreveu ele mesmo o relatório oficial do comitê, sem assinar, e depois publicou uma resenha anônima do próprio relatório nas *Philosophical Transactions*. O relatório saiu como *Commercium Epistolicum* no começo de 1713, e Leibniz só viu o documento no outono de 1714.

Aqui começa a parte em que eu preciso ser chato. A continuação dessa história, do jeito que circula, é que o rancor da disputa isolou a matemática britânica por um século, e que a culpa foi de os ingleses se agarrarem aos pontinhos de Newton em vez do $d$ de Leibniz. Quem estudou o período de perto contesta. Niccolò Guicciardini, no livro que dedicou ao cálculo de fluxões na Grã-Bretanha entre 1700 e 1800, sustenta que a diferença entre a notação de Newton e a de Leibniz recebeu importância demais: as duas escolas compartilhavam um método matemático comum, com dois algoritmos que se traduziam um no outro, e passar de uma notação pra outra era trivialidade. E rastreia a imagem deprimente do cálculo newtoniano até os escritos da Analytical Society de Cambridge, no começo do século XIX, reformadores com interesse direto em pintar o passado como atrasado. A disputa não foi inofensiva. Mas a versão forte da lenda tem origem identificável e autor interessado, e a lista de matemáticos britânicos do século XVIII, com Taylor, Stirling, Bayes, Maclaurin e Simpson dentro, não parece lista de terra arrasada.

O que se afirma com tranquilidade sobre notação é mais modesto e mais interessante que a lenda: Leibniz sabia que achar boa notação era problema de primeira ordem e pensava muito nisso, enquanto Newton escrevia mais para si mesmo e usava a notação que lhe ocorria no dia. O $d$ e o $\int$ deixam explícito o aspecto de operador, e foi esse aspecto que os desenvolvimentos posteriores foram cobrar.

Agora a pergunta que me interessava, e que é a razão de este post existir: Leibniz enunciou a regra que leva o nome dele?

A resposta honesta é não, não nessa forma. O que a literatura documenta é mais estreito, e antes de eu contar o que é, o grau de certeza: eu li isso no resumo do capítulo 2 da monografia, o que o editor publica na página do livro, e não no volume impresso. Com a ressalva na mesa. Steven Engelsman, na monografia sobre a origem da diferenciação parcial a partir de problemas de famílias de curvas, situa em 1697 a descoberta e o uso, por Leibniz e Johann Bernoulli, do que ele chama teorema da permutabilidade entre derivação e integração, na forma $d_x\int \varphi(x,a) da = \int d_x \varphi(x,a) da$, com Jakob Bernoulli usando a mesma propriedade em 1698. O contexto era o problema das trajetórias ortogonais, e os dois estavam conscientes da novidade conceitual: chamaram a operação de diferenciação de curva em curva, em contraste com a derivação ordinária ao longo de uma única curva.

Olha bem o que está e o que não está nessa fórmula. Está o terceiro termo, a troca de ordem, o pedaço que é teorema de fato. Não estão os limites variáveis, não estão os dois termos de fronteira, não está hipótese nenhuma. O que Leibniz teve em 1697, pelo que a documentação sustenta, foi a permutação com limites fixos, escrita na linguagem de famílias de curvas, e usada como ferramenta para resolver um problema geométrico concreto. A regra completa que hoje leva o nome dele, com os três termos e com o retângulo de continuidade, é construção posterior de outras pessoas.

E aqui tem uma ironia de bibliografia que vale contar. As notas de Keith Conrad sobre derivação sob o sinal da integral, que são hoje a referência que todo mundo manda para quem pergunta, abrem dizendo que o método é "devido a Leibniz em 1697", e a nota de rodapé dessa afirmação aponta para uma resposta no History of Science and Mathematics Stack Exchange. Não é crítica ao Conrad, o texto dele é de matemática e é excelente. É um retrato de como funciona a atribuição em matemática: a data circula com precisão de ano, a cadeia de citação termina num fórum, e ninguém checa porque o crédito não muda a fórmula.

O rigor que hoje se exige veio depois, e veio de outro projeto. Leibniz operava com infinitesimais, quantidades menores que qualquer grandeza dada e ainda assim não nulas, e nem ele tinha certeza do estatuto delas. Numa carta a Johann Bernoulli de junho de 1698 escreve, em tradução livre minha do inglês, que talvez o infinito e o infinitamente pequeno que concebemos sejam imaginários, mas adequados para determinar coisas reais, assim como as raízes também costumam ser consideradas imaginárias. É o autor do cálculo dizendo, com elegância, que não sabe se os objetos dele existem.

A formulação moderna abandonou o infinitesimal como objeto e reconstruiu tudo em cima de limite, com Bolzano, Cauchy e Weierstrass, e foi essa reconstrução que trouxe as hipóteses. A troca de derivada com integral deixou de ser propriedade evidente e passou a exigir continuidade, convergência uniforme e, com a integral de Lebesgue, convergência dominada, que é a hipótese que dá conta do contraexemplo da seção anterior sem pedir nada além de uma cota integrável.

Fecha o círculo o Feynman, responsável pela regra ter fama de arma secreta. Em *Surely You're Joking, Mr. Feynman!*, no capítulo "A Different Box of Tools", ele conta que o professor de física do colégio, o Mr. Bader, mandou ele ficar depois da aula e deu de presente um livro, o *Advanced Calculus* do Woods, porque ele falava demais e fazia barulho por tédio. E conta o efeito: "aquele livro também mostrava como derivar parâmetros sob o sinal da integral, é uma certa operação. Acontece que isso não é muito ensinado nas universidades, elas não dão ênfase nisso". Foi com essa peça que ele construiu a fama de resolver integrais em Princeton, não por ser mais rápido, mas porque a caixa de ferramentas dele tinha algo que as outras não tinham. A regra é de 1697, o rigor é do século XIX, e a fama é de um físico que ganhou um livro de presente por ser aluno inconveniente.

O termo de fronteira é o resumo do post. É a parte da regra que ninguém precisa provar, que qualquer um deduz do TFC, e é justamente a parte que todo mundo esquece de escrever. Vale 40% da resposta no caso que eu conferi. A parte difícil você respeita, porque ela impõe hipótese e te obriga a pensar. A parte fácil você atropela, e é ela que te cobra a conta.

## Fontes

- Biografia de Leibniz, arquivo MacTutor, St Andrews: datas de nascimento e morte, doutorado em direito em Altdorf, os anos de Paris e o contato com Huygens, conteúdo do *Nova methodus* de 1684, primeira aparição impressa do ∫ em 1686, cronologia da disputa e do *Commercium Epistolicum*. [mathshistory.st-andrews.ac.uk/Biographies/Leibniz](https://mathshistory.st-andrews.ac.uk/Biographies/Leibniz/)
- Biografia de Newton, arquivo MacTutor: comitê "imparcial" da Royal Society, relatório escrito por Newton sem assinatura e resenha anônima do próprio relatório. [mathshistory.st-andrews.ac.uk/Biographies/Newton](https://mathshistory.st-andrews.ac.uk/Biographies/Newton/)
- *Earliest Uses of Symbols of Calculus*, compilação de Jeff Miller hospedada no MacTutor, citando Cajori vol. 2 p. 204: manuscrito de 29 de outubro de 1675 com a frase sobre o ∫, manuscrito de 11 de novembro de 1675 com $dx$, $dy$ e $dy/dx$, e a informação de que os dois foram publicados primeiro por Gerhardt e hoje estão na edição crítica da Academia, *Sämtliche Schriften und Briefe*, Reihe VII vol. 5, *Infinitesimalmathematik 1674-1676*, Akademie Verlag, 2008, pp. 288-295 e 321-331. [mathshistory.st-andrews.ac.uk/Miller/mathsym/calculus](https://mathshistory.st-andrews.ac.uk/Miller/mathsym/calculus/)
- *The rise of calculus*, MacTutor: postura de Leibniz e de Newton em relação a notação, *calculus summatorius*, e a sugestão do nome cálculo integral por Jacob Bernoulli em 1690. [mathshistory.st-andrews.ac.uk/HistTopics/The_rise_of_calculus](https://mathshistory.st-andrews.ac.uk/HistTopics/The_rise_of_calculus/)
- Niccolò Guicciardini, *The Development of Newtonian Calculus in Britain, 1700-1800*, Cambridge University Press, 1989: crítica à tese do declínio britânico, origem da imagem na Analytical Society de Cambridge, e a posição de que as duas escolas compartilhavam um método comum com notações traduzíveis uma na outra. Parafraseado, não citado; ver a seção seguinte.
- Steven B. Engelsman, *Families of Curves and the Origins of Partial Differentiation*, North-Holland Mathematics Studies 93, 1984: 1697 como data da descoberta e uso do teorema de permutabilidade por Leibniz e Johann Bernoulli, 1698 para Jakob Bernoulli, e o termo diferenciação de curva em curva. Conferido no resumo do capítulo 2, *Families of Curves in the 1690s*, publicado pela editora, e não no volume impresso. [sciencedirect.com/bookseries/north-holland-mathematics-studies/vol/93](https://www.sciencedirect.com/bookseries/north-holland-mathematics-studies/vol/93/suppl/C)
- Carta de Leibniz a Johann Bernoulli de 7/17 de junho de 1698, edição da Academia A III 7, 796-97, em tradução inglesa publicada pela Technion: os infinitos e infinitamente pequenos como possivelmente imaginários. [humanities.technion.ac.il](https://humanities.technion.ac.il/wp-content/uploads/2023/07/Bernoulli-Leibniz.English-2.pdf)
- Keith Conrad, *Differentiating under the integral sign*: o Teorema 12.3, com a dominação pedida só para $t$ num intervalo em volta do ponto; o Corolário 12.4, que tira a versão de limites variáveis do teorema de limites fixos mais a regra da cadeia sobre $I(t,a,b)$; a seção 8, que é a integral do truque de Feynman deste post, com as dominantes na Tabela 2; a atribuição a "Leibniz em 1697" na primeira frase, cuja nota de rodapé é a referência [4], uma resposta no History of Science and Mathematics Stack Exchange; e a referência [16], a edição de 1934 do Woods pela Ginn and Co. A epígrafe é o trecho do Feynman. [kconrad.math.uconn.edu](https://kconrad.math.uconn.edu/blurbs/analysis/diffunderint.pdf)
- Shakir Mohamed, Mihaela Rosca, Michael Figurnov e Andriy Mnih, *Monte Carlo Gradient Estimation in Machine Learning*, JMLR 21 (2020) 1-62: as condições para a troca de derivada e integral no estimador score function (seção 4.3.1), a hipótese de continuidade absoluta e o exemplo de suporte limitado com $\mathrm{Uniforme}(0,\theta)$ e $f(x)=x$, com gradiente verdadeiro $1/2$ contra $-1/2$ do estimador (seção 4.3.2), a derivação do estimador pathwise empurrando o parâmetro pro custo (seção 5.2), e a separação em termo de fronteira e termo interior na equação (41a). [jmlr.org/papers/volume21/19-346](https://jmlr.org/papers/volume21/19-346/19-346.pdf)
- Tzu-Mao Li, Miika Aittala, Frédo Durand e Jaakko Lehtinen, *Differentiable Monte Carlo Ray Tracing through Edge Sampling*, ACM Transactions on Graphics 37(6), SIGGRAPH Asia 2018: descontinuidade de visibilidade no integrando e amostragem direta das deltas de Dirac introduzidas pela derivada. A citação do parágrafo de rendering vem do resumo dos autores. [people.csail.mit.edu/tzumao/diffrt](https://people.csail.mit.edu/tzumao/diffrt/)
- Richard Feynman, *Surely You're Joking, Mr. Feynman!*, capítulo "A Different Box of Tools": o Mr. Bader, o *Advanced Calculus* do Woods, e o trecho sobre derivar parâmetros sob o sinal da integral.
- Conferência numérica de tudo que este post afirma em número: $A^{\prime}(7)$ e $A^{\prime\prime}(7)$ contra a forma fechada, o termo de fronteira esquecido valendo $F(7)$, a janela deslizante, o gradiente de esperança com suporte fixo, os cinco números da $\mathrm{Uniforme}(0,\theta)$, o contraexemplo $\int_0^\infty t e^{-tx}dx$ e a integral $\int_0^1 (x^a-1)/\ln x\,dx = \ln(a+1)$. São 21 verificações, quadratura de Simpson com 200 mil a 400 mil subintervalos somada com `math.fsum`, diferenças finitas centrais, e uma tolerância própria por método. Script em Python, só biblioteca padrão. [verificacao.py](/code/2026-09-02-termo-de-fronteira-regra-de-leibniz/verificacao.py)

## O que eu não consegui verificar

- **Se Leibniz chegou perto da forma com limites variáveis.** O que achei documentado é a permutação com limites fixos, em 1697. Nenhuma fonte que eu alcancei diz que ele tratou dos termos de fronteira nesse contexto, e nenhuma diz que ele não tratou. Fica em aberto.
- **Quem primeiro enunciou a regra na forma moderna, com hipóteses.** Não achei fonte. Sei dizer que a maquinaria veio da rigorização do século XIX e que a versão com convergência dominada é posterior a Lebesgue, mas não atribuo o primeiro enunciado a ninguém porque não sei.
- **A monografia do Engelsman e a edição Gerhardt eu não li.** A afirmação sobre 1697 vem do resumo do capítulo 2 publicado pela editora, não do volume impresso, e não fui à correspondência original. O exemplar está no Internet Archive, mas em regime de empréstimo, sem busca no texto. Quem quiser fechar essa lacuna precisa do livro na mão.
- **A formulação exata do Guicciardini.** A posição dele sobre a notação ter recebido importância demais eu confirmei em fonte secundária, e por isso ela aparece aqui como paráfrase, não entre aspas. Não tenho a página, e não vou fingir que tenho.
- **A divergência de data entre duas páginas do MacTutor**, 11 contra 21 de novembro de 1675, continua sem resolução. O que eu consegui apurar é que as duas não têm o mesmo lastro documental: a página de símbolos cita Cajori, a biografia não cita nada. Quem for atrás dos manuscritos tem o endereço na lista acima, edição da Academia, série VII volume 5.
- **Qual edição do Woods o Feynman tinha.** A bibliografia do Conrad cita a edição nova, de 1934, da Ginn and Co. O Feynman não dá edição no relato. Não sei qual era.
