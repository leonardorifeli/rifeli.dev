---
title: "Por que priorizar o fetch nativo? E como implementar timeout nas requisições"
draft: true
date: 2025-08-20T00:00:00.000Z
description: "Entenda por que o fetch nativo deve ser sua primeira escolha no Node.js e veja como implementar timeout de forma simples e eficiente."
comments: true
keywords: [
  "Node.js",
  "fetch",
  "timeout",
  "AbortController",
  "AbortSignal",
  "JavaScript",
  "backend",
  "HTTP requests",
  "resiliência",
  "boas práticas",
  "uso de fetch em nodejs",
  "como implementar timeout em nodejs",
  "como implementar timeout em fetch nodejs"
]
tags:
  - nodejs
  - fetch
  - timeout
  - código
  - nativo
---

# Introdução

<img id="image-custom" src="https://nodejs.org/static/logos/nodejsDark.svg" alt="" />
<p id="image-legend">Node.js</p>

Na Harmo, nosso codebase é bastante diverso. Sempre buscamos equilíbrio entre as linguagens, usando cada uma para aquilo que faz de melhor. Começamos nosso core em **Node.js** e, desde 2017, evoluímos muito com **Golang** (desde a versão 1.7). Hoje, também contamos com Python, Vue.js e até shell scripts para infra.

No ecossistema **Node.js** é comum haver múltiplas formas de resolver o mesmo problema. Por isso, adotamos uma diretriz clara: **sempre priorizar o que é nativo**, evitando dependências externas desnecessárias. Quando precisamos de algo mais específico, criamos pacotes privados que abstraem essa lógica, garantindo reaproveitamento e segurança.

Dessa forma, para gerir os clients back-end que fazem requisições HTTPS (internas e externas), usamos desde o Node v18 o **fetch** nativo. Porém, ele não possui uma forma "oficial” de configurar timeout. Vamos ver como contornar isso.

<img id="image-custom" src="/images/posts/nodejs-fetch/distribuicao_tecnologias.png" alt="" />
<p id="image-legend">Distribuição das linguagens no codebase da Harmo</p>

# Por que usar fetch nativo?

A primeira pergunta que sempre aparece é: *"Por que usar algo nativo e contornar essa limitação, se eu posso importar o Axios e setar `timeout` facilmente?”*.

### Pontos que pesam a favor do fetch:

- **Livre de dependências externas**: menos pacotes para atualizar, menos riscos de vulnerabilidades.
- **Adoção e padronização**: hoje é API estável, padronizada e suportada oficialmente no Node 18+.
- **API moderna**: suporta streaming, trabalha com Promises e se alinha ao padrão da Web.

### Comparativo mais amplo — fetch vs Axios

1. **Zero dependências, menos superfície de risco**
   - Nada de instalar libs só para HTTP.
   - Menos código de terceiros no deploy, menos CVEs para monitorar.

2. **Padrão da Web (WHATWG) e futuro-proof**
   - Mesma API usada em navegadores, Deno, Bun, runtimes serverless/edge.
   - Isomórfico: o mesmo código funciona em front e back.

3. **Disponível nativamente no Node 18+**
   - Já faz parte do runtime, baseado em *undici*.
   - Suporte a `AbortController` e `AbortSignal.timeout(ms)`.

4. **API moderna e composável**
   - `Request`, `Response`, `Headers` padronizados.
   - Composição simples via funções, sem precisar de interceptors acoplados.

5. **Performance e simplicidade operacional**
   - Menos camadas ⇒ overhead menor.
   - Tree-shaking natural: usa a API do runtime, não importa um bundle extra.

---

# E quando faz sentido usar Axios (ou outra lib)?

Não é sobre "nunca usar Axios”, mas sim **começar com fetch** e só adicionar uma lib se o caso justificar.

**Exemplos em que pode valer a pena:**

- Interceptors prontos para logging, métricas ou autenticação.
- Retries/backoff já implementados.
- Serialização automática de `params` e normalização de erros.
- Ambientes legados (Node < 18).
- Ergonomia de configuração (`axios.create`, defaults globais, etc.).

---

# Problema de Timeout e helpers

O **fetch** não tem uma opção `timeout` nativa no objeto de configuração.
Se você não tratar isso, uma requisição pode ficar pendurada indefinidamente, travando fluxo e degradando UX.

### Solução 1: AbortController + setTimeout

```js
async function fetchWithTimeout(url, options = {}, timeout = 5000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}
```

### Solução 2: AbortSignal.timeout (mais moderna)

```js
const response = await fetch("https://api.exemplo.com", {
  signal: AbortSignal.timeout(3000),
});
```

# Conclusão

Como trabalhamos com microsserviços e serverless, estamos sempre atualizando nosso codebase e priorizando recursos nativos.

- **O fetch nativo deve ser sempre a primeira escolha:** leve, padronizado e futuro-proof;
- **Timeout não é um problema:** com AbortController ou AbortSignal.timeout, você cobre 99% dos cenários;
- Axios e outras libs ainda têm espaço, mas só quando há uma necessidade clara (interceptors complexos, retrys prontos, ergonomia global).

# Lições aprendidas

Interessante refletir e analisar cada caso, mas o que sempre buscamos ter aqui é o básico bem feito.

- **Comece simples:** fetch nativo atende a maioria dos casos;
- **Priorize o controle:** implemente timeout sempre, mesmo em chamadas internas;
- **Reduza dependências:** cada pacote a menos significa menos riscos, menos manutenção e menos bugs;
- **Crie seus utilitários:** pequenos helpers (fetchJson, fetchWithRetry) podem substituir dezenas de linhas de configs em libs externas;
- **Padronize no time:** uma decisão simples como **“usar fetch nativo com helper padrão”** já elimina inconsistências e acelera onboarding de devs.
