#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação numérica das afirmações do post "O termo de fronteira".

    https://rifeli.dev/blog/2026-09-02-termo-de-fronteira-regra-de-leibniz/

Só biblioteca padrão. Roda com `python3 verificacao.py`, imprime uma linha por
verificação com método, discretização, valor esperado, valor obtido, erro
absoluto e tolerância, e sai com código diferente de zero se qualquer erro
passar da tolerância daquele método.

As tolerâncias são separadas por método porque os métodos têm regimes de erro
diferentes, e uma tolerância única esconderia justamente o que o post afirma:
que os erros da tabela são do método numérico, não da fórmula. Cada constante
TOL_* abaixo traz a conta que a justifica.

Métodos usados:

  - Quadratura de Simpson composta, somada com math.fsum para que o erro de
    arredondamento não cresça com o número de subintervalos.
  - Diferença central de primeira ordem, erro O(h²) mais arredondamento O(eps/h).
  - Diferença central de segunda ordem, erro O(h²) mais arredondamento
    O(eps/h²), que é o termo que domina quando h encolhe demais.
"""

import math
import sys

# --- Tolerâncias, uma por método ------------------------------------------

# Identidade algébrica avaliada em ponto flutuante: só arredondamento.
TOL_EXATA = 1e-12

# Simpson composto sobre integrando suave, com n na casa de 10^5. O erro de
# truncamento (b-a)^5/(180 n^4) * max|f''''| fica abaixo de 10^-18; o piso real
# é o arredondamento da soma, que com fsum fica na ordem de eps * |resultado|.
TOL_QUADRATURA = 1e-11

# Diferença central com h = 1e-5. Truncamento h²/6 * |f'''| ~ 1e-11 * |f'''|,
# arredondamento eps * |f| / h ~ 2.2e-16 * 60 / 1e-5 ~ 1.3e-9. Domina o
# arredondamento; 5e-8 dá quase duas ordens de folga.
TOL_DIF_PRIMEIRA = 5e-8

# Diferença segunda com h = 1e-3. Truncamento h²/12 * |f''''| e arredondamento
# 4 eps |f| / h² ~ 5e-8. O h maior é proposital: com h = 1e-5 o arredondamento
# explodiria para 4 eps |f| / 1e-10 ~ 5e-4. É essa troca que explica as três
# ordens de grandeza entre as duas linhas da tabela do post.
TOL_DIF_SEGUNDA = 1e-5

# Integral imprópria truncada em x = 40/t: a cauda descartada vale e^-40 ~ 4e-18.
TOL_IMPROPRIA = 1e-9

# Simpson perto de extremo com derivada de ordem alta ilimitada (x^a com a < 2
# tem segunda derivada infinita em 0). O erro deixa de ser O(h^4) e passa a ser
# governado pelos poucos subintervalos junto às pontas.
TOL_ENDPOINT = 1e-6


# --- Máquina numérica ------------------------------------------------------

def simpson(f, a, b, n):
    """Simpson composto em n subintervalos (n é forçado a par).

    A soma vai em math.fsum de propósito. Somando ingenuamente 4*10^5 termos, o
    erro de arredondamento acumulado chegaria perto de 1e-12, e ele reaparece
    multiplicado por 4/h² na diferença segunda, contaminando a linha de A''(7).
    """
    if n % 2:
        n += 1
    h = (b - a) / n
    termos = [f(a), f(b)]
    termos.extend(4.0 * f(a + i * h) for i in range(1, n, 2))
    termos.extend(2.0 * f(a + i * h) for i in range(2, n, 2))
    return h / 3.0 * math.fsum(termos)


def derivada_central(g, t, h):
    """(g(t+h) - g(t-h)) / 2h."""
    return (g(t + h) - g(t - h)) / (2.0 * h)


def derivada_segunda_central(g, t, h):
    """(g(t+h) - 2g(t) + g(t-h)) / h²."""
    return (g(t + h) - 2.0 * g(t) + g(t - h)) / (h * h)


# --- Coleta de resultados --------------------------------------------------

RESULTADOS = []


def registrar(nome, metodo, discretizacao, esperado, obtido, tolerancia):
    erro = abs(obtido - esperado)
    RESULTADOS.append({
        "nome": nome,
        "metodo": metodo,
        "discretizacao": discretizacao,
        "esperado": esperado,
        "obtido": obtido,
        "erro": erro,
        "tolerancia": tolerancia,
        "passou": erro <= tolerancia,
    })
    return erro


# --- 1 e 2. O acumulador com memória logarítmica ---------------------------
#
#   A(t) = A0 + integral de 0 a t de F(tau) * log2(2 + t - tau) dtau
#
# com F(tau) = 1 + tau/2 e t = 7. O parâmetro aparece no limite superior e
# dentro do núcleo, que é o caso completo da regra de Leibniz.

T_ALVO = 7.0
N_ACUMULADOR = 400_000
H_PRIMEIRA = 1e-5
H_SEGUNDA = 1e-3
C = 1.0 / math.log(2.0)


def F(tau):
    return 1.0 + tau / 2.0


def dF(_tau):
    return 0.5


def A(t):
    """A(t) com A0 = 0. O A0 não muda derivada nenhuma."""
    return simpson(lambda tau: F(tau) * math.log2(2.0 + t - tau), 0.0, t, N_ACUMULADOR)


def A_linha_leibniz(t):
    """F(t) + c * integral de F(tau)/(2 + t - tau).

    Primeiro termo: fronteira, g(t, b(t)) b'(t), que aqui vale F(t) porque o
    núcleo vale 1 na diagonal. Segundo termo: interior.
    """
    fronteira = F(t)
    interior = C * simpson(lambda tau: F(tau) / (2.0 + t - tau), 0.0, t, N_ACUMULADOR)
    return fronteira + interior


def A_linha_sem_fronteira(t):
    """A conta errada do post: só o termo interior."""
    return C * simpson(lambda tau: F(tau) / (2.0 + t - tau), 0.0, t, N_ACUMULADOR)


def A_duas_linhas_leibniz(t):
    """F'(t) + c [ F(t)/2 - integral de F(tau)/(2 + t - tau)² ].

    Leibniz aplicado uma segunda vez sobre a integral que sobrou. O F(t)/2 é o
    novo termo de fronteira, o núcleo 1/(2+t-tau) avaliado na diagonal.
    """
    interior = simpson(lambda tau: F(tau) / (2.0 + t - tau) ** 2, 0.0, t, N_ACUMULADOR)
    return dF(t) + C * (F(t) / 2.0 - interior)


def A_linha_fechada(t):
    """Forma fechada, pela substituição u = 2 + t - tau.

    Com F(tau) = 1 + tau/2 e t = 7, u vai de 2 a 9 e F = (11 - u)/2, então
    a integral interior é (11 ln(9/2) - 7)/2.
    """
    assert t == 7.0, "a forma fechada abaixo foi derivada para t = 7"
    interior = (11.0 * math.log(9.0 / 2.0) - 7.0) / 2.0
    return F(t) + C * interior


def A_duas_linhas_fechada(t):
    """Idem para a segunda derivada: a integral vale (77/18 - ln(9/2))/2."""
    assert t == 7.0, "a forma fechada abaixo foi derivada para t = 7"
    interior = (77.0 / 18.0 - math.log(9.0 / 2.0)) / 2.0
    return dF(t) + C * (F(t) / 2.0 - interior)


def verificar_acumulador():
    exata_primeira = A_linha_fechada(T_ALVO)
    exata_segunda = A_duas_linhas_fechada(T_ALVO)

    leibniz_primeira = A_linha_leibniz(T_ALVO)
    leibniz_segunda = A_duas_linhas_leibniz(T_ALVO)
    numerica_primeira = derivada_central(A, T_ALVO, H_PRIMEIRA)
    numerica_segunda = derivada_segunda_central(A, T_ALVO, H_SEGUNDA)

    registrar(
        "A'(7), fórmula de Leibniz contra forma fechada",
        "Simpson", f"n={N_ACUMULADOR}",
        exata_primeira, leibniz_primeira, TOL_QUADRATURA,
    )
    registrar(
        "A'(7), diferença central contra forma fechada",
        "diferença central", f"h={H_PRIMEIRA:g}, n={N_ACUMULADOR}",
        exata_primeira, numerica_primeira, TOL_DIF_PRIMEIRA,
    )
    registrar(
        "A''(7), fórmula de Leibniz contra forma fechada",
        "Simpson", f"n={N_ACUMULADOR}",
        exata_segunda, leibniz_segunda, TOL_QUADRATURA,
    )
    registrar(
        "A''(7), diferença segunda contra forma fechada",
        "diferença segunda", f"h={H_SEGUNDA:g}, n={N_ACUMULADOR}",
        exata_segunda, numerica_segunda, TOL_DIF_SEGUNDA,
    )

    # O número que abre o post: o que a omissão do termo de fronteira custa.
    # A diferença tem que ser F(7) = 4,5 exatos, e não uma sobra qualquer.
    esquecido = A_linha_leibniz(T_ALVO) - A_linha_sem_fronteira(T_ALVO)
    registrar(
        "termo de fronteira esquecido em A'(7) vale F(7)",
        "diferença de duas quadraturas", f"n={N_ACUMULADOR}",
        F(T_ALVO), esquecido, TOL_QUADRATURA,
    )

    return {
        "numerica_primeira": numerica_primeira,
        "leibniz_primeira": leibniz_primeira,
        "numerica_segunda": numerica_segunda,
        "leibniz_segunda": leibniz_segunda,
        "sem_fronteira": A_linha_sem_fronteira(T_ALVO),
        "exata_primeira": exata_primeira,
        "exata_segunda": exata_segunda,
    }


# --- 3. Janela deslizante --------------------------------------------------
#
#   A(t) = integral de t-W a t de f(tau) dtau   =>   A'(t) = f(t) - f(t-W)
#
# Os dois limites andam, o integrando não depende de t: fronteira pura.

W_JANELA = 3.0
T_JANELA = 4.2
N_JANELA = 200_000
H_JANELA = 1e-5


def sinal(tau):
    """Um sinal qualquer, suave e sem simetria que possa mascarar erro."""
    return math.sin(tau) + tau * tau / 10.0 + math.exp(-tau)


def verificar_janela():
    janela = lambda t: simpson(sinal, t - W_JANELA, t, N_JANELA)
    esperado = sinal(T_JANELA) - sinal(T_JANELA - W_JANELA)
    obtido = derivada_central(janela, T_JANELA, H_JANELA)
    registrar(
        "janela deslizante: A'(t) = f(t) - f(t-W)",
        "diferença central", f"h={H_JANELA:g}, n={N_JANELA}, W={W_JANELA:g}",
        esperado, obtido, TOL_DIF_PRIMEIRA,
    )
    return esperado, obtido


# --- 4. Gradiente de esperança com suporte fixo ----------------------------
#
#   X ~ N(mu, 1), f(x) = x³.  E[f(X)] = mu³ + 3mu, logo d/dmu = 3(mu² + 1).
#
# Suporte independente do parâmetro: a identidade do score function vale.

MU = 1.7
N_NORMAL = 200_000
H_NORMAL = 1e-5
RAIO_NORMAL = 12.0  # 12 desvios: a cauda descartada é da ordem de 1e-32


def densidade_normal(x, mu):
    return math.exp(-0.5 * (x - mu) ** 2) / math.sqrt(2.0 * math.pi)


def verificar_suporte_fixo():
    esperanca = lambda mu: simpson(
        lambda x: x ** 3 * densidade_normal(x, mu),
        mu - RAIO_NORMAL, mu + RAIO_NORMAL, N_NORMAL,
    )
    # score de N(mu,1): d/dmu log p = (x - mu)
    score = simpson(
        lambda x: x ** 3 * (x - MU) * densidade_normal(x, MU),
        MU - RAIO_NORMAL, MU + RAIO_NORMAL, N_NORMAL,
    )
    numerica = derivada_central(esperanca, MU, H_NORMAL)
    fechada = 3.0 * (MU * MU + 1.0)

    registrar(
        "E[X³] sob N(mu,1): identidade do score contra forma fechada",
        "Simpson", f"n={N_NORMAL}, mu={MU:g}",
        fechada, score, TOL_QUADRATURA,
    )
    registrar(
        "E[X³] sob N(mu,1): derivada numérica contra forma fechada",
        "diferença central", f"h={H_NORMAL:g}, n={N_NORMAL}",
        fechada, numerica, TOL_DIF_PRIMEIRA,
    )
    return fechada, score, numerica


# --- 5. Suporte que depende do parâmetro -----------------------------------
#
#   X ~ Uniforme(0, theta), f(x) = x².  E[f(X)] = theta²/3, gradiente 2theta/3.
#
# Aqui a fronteira é o parâmetro. Três contas separadas:
#   interior  = integral de 0 a theta de f(x) * d_theta(1/theta) dx = -theta/3
#   fronteira = f(theta) p_theta(theta) = theta
#   soma      = 2theta/3, que é o gradiente verdadeiro
# e, por outro caminho, o pathwise: x = theta*u com u ~ U(0,1) leva a
# E[f(X)] = integral de 0 a 1 de f(theta u) du, com limites fixos.

THETA = 3.0
N_UNIFORME = 200_000
H_UNIFORME = 1e-5


def verificar_suporte_movel():
    verdadeiro = 2.0 * THETA / 3.0

    esperanca = lambda th: simpson(lambda x: x * x / th, 0.0, th, N_UNIFORME)
    numerica = derivada_central(esperanca, THETA, H_UNIFORME)

    # Aplicação ingênua do score function: deriva só a densidade no interior,
    # com d_theta(1/theta) = -1/theta², e ignora que o suporte se move.
    interior = simpson(lambda x: x * x * (-1.0 / (THETA * THETA)), 0.0, THETA, N_UNIFORME)
    fronteira = (THETA ** 2) * (1.0 / THETA)  # f(theta) * p_theta(theta)

    # Pathwise: o parâmetro sai da fronteira e vai pro integrando.
    reparametrizada = lambda th: simpson(lambda u: (th * u) ** 2, 0.0, 1.0, N_UNIFORME)
    pathwise = derivada_central(reparametrizada, THETA, H_UNIFORME)

    registrar(
        "U(0,theta), f=x²: derivada numérica contra 2theta/3",
        "diferença central", f"h={H_UNIFORME:g}, n={N_UNIFORME}, theta={THETA:g}",
        verdadeiro, numerica, TOL_DIF_PRIMEIRA,
    )
    registrar(
        "U(0,theta): termo interior sozinho vale -theta/3",
        "Simpson", f"n={N_UNIFORME}, theta={THETA:g}",
        -THETA / 3.0, interior, TOL_QUADRATURA,
    )
    registrar(
        "U(0,theta): termo de fronteira f(theta)p(theta) vale theta",
        "avaliação direta", f"theta={THETA:g}",
        THETA, fronteira, TOL_EXATA,
    )
    registrar(
        "U(0,theta): interior + fronteira = 2theta/3",
        "Simpson", f"n={N_UNIFORME}, theta={THETA:g}",
        verdadeiro, interior + fronteira, TOL_QUADRATURA,
    )
    registrar(
        "U(0,theta): pathwise, d/dtheta da integral de f(theta u) du",
        "diferença central", f"h={H_UNIFORME:g}, n={N_UNIFORME}",
        verdadeiro, pathwise, TOL_DIF_PRIMEIRA,
    )
    return {
        "verdadeiro": verdadeiro,
        "numerica": numerica,
        "interior": interior,
        "fronteira": fronteira,
        "soma": interior + fronteira,
        "pathwise": pathwise,
    }


# --- 6. Contraexemplo em domínio infinito ----------------------------------
#
#   I(t) = integral de 0 a infinito de t e^{-tx} dx = 1 para todo t > 0,
#   e I(0) = 0. Integrando suave em t para cada x, e mesmo assim I é
#   descontínua na origem: continuidade não basta em domínio infinito.

N_IMPROPRIA = 400_000
TS_IMPROPRIA = (1.0, 0.1, 0.01)


def verificar_impropria():
    valores = []
    for t in TS_IMPROPRIA:
        limite = 40.0 / t  # e^-40 ~ 4e-18 de cauda descartada
        obtido = simpson(lambda x: t * math.exp(-t * x), 0.0, limite, N_IMPROPRIA)
        registrar(
            f"integral de t e^(-tx) em [0,inf) com t={t:g}",
            "Simpson truncado", f"n={N_IMPROPRIA}, corte em 40/t={limite:g}",
            1.0, obtido, TOL_IMPROPRIA,
        )
        valores.append(obtido)

    # Em t = 0 o integrando é identicamente nulo, então a integral é 0 exato.
    em_zero = simpson(lambda x: 0.0 * math.exp(0.0), 0.0, 1000.0, 1000)
    registrar(
        "integral de t e^(-tx) em [0,inf) com t=0",
        "avaliação direta", "integrando identicamente nulo",
        0.0, em_zero, TOL_EXATA,
    )
    return valores, em_zero


# --- 7. O parâmetro inventado (truque de Feynman) --------------------------
#
#   I(a) = integral de 0 a 1 de (x^a - 1)/ln x dx = ln(a+1), para a > -1.
#
# É a seção 8 das notas do Keith Conrad, que dá as dominantes explícitas:
# A(x) = (1 - x^c)/log x e B(x) = 1 para 0 < a < c.

N_FEYNMAN = 200_000
AS_FEYNMAN = (0.5, 1.0, 2.0, 4.0)


def integrando_feynman(x, a):
    """(x^a - 1)/ln x, com os dois extremos definidos por continuidade.

    Em x -> 0+ o quociente vai a 0; em x -> 1- vai a `a`. Sem tratar as pontas
    o Simpson pega 0/0 e 1/0 e devolve nan.
    """
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return a
    return (x ** a - 1.0) / math.log(x)


def verificar_feynman():
    obtidos = []
    for a in AS_FEYNMAN:
        obtido = simpson(lambda x: integrando_feynman(x, a), 0.0, 1.0, N_FEYNMAN)
        registrar(
            f"integral de (x^a-1)/ln x em [0,1] com a={a:g}",
            "Simpson", f"n={N_FEYNMAN}",
            math.log(a + 1.0), obtido, TOL_ENDPOINT,
        )
        obtidos.append(obtido)
    return obtidos


# --- Relatório -------------------------------------------------------------

def imprimir_cabecalho(acumulador, uniforme):
    print("Verificação numérica: O termo de fronteira, regra de Leibniz")
    print("https://rifeli.dev/blog/2026-09-02-termo-de-fronteira-regra-de-leibniz/")
    print()
    print("Parâmetros do caso principal:")
    print(f"  F(tau) = 1 + tau/2, t = {T_ALVO:g}, núcleo log2(2 + t - tau)")
    print(f"  Simpson com n = {N_ACUMULADOR} subintervalos")
    print(f"  diferença central h = {H_PRIMEIRA:g}, diferença segunda h = {H_SEGUNDA:g}")
    print()
    print("A tabela do post, com todos os dígitos:")
    print(f"  A'(7)  numérico {acumulador['numerica_primeira']:.12f}"
          f"  Leibniz {acumulador['leibniz_primeira']:.12f}"
          f"  erro {abs(acumulador['numerica_primeira'] - acumulador['leibniz_primeira']):.1e}")
    print(f"  A''(7) numérico {acumulador['numerica_segunda']:.12f}"
          f"  Leibniz {acumulador['leibniz_segunda']:.12f}"
          f"  erro {abs(acumulador['numerica_segunda'] - acumulador['leibniz_segunda']):.1e}")
    print(f"  A'(7) sem o termo de fronteira: {acumulador['sem_fronteira']:.12f}")
    print(f"  diferença para o valor certo:   {acumulador['leibniz_primeira'] - acumulador['sem_fronteira']:.12f}"
          f"  ({100.0 * (acumulador['leibniz_primeira'] - acumulador['sem_fronteira']) / acumulador['leibniz_primeira']:.1f}%"
          " da resposta)")
    print()
    print("Uniforme(0, theta) com f(x) = x², theta = 3:")
    print(f"  gradiente verdadeiro         {uniforme['verdadeiro']:+.9f}")
    print(f"  só o termo interior          {uniforme['interior']:+.9f}")
    print(f"  só o termo de fronteira      {uniforme['fronteira']:+.9f}")
    print(f"  interior + fronteira         {uniforme['soma']:+.9f}")
    print(f"  pathwise (x = theta u)       {uniforme['pathwise']:+.9f}")
    print()


def imprimir_tabela():
    largura = max(len(r["nome"]) for r in RESULTADOS)
    print(f"{'verificação'.ljust(largura)}  {'esperado':>18}  {'obtido':>18}  "
          f"{'erro':>9}  {'tolerância':>10}  ok")
    print("-" * (largura + 66))
    for r in RESULTADOS:
        print(f"{r['nome'].ljust(largura)}  {r['esperado']:>18.12f}  {r['obtido']:>18.12f}  "
              f"{r['erro']:>9.1e}  {r['tolerancia']:>10.1e}  "
              f"{'ok' if r['passou'] else 'FALHOU'}")
    print()
    for r in RESULTADOS:
        print(f"  {r['nome']}: {r['metodo']}, {r['discretizacao']}")


def main():
    acumulador = verificar_acumulador()
    verificar_janela()
    verificar_suporte_fixo()
    uniforme = verificar_suporte_movel()
    verificar_impropria()
    verificar_feynman()

    imprimir_cabecalho(acumulador, uniforme)
    imprimir_tabela()

    falhas = [r for r in RESULTADOS if not r["passou"]]
    print()
    if falhas:
        print(f"FALHOU: {len(falhas)} de {len(RESULTADOS)} verificações passaram da tolerância.")
        for r in falhas:
            print(f"  - {r['nome']}: erro {r['erro']:.3e} > tolerância {r['tolerancia']:.1e}")
        return 1
    print(f"OK: {len(RESULTADOS)} verificações dentro da tolerância.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
