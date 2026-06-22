# As oito famílias de matemática que rodam por trás da Harmo

Três variações para o LinkedIn. Post no blog datado 2026-06-26. Continuação do post do alpinista no nevoeiro. Link do blog no primeiro comentário. Primeira linha sempre narrativa, nunca bloco de código.

Primeiro comentário (qualquer variação):

> Post completo: https://rifeli.dev/blog/2026-06-26-formulas-essenciais-data-science-harmo/

---

## Variação 1 — continuação do alpinista / cheatsheet em produção (recomendada)

Tem um cheatsheet clássico de data science circulando com oito caixas de fórmulas. A reação mais comum de quem bate o olho é "isso é coisa de pesquisador, eu só faço CRUD". Mas as oito moram em produção, todo dia.

Processamos 10 milhões de pesquisas, 1 milhão de eventos de performance de loja e 300 mil avaliações públicas por mês, em mais de 60 mil lojas físicas. Nada disso roda sem matemática trabalhando no background, mesmo quando o time que opera não chama as coisas por esses nomes.

Estatística descritiva separa "achismo de loja" de "leitura de loja". Álgebra linear e cálculo são o motor do NLP que classifica sentimento de avaliação em escala, com a mesma derivada parcial de Cálculo II que vira retropropagação. Séries temporais disparam os alarmes operacionais via moving average e z-score. Probabilidade e information theory sustentam decisão sob incerteza, de churn a detecção de avaliação falsa.

No post anterior mostrei que uma única ferramenta, o gradiente descendente, sustenta toda IA moderna. Aqui o quadro é maior: cada caixa do cheatsheet tem aplicação concreta. A diferença entre o aluno que aproveita isso na carreira e o que não aproveita é só saber onde olhar.

O mapa inteiro, família por família, no blog. Link no primeiro comentário.

#DataScience #MachineLearning #Matematica #NLP #Engenharia

---

## Variação 2 — Correlação de Ouro / reputação é performance (C-level e champion)

Cada 0,1 estrela a mais na nota média do Google se associa, em média, a 8,8% a mais de pedidos de rota. Esse número tem nome aqui dentro: Correlação de Ouro. E é só estatística descritiva.

A fórmula é a correlação de Pearson, primeira página de qualquer livro de estatística. O valor não está na fórmula, está na aplicação: descobrir esse ponto numa amostra grande de lojas, validar que ele se mantém em diferentes segmentos de varejo, e sustentar ele dentro de uma reunião com o CFO do cliente como bússola de investimento.

É isso que transforma reputação de assunto de imagem em assunto de performance. Não é "a loja parece melhor avaliada". É "cada décimo de estrela tem retorno mensurável em fluxo na porta". Reputação não é imagem, é performance, e a matemática é o que sustenta a afirmação dentro de uma sala onde todo número é questionado.

E a estatística descritiva não para na Correlação de Ouro. Média e desvio padrão pra achar a loja que destoa da rede. Variância pra saber quando uma diferença é sinal e não ruído. Valor esperado pra ancorar decisão de investimento em escala de milhares de lojas.

As oito famílias de matemática que sustentam a operação no rifeli.dev. Link nos comentários.

#DataScience #Varejo #Reputacao #Estatistica #DriveToStore

---

## Variação 3 — insight / matemática disfarçada

Você provavelmente roda z-score, moving average e probabilidade condicional em produção sem chamar nenhum deles pelo nome.

É o caso mais comum. O threshold de alarme que dispara "quando o valor está muito fora do normal" é um z-score. A regra que compara o valor de hoje com a média dos últimos 7 dias é moving average, é literalmente o que faz o robô diário de custo AWS abrir task automática aqui. A regra de negócio que estima risco de churn a partir do histórico do cliente é Bayes atualizando crença com evidência. A métrica de dashboard que "suaviza" a previsão é exponential smoothing.

O cheatsheet de data science tem oito caixas, e a leitura útil dele não é "preciso decorar tudo pra fazer data science". É que cada família já aparece no seu dia a dia, disfarçada de regra de negócio, de threshold, de métrica de painel. Information theory parece esotérica até o momento em que você precisa escolher features entre centenas de candidatas, e aí vira a única coisa que funciona em escala.

Mapeei onde cada uma das oito famílias mora na operação da Harmo, do NLP ao alarme operacional. Link no primeiro comentário.

#DataScience #MachineLearning #SRE #Matematica #Engenharia

---

## Notas operacionais

- Recomendada: Variação 1. Número absoluto cedo e aprovado (10M pesquisas, 60k lojas), amarra com o post do alpinista no nevoeiro, fecha na lição "saber onde olhar".
- Variação 2 é a de maior alcance comercial: Correlação de Ouro (+0,1 estrela = +8,8% pedidos de rota) e a bandeira "reputação é performance". Boa pra audiência C-level e champion. Todos os números usados estão na lista aprovada pra uso externo.
- Variação 3 carrega o insight da "matemática disfarçada", boa pra engenheiro/SRE sênior.
- Todos os números de volume e a Correlação de Ouro são os aprovados pra uso externo. Não trocar por médias não aprovadas.
- A pergunta de fechamento do post no blog é genuína e específica (qual das oito famílias você aplica sem ver como matemática), então aqui o CTA pode ser essa pergunta, não fórmula vazia.
- Primeira linha narrativa. Link no primeiro comentário. Hashtags no fim, 4 a 5. Sem emoji, sem travessão.
