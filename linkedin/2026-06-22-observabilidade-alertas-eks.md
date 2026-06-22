# Observabilidade e alertas no EKS: fechando o loop

Três variações para o LinkedIn. Post no blog datado 2026-06-22. Link do blog no primeiro comentário. Primeira linha sempre narrativa, nunca bloco de código.

Primeiro comentário (qualquer variação):

> Post completo: https://rifeli.dev/blog/2026-06-22-observabilidade-alertas-eks/

---

## Variação 1 — war story / fadiga de alerta (recomendada)

Em 6 meses uma operação acumula 200 alertas. Metade é falso positivo. E no dia que o alerta verdadeiro chega, ele some no meio do ruído.

Esse é o caminho natural de quase toda operação. Você começa com poucos alertas, eles avisam bem, você ganha confiança e vai adicionando mais. Quando percebe, desligou o celular no fim de semana porque ele não para de vibrar por coisa que não exige ação nenhuma.

A regra que adotamos pra operar o cluster EKS da Harmo é dura de propósito: alerta só existe se tem ação humana associada e precisa acontecer agora. Se a ação pode esperar o horário comercial, não é alerta, é uma task no board. Se não tem ação ("a CPU subiu"), não é alerta, é métrica no dashboard.

Na prática isso virou três camadas. Disponibilidade que acorda gente de madrugada, com runbook e SLA. Anomalia que chega no Slack sem on-call. Saúde técnica que vira task semanal. Cada coisa no canal certo, e o canal certo importa tanto quanto o alerta.

Esse é o último post da série cloud-native: a camada que transforma "consegui consertar" em "vou ver chegar da próxima vez". Stack de métricas, estratégia de log e a filosofia de alerta inteira no blog. Link no primeiro comentário.

#EKS #SRE #Observability #Kubernetes #CloudNative

---

## Variação 2 — insight contrário / menos alerta é mais alerta

Quase todo time acha que observabilidade boa é ter muito alerta. É o contrário. Menos alerta é mais alerta.

O raciocínio é simples quando você inverte a pergunta. Não é "o que eu consigo monitorar?", é "o que exige um humano agindo agora?". Tudo que não passa nesse filtro não é alerta. É dashboard pra olhar quando quiser, ou task pra resolver no ritmo certo. Misturar as três coisas no mesmo canal de alerta é como construir a própria cegueira.

A regra que seguimos no EKS da Harmo separa em três camadas:

:: Disponibilidade. API em 5xx acima do baseline, latência de commit no banco fora do patamar, cluster sem nó pronto. Acorda gente, tem runbook, tem postmortem.
:: Anomalia. Custo diário acima da baseline, erro acima do normal mas abaixo do crítico. Vai pro Slack, sem on-call. Se três aparecem juntos, muda de gravidade.
:: Saúde técnica. Índice sem uso há 30 dias, CVE alto, certificado vencendo. Vira task semanal, nunca alerta real.

Detalhe não negociável: todo alerta que pagina tem link de runbook no annotation. Alerta sem runbook é alerta novo, e alerta novo nunca deveria chegar numa pessoa que não sabe o que fazer.

Filosofia completa e os exemplos de regra no Prometheus no blog. Link nos comentários.

#SRE #Observability #EKS #DevOps #Prometheus

---

## Variação 3 — fechamento de série / loop fechado

Seis posts sobre cloud-native operado de verdade, e o que fecha todos eles não é ferramenta cara. É loop fechado.

A série passou por crise de performance no Aurora, batch inserts, IRSA e Pod Identity, relatório de custo e concorrência em Go. Cada post resolveu um problema. Observabilidade é o que liga eles: cada incidente vira a métrica ou o alerta que teria avisado antes.

A crise do Aurora? Alerta em latência de commit e em índice sem uso teria pego a deterioração antes do pico. O loop improdutivo que multiplicou a conta AWS? Anomalia de custo já é alerta estruturado hoje. O worker pool em Go? Expor goroutines ativas e queue length torna o pool observável. Cada deixa dos posts anteriores virou um sensor.

A lição que sobrou: um stack simples e bem usado bate um stack sofisticado e abandonado. Operação boa é repetível, e repetível é o que você consegue explicar pra alguém que entrou no time ontem.

Como cada post da série fecha o loop, com os exemplos de regra no Prometheus, no rifeli.dev. Link no primeiro comentário.

#CloudNative #SRE #EKS #Kubernetes #Observability

---

## Notas operacionais

- Recomendada: Variação 1. Número absoluto cedo (200 alertas em 6 meses), dor concreta da fadiga de alerta, fecha na regra forte.
- Variação 2 carrega o insight contrário ("menos alerta é mais alerta") e usa marcador :: pras três camadas. Boa pra audiência SRE/sênior.
- Variação 3 amarra a série inteira, boa se publicada como encerramento e linkando os posts anteriores.
- Primeira linha narrativa, nunca bloco de código. Link no primeiro comentário em até 60 segundos. Hashtags no fim, 4 a 5. Sem emoji, sem travessão.
- O CTA do post no blog ainda tem emoji e "Conta nos comentários" formulaico (contraria a régua). Vale alinhar antes de divulgar.
