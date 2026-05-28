# IRSA vs Pod Identity no EKS: diferenças, armadilhas e um bug silencioso que me custou duas horas

Três variações para o LinkedIn. Mesmo título do post no blog. Link do blog no primeiro comentário.

---

## Variação 1 — war story / abertura forte

```
AccessDeniedException: User: anonymous is not authorized to perform: secretsmanager:GetSecretValue
```

Migração de IRSA pra Pod Identity num cluster EKS antigo da Harmo. Fiz tudo certo: nova role, associação via CLI, removi a annotation antiga. Rollout. Veio essa mensagem.

"User: anonymous". Ou seja, o pod fazendo a chamada sem credencial nenhuma. Não era problema de permissão da role, era problema de não ter role nenhuma injetada.

Quarenta minutos travado checando trust policy, associação, Service Account, logs. Tudo certo. O incidente todo, contando rollback e revalidação, comeu duas horas. Quando achei, a resposta era óbvia: o EKS Pod Identity Agent não estava instalado no cluster. Cluster antigo, criado antes do Pod Identity existir, addon nunca foi adicionado. Sem o agent rodando como DaemonSet, ninguém intercepta a chamada do SDK, e o pod cai pra modo anonymous.

A mensagem da AWS não dá pista nenhuma disso. "anonymous" parece problema de trust, não de infraestrutura ausente.

Lição operacional: erro de AccessDenied no EKS pede checagem de camadas, não só de permissão. "User: anonymous" é credencial ausente, não permissão insuficiente. Trate como problema de infraestrutura até prova em contrário.

Detalhamento completo, com a tabela comparativa IRSA vs Pod Identity e o comando que resolve o bug, no rifeli.dev. Link no primeiro comentário.

#EKS #Kubernetes #AWS #SRE #CloudNative

---

## Variação 2 — escala / contexto Harmo

Mais de 50 microservices em Go rodando em EKS na Harmo. Atendem 10 milhões de pesquisas e 300 mil avaliações públicas por mês. Cada um precisa de credencial AWS pra acessar S3, Secrets Manager, SQS, DynamoDB, o que for.

Por anos, IRSA foi a resposta: IAM Role atrelada a Service Account via OIDC, e fim. Em 2023 a AWS lançou Pod Identity, que faz a mesma coisa de forma mais simples. Hoje os dois coexistem em produção, e a dúvida de qual usar aparece em cluster novo e em qualquer conversa de migração.

Recomendação pragmática depois de configurar, quebrar e migrar entre os dois nos últimos meses:

:: Cluster novo: Pod Identity. Trust policy simples, menos peças móveis.
:: Cluster antigo com IRSA funcionando: não migre só por migrar. O valor marginal é limitado.
:: Role compartilhada entre vários clusters: Pod Identity ganha por muito. Com IRSA, cada OIDC provider entra na trust policy, vira lista enorme.
:: Multi-cloud ou OIDC externo: IRSA. Pod Identity é AWS-only.

E uma armadilha que me custou duas horas num cluster antigo: Pod Identity depende de addon instalado no cluster. Sem isso, o pod cai em modo anonymous e a mensagem de erro da AWS não te dá pista nenhuma disso.

Post completo no rifeli.dev. Link no primeiro comentário.

#EKS #AWS #Kubernetes #CloudArchitecture #Harmo

---

## Variação 3 — insight contra-intuitivo / lição central

`User: anonymous is not authorized` no EKS quase nunca é o que parece.

O reflexo é olhar pra permissão da role, conferir trust policy, checar se a Service Account está certa. Tudo o que tem cara de "AccessDenied" no IAM. E em alguns casos é isso mesmo.

Mas quando a mensagem diz `User: anonymous`, o problema raramente é permissão insuficiente. É credencial ausente. O pod fez a chamada sem nenhuma identidade injetada, e o AWS responde como se um stranger qualquer estivesse batendo na porta.

A diferença é grande na hora de debugar. Permissão insuficiente é problema de IAM. Credencial ausente é problema de infraestrutura do cluster: token mal projetado, webhook mutating ausente, OIDC provider não registrado, ou (foi o meu caso esses dias) o EKS Pod Identity Agent simplesmente não instalado no cluster.

Pensa numa catraca com leitor de crachá não instalado. Você passa o crachá e a mensagem é "acesso negado". O reflexo é pensar que seu crachá perdeu permissão, e você gasta uma hora investigando o cadastro. Mas o leitor não existe naquele andar, então qualquer crachá vai cair na mesma mensagem genérica. A pista estava num andar acima do que eu estava investigando.

Lição que vale registrar: erro de AccessDenied no EKS pede checagem de camadas, não só de permissão. Trate "User: anonymous" como infraestrutura ausente até prova em contrário.

War story completa e comparação IRSA vs Pod Identity no rifeli.dev. Link no primeiro comentário.

#EKS #Kubernetes #AWS #DevOps #Engineering

---

## Notas operacionais

- Recomendo Variação 1 como primária: war story curta com a mensagem de erro logo no topo, fecha com a lição operacional. Padrão que performou bem no post do Aurora.
- Variação 2 puxa pelo lado de escala Harmo + decisão técnica. Boa pra audiência C-level / champion que quer recomendação pragmática.
- Variação 3 é a mais cirúrgica tecnicamente, leitor SRE / DevOps sênior. Carrega a analogia da catraca como hook didático.
- Link no primeiro comentário em até 60 segundos da publicação.
