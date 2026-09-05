# O termo de fronteira

Três variações para o LinkedIn. Post no blog datado 2026-09-02, a mesma data do
prefixo da URL. Link do blog no primeiro comentário. Primeira linha sempre
narrativa, nunca fórmula solta.

Primeiro comentário (qualquer variação):

> Post completo: https://rifeli.dev/blog/2026-09-02-termo-de-fronteira-regra-de-leibniz/

---

## Variação 1 — os 40% que sumiram (recomendada)

A conta dava 6,885. O valor certo era 11,385.

A diferença não era arredondamento nem erro de quadratura. Era um termo inteiro que eu tinha deixado de escrever. Quase 40% da resposta desapareceu porque a derivada de uma integral tem três pedaços e eu só tinha somado dois.

O pedaço esquecido tem nome: termo de fronteira. Ele aparece quando os limites da integral se movem junto com a variável que você está derivando, e a ironia é que ele é a parte fácil da regra. A parte difícil, a troca de derivada com integral lá dentro, exige hipótese, te obriga a pensar, e por isso você respeita. A parte fácil você atropela.

E ela não perdoa. Peguei o caso mais comum de computação que existe, um agregado de janela deslizante, desses que todo sistema de observabilidade calcula. Soma dos últimos W minutos é uma integral com os dois limites andando junto com o tempo. Faz a conta e o resultado é curioso: a derivada é só fronteira, o que entra na janela menos o que sai dela.

Isso explica um fantasma que quem opera produção conhece. Cada pico gera dois eventos na variação da métrica, um quando entra na janela e outro, exatamente uma janela depois, quando sai. Aquela queda que aparece W minutos depois do incidente não é o sistema melhorando. É o segundo termo de fronteira entrando na conta com sinal trocado. O gráfico está certo, a leitura é que erra.

Escrevi um post inteiro sobre esse termo, com a derivação a partir da regra da cadeia, o erro medido numericamente, e três lugares de computação onde ele decide o resultado. Link no primeiro comentário.

#Matematica #Calculo #Observabilidade #Engenharia #DataScience

---

## Variação 2 — onde isso quebra machine learning

Existe um erro de cálculo que troca o sinal do seu gradiente e não levanta nenhum alarme.

Ele acontece quando você deriva uma esperança cujo suporte depende do parâmetro. Exemplo mínimo, que dá pra conferir em dez linhas de Python: X uniforme entre 0 e teta, e você quer a derivada do valor esperado de X ao quadrado em relação a teta.

A resposta certa em teta igual a 3 é 2. Derivar só a densidade, que é o que a regra da cadeia enxerga quando você diferencia o código de amostragem sem olhar o domínio, entrega menos 1.

Não é imprecisão. É sinal trocado e 150% de erro. O que falta é o termo de fronteira, o efeito de o próprio domínio esticar quando o parâmetro cresce.

Quando o suporte não depende do parâmetro, a troca de derivada com integral vale e cai naquela identidade que sustenta os estimadores de gradiente por amostragem, o mesmo movimento que aparece em policy gradient. Quando o suporte depende, você precisa da fronteira, e a saída conhecida é reescrever a amostragem pra tirar o parâmetro dos limites e jogar pro integrando. É exatamente isso que o truque de reparametrização faz. Ele não é esperteza de implementação, é uma mudança de variável que move o parâmetro de onde a regra é traiçoeira pra onde ela é bem comportada.

O mesmo fenômeno aparece em rendering diferenciável, e ali a fronteira é literalmente uma silhueta: quem ignora a contribuição da borda treina cor e material e não consegue mover geometria.

Três aplicações, os números conferidos, e a derivação inteira no post. Link no primeiro comentário.

#MachineLearning #Calculo #Matematica #DataScience #Engenharia

---

## Variação 3 — a regra de Leibniz não é de Leibniz

Fui atrás de uma coisa simples: confirmar que Leibniz tinha enunciado a regra que leva o nome dele. Não tinha.

O que a documentação sustenta é bem mais estreito. Em 1697, ele e Johann Bernoulli descobriram e usaram a troca de ordem entre derivada e integral, com limites fixos, na linguagem de famílias de curvas, pra resolver um problema geométrico concreto. Está lá o terceiro termo, o pedaço que é teorema de fato. Não estão os limites variáveis, não estão os dois termos de fronteira, não está hipótese nenhuma. A regra completa que hoje leva o nome dele é construção posterior de outras pessoas.

E tem uma ironia de bibliografia que vale sozinha o parágrafo. As notas que hoje são a referência padrão do assunto abrem dizendo que o método é devido a Leibniz em 1697, e a nota de rodapé dessa afirmação aponta para uma resposta de fórum. Não é crítica ao autor, o texto de matemática dele é excelente. É um retrato de como a atribuição funciona: a data circula com precisão de ano, a cadeia de citação termina num fórum, e ninguém checa, porque o crédito não muda a fórmula.

De brinde, a disputa com Newton é pior do que a versão que costuma circular. Newton, que presidia a Royal Society, nomeou um comitê imparcial pra decidir se o inventor do cálculo era ele ou Leibniz, escreveu ele mesmo o relatório oficial do comitê sem assinar, e depois publicou uma resenha anônima do próprio relatório.

Já a lenda de que isso isolou a matemática britânica por um século é contestada por quem estudou o período de perto, e o post explica por quê, com fonte.

Escrevi tudo isso junto com a matemática, e separei numa seção final o que eu não consegui verificar. Link no primeiro comentário.

#HistoriaDaCiencia #Matematica #Calculo #Pesquisa #Ciencia

---

## Notas operacionais

- Recomendada: Variação 1. Abre com dois números e uma perda concreta, que é o
  gancho mais forte do post, e amarra rápido num problema de produção que a
  audiência de engenharia reconhece. É a que melhor converte em clique.
- Variação 2 é a de audiência mais técnica e a de maior chance de comentário
  qualificado, porque o exemplo do sinal trocado é conferível em dez linhas e
  gente de ML vai querer discutir reparametrização.
- Variação 3 é a de maior alcance bruto. História com escândalo acadêmico
  circula muito, e o gancho da atribuição errada é forte. Cuidado: ela vende
  menos a matemática, então é a melhor pra alcance e a pior pra atrair leitor
  que vai realmente ler a derivação.
- Não afirmar que Leibniz não chegou perto da forma com limites variáveis. O
  post diz que não achou documentação nos dois sentidos e deixa em aberto. A
  variação 3 está redigida assim de propósito, manter.
- Não nomear o autor das notas de referência na variação 3. No post ele está
  nomeado e creditado com elogio, o que é justo no formato longo. No formato
  curto do LinkedIn, nomear sem o contexto inteiro vira alfinetada.
- Os números conferidos e citáveis: 6,885 contra 11,385, diferença de 4,5 exatos
  e 39,5% da resposta; suporte móvel com sinal trocado e 150% de erro. Todos
  reproduzidos numericamente e descritos no post.
- Primeira linha narrativa, nunca fórmula. Link no primeiro comentário.
  Hashtags no fim, 5. Sem emoji, sem travessão.
