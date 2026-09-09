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

# Simpson perto de extremo onde o integrando tem derivadas de ordem alta
# ilimitadas: perto de x = 0 o integrando do truque de Feynman vale -1/ln x,
# que vai a zero mas com todas as derivadas explodindo. O erro deixa de ser
# O(h^4) e passa a ser governado pelos subintervalos junto à ponta.
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


RESULTADOS = []


def registrar(nome, como, esperado, obtido, tolerancia):
    """Guarda uma verificação. `como` é método mais discretização."""
    erro = abs(obtido - esperado)
    RESULTADOS.append({
        "nome": nome, "como": como, "esperado": esperado, "obtido": obtido,
        "erro": erro, "tolerancia": tolerancia, "passou": erro <= tolerancia,
    })


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


def interior_primeira(t):
    """c * integral de F(tau)/(2 + t - tau): A'(t) sem o termo de fronteira.

    É a conta errada que abre o post, e por isso ela é uma função nomeada: o
    valor dela aparece publicado.
    """
    return C * simpson(lambda tau: F(tau) / (2.0 + t - tau), 0.0, t, N_ACUMULADOR)


def A_linha_leibniz(t):
    """F(t) + interior. O F(t) é a fronteira, g(t, b(t)) b'(t), que aqui sai
    redonda porque o núcleo vale 1 na diagonal."""
    return F(t) + interior_primeira(t)


def A_duas_linhas_leibniz(t):
    """F'(t) + c [ F(t)/2 - integral de F(tau)/(2 + t - tau)² ].

    Leibniz aplicado uma segunda vez sobre a integral que sobrou. O F(t)/2 é o
    novo termo de fronteira, o núcleo 1/(2+t-tau) avaliado na diagonal.
    """
    interior = simpson(lambda tau: F(tau) / (2.0 + t - tau) ** 2, 0.0, t, N_ACUMULADOR)
    return dF(t) + C * (F(t) / 2.0 - interior)


def A_linha_fechada():
    """Forma fechada em t = 7, pela substituição u = 2 + t - tau.

    Com F(tau) = 1 + tau/2, u vai de 2 a 9 e F = (11 - u)/2, então a integral
    interior é (11 ln(9/2) - 7)/2.
    """
    return F(T_ALVO) + C * (11.0 * math.log(4.5) - 7.0) / 2.0


def A_duas_linhas_fechada():
    """Idem para a segunda derivada: a integral vale (77/18 - ln(9/2))/2."""
    return dF(T_ALVO) + C * (F(T_ALVO) / 2.0 - (77.0 / 18.0 - math.log(4.5)) / 2.0)


def verificar_acumulador():
    exata_1, exata_2 = A_linha_fechada(), A_duas_linhas_fechada()
    sem_fronteira = interior_primeira(T_ALVO)
    leibniz_1 = F(T_ALVO) + sem_fronteira
    leibniz_2 = A_duas_linhas_leibniz(T_ALVO)
    numerica_1 = derivada_central(A, T_ALVO, H_PRIMEIRA)
    numerica_2 = derivada_segunda_central(A, T_ALVO, H_SEGUNDA)

    disc = f"n={N_ACUMULADOR}"
    registrar("A'(7): Leibniz vs fechada", f"Simpson, {disc}",
              exata_1, leibniz_1, TOL_QUADRATURA)
    registrar("A'(7): numérica vs fechada", f"dif. central h={H_PRIMEIRA:g}, {disc}",
              exata_1, numerica_1, TOL_DIF_PRIMEIRA)
    registrar("A''(7): Leibniz vs fechada", f"Simpson, {disc}",
              exata_2, leibniz_2, TOL_QUADRATURA)
    registrar("A''(7): numérica vs fechada", f"dif. segunda h={H_SEGUNDA:g}, {disc}",
              exata_2, numerica_2, TOL_DIF_SEGUNDA)
    # O número que abre o post: a omissão do termo de fronteira tem que custar
    # exatamente F(7) = 4,5, e não uma sobra qualquer.
    registrar("termo de fronteira esquecido = F(7)", f"Simpson, {disc}",
              F(T_ALVO), leibniz_1 - sem_fronteira, TOL_QUADRATURA)

    return {"numerica_1": numerica_1, "leibniz_1": leibniz_1, "numerica_2": numerica_2,
            "leibniz_2": leibniz_2, "sem_fronteira": sem_fronteira}


# --- 3. Janela deslizante --------------------------------------------------
#
#   A(t) = integral de t-W a t de f(tau) dtau   =>   A'(t) = f(t) - f(t-W)
#
# Os dois limites andam, o integrando não depende de t: fronteira pura.

W_JANELA, T_JANELA, N_JANELA = 3.0, 4.2, 200_000


def sinal(tau):
    """Um sinal qualquer, suave e sem simetria que possa mascarar erro."""
    return math.sin(tau) + tau * tau / 10.0 + math.exp(-tau)


def verificar_janela():
    janela = lambda t: simpson(sinal, t - W_JANELA, t, N_JANELA)
    registrar("janela: A'(t) = f(t) - f(t-W)",
              f"dif. central h={H_PRIMEIRA:g}, n={N_JANELA}, W={W_JANELA:g}",
              sinal(T_JANELA) - sinal(T_JANELA - W_JANELA),
              derivada_central(janela, T_JANELA, H_PRIMEIRA), TOL_DIF_PRIMEIRA)


# --- 4. Gradiente de esperança com suporte fixo ----------------------------
#
#   X ~ N(mu, 1), f(x) = x³.  E[f(X)] = mu³ + 3mu, logo d/dmu = 3(mu² + 1).
#
# Suporte independente do parâmetro: a identidade do score function vale.

MU, N_NORMAL, RAIO_NORMAL = 1.7, 200_000, 12.0  # 12 desvios: cauda ~ 1e-32


def densidade_normal(x, mu):
    return math.exp(-0.5 * (x - mu) ** 2) / math.sqrt(2.0 * math.pi)


def verificar_suporte_fixo():
    fechada = 3.0 * (MU * MU + 1.0)
    esperanca = lambda mu: simpson(lambda x: x ** 3 * densidade_normal(x, mu),
                                   mu - RAIO_NORMAL, mu + RAIO_NORMAL, N_NORMAL)
    # score de N(mu,1): d/dmu log p = (x - mu)
    score = simpson(lambda x: x ** 3 * (x - MU) * densidade_normal(x, MU),
                    MU - RAIO_NORMAL, MU + RAIO_NORMAL, N_NORMAL)

    registrar("E[X³] sob N(mu,1): score vs fechada", f"Simpson, n={N_NORMAL}, mu={MU:g}",
              fechada, score, TOL_QUADRATURA)
    registrar("E[X³] sob N(mu,1): numérica vs fechada",
              f"dif. central h={H_PRIMEIRA:g}, n={N_NORMAL}",
              fechada, derivada_central(esperanca, MU, H_PRIMEIRA), TOL_DIF_PRIMEIRA)


# --- 5. Suporte que depende do parâmetro -----------------------------------
#
#   X ~ Uniforme(0, theta), f(x) = x².  E[f(X)] = theta²/3, gradiente 2theta/3.
#
# Aqui a fronteira é o parâmetro. As três parcelas separadas:
#   interior  = integral de 0 a theta de f(x) * d_theta(1/theta) dx = -theta/3
#   fronteira = f(theta) p_theta(theta) = theta
#   soma      = 2theta/3, o gradiente verdadeiro
# e, por outro caminho, o pathwise: x = theta*u com u ~ U(0,1) leva a
# E[f(X)] = integral de 0 a 1 de f(theta u) du, com limites fixos.

THETA, N_UNIFORME = 3.0, 200_000


def verificar_suporte_movel():
    verdadeiro = 2.0 * THETA / 3.0
    disc = f"n={N_UNIFORME}, theta={THETA:g}"

    esperanca = lambda th: simpson(lambda x: x * x / th, 0.0, th, N_UNIFORME)
    # Aplicação ingênua do score function: deriva só a densidade no interior,
    # com d_theta(1/theta) = -1/theta², e ignora que o suporte se move.
    interior = simpson(lambda x: -x * x / (THETA * THETA), 0.0, THETA, N_UNIFORME)
    fronteira = (THETA ** 2) * (1.0 / THETA)  # f(theta) * p_theta(theta)
    # Pathwise: o parâmetro sai da fronteira e vai pro integrando.
    reparametrizada = lambda th: simpson(lambda u: (th * u) ** 2, 0.0, 1.0, N_UNIFORME)

    registrar("U(0,theta): numérica vs 2theta/3", f"dif. central h={H_PRIMEIRA:g}, {disc}",
              verdadeiro, derivada_central(esperanca, THETA, H_PRIMEIRA), TOL_DIF_PRIMEIRA)
    registrar("U(0,theta): interior sozinho = -theta/3", f"Simpson, {disc}",
              -THETA / 3.0, interior, TOL_QUADRATURA)
    registrar("U(0,theta): fronteira f(t)p(t) = theta", f"avaliação direta, theta={THETA:g}",
              THETA, fronteira, TOL_EXATA)
    registrar("U(0,theta): interior + fronteira", f"Simpson, {disc}",
              verdadeiro, interior + fronteira, TOL_QUADRATURA)
    registrar("U(0,theta): pathwise, d/dtheta f(theta u)",
              f"dif. central h={H_PRIMEIRA:g}, {disc}",
              verdadeiro, derivada_central(reparametrizada, THETA, H_PRIMEIRA),
              TOL_DIF_PRIMEIRA)

    return {"verdadeiro": verdadeiro, "interior": interior, "fronteira": fronteira,
            "soma": interior + fronteira,
            "pathwise": derivada_central(reparametrizada, THETA, H_PRIMEIRA)}


# --- 6. Contraexemplo em domínio infinito ----------------------------------
#
#   I(t) = integral de 0 a infinito de t e^{-tx} dx = 1 para todo t > 0,
#   e I(0) = 0. Integrando suave em t para cada x, e mesmo assim I é
#   descontínua na origem: continuidade não basta em domínio infinito.
#
# O t = 0 não entra como verificação: lá o integrando é identicamente nulo e
# integrar zero não prova nada. O que prova a descontinuidade é I continuar
# valendo 1 com t arbitrariamente pequeno, e é isso que a lista abaixo faz.

N_IMPROPRIA = 400_000
TS_IMPROPRIA = (1.0, 0.1, 0.01, 0.001)


def verificar_impropria():
    for t in TS_IMPROPRIA:
        limite = 40.0 / t  # e^-40 ~ 4e-18 de cauda descartada
        registrar(f"integral de t·e^(-tx), t={t:g}",
                  f"Simpson truncado, n={N_IMPROPRIA}, corte 40/t={limite:g}",
                  1.0, simpson(lambda x: t * math.exp(-t * x), 0.0, limite, N_IMPROPRIA),
                  TOL_IMPROPRIA)


# --- 7. O parâmetro inventado (truque de Feynman) --------------------------
#
#   I(a) = integral de 0 a 1 de (x^a - 1)/ln x dx = ln(a+1), para a > -1.
#
# Para a < 0 o integrando é ilimitado em x = 0 (vale x^a/ln x, e x^a estoura),
# então a integral é imprópria e o Simpson direto não serve. A substituição
# x = u^p transforma o integrando em (u^{pa} - 1) u^{p-1} / ln u, que perto de
# u = 0 se comporta como u^{p(a+1)-1}: escolhendo p com p(a+1) > 1 o integrando
# volta a ser limitado. Note que no extremo u = 1 o valor limite passa a ser
# p*a, e não a; errar isso custa h/3 * |p a - a| de erro, que para n = 2*10^5
# já é 2,5e-6 e domina tudo.

N_FEYNMAN = 200_000
AS_FEYNMAN = ((0.5, 1), (1.0, 1), (2.0, 1), (4.0, 1), (-0.5, 4))


def integrando_feynman(u, a, p):
    """(u^{pa} - 1) u^{p-1} / ln u, com os extremos definidos por continuidade.

    Com p = 1 é o integrando original. Em u -> 0+ o valor tende a 0 sempre que
    p(a+1) > 1; em u -> 1- tende a p*a.
    """
    if u <= 0.0:
        return 0.0
    if u >= 1.0:
        return p * a
    return (u ** (p * a) - 1.0) * u ** (p - 1.0) / math.log(u)


def verificar_feynman():
    for a, p in AS_FEYNMAN:
        como = f"Simpson, n={N_FEYNMAN}" + (f", subst. x=u^{p}" if p != 1 else "")
        registrar(f"integral de (x^a-1)/ln x, a={a:g}", como, math.log(a + 1.0),
                  simpson(lambda u: integrando_feynman(u, a, p), 0.0, 1.0, N_FEYNMAN),
                  TOL_ENDPOINT)


# A dominação que o post publica. A tabela do Conrad cobre 0 < a < c e dá a
# cota |d_a f| <= 1, que é falsa para a negativo. A cota que vale em todo
# a0 > -1 é local: tome [c, C] em volta de a0, com c > -1, contendo o zero.
# Como x^s decresce em s para x em (0,1), vale x^a <= x^c; e escrevendo o
# próprio integrando como integral, f(x,a) = integral de 0 a a de x^s ds,
# vale |f| <= (C-c) x^c. As duas são integráveis, porque c > -1.

VIZINHANCAS = ((-0.5, -0.75, 0.25), (2.0, -0.25, 2.5), (-0.9, -0.95, 0.05))
GRADE_X, GRADE_A = 2000, 40


def verificar_dominacao():
    pior = 0.0
    for _a0, c, cc in VIZINHANCAS:
        for i in range(1, GRADE_X):
            x = i / GRADE_X
            cota_x = x ** c
            for j in range(GRADE_A + 1):
                a = c + (cc - c) * j / GRADE_A
                pior = max(pior, x ** a - cota_x)  # |d_a f| <= x^c
                pior = max(pior, abs(integrando_feynman(x, a, 1)) - (cc - c) * cota_x)
    registrar("dominação local do truque de Feynman",
              f"grade {GRADE_X}x{GRADE_A + 1}, {len(VIZINHANCAS)} vizinhanças",
              0.0, max(pior, 0.0), TOL_EXATA)


# --- Relatório -------------------------------------------------------------

def imprimir_resumo(acu, uni):
    """Reproduz, com todos os dígitos, os números que o post publica."""
    print("Verificação numérica: O termo de fronteira, regra de Leibniz")
    print("https://rifeli.dev/blog/2026-09-02-termo-de-fronteira-regra-de-leibniz/")
    print()
    print(f"Caso principal: F(tau) = 1 + tau/2, t = {T_ALVO:g}, "
          "núcleo log2(2 + t - tau)")
    print()
    print("A tabela do post:")
    for rot, num, lei in (("A'(7) ", acu["numerica_1"], acu["leibniz_1"]),
                          ("A''(7)", acu["numerica_2"], acu["leibniz_2"])):
        print(f"  {rot}  numérico {num:.12f}   Leibniz {lei:.12f}   "
              f"erro {abs(num - lei):.1e}")
    perdido = acu["leibniz_1"] - acu["sem_fronteira"]
    print(f"  A'(7) sem o termo de fronteira: {acu['sem_fronteira']:.12f}, "
          f"ou seja {perdido:.12f} a menos "
          f"({100.0 * perdido / acu['leibniz_1']:.1f}% da resposta)")
    print()
    print(f"Uniforme(0, theta) com f(x) = x², theta = {THETA:g}:")
    for rot, v in (("gradiente verdadeiro", uni["verdadeiro"]),
                   ("só o interior", uni["interior"]),
                   ("só a fronteira", uni["fronteira"]),
                   ("interior + fronteira", uni["soma"]),
                   ("pathwise (x = theta u)", uni["pathwise"])):
        print(f"  {rot:<24} {v:+.9f}")
    print()


def imprimir_tabela():
    ln = max(len(r["nome"]) for r in RESULTADOS)
    lc = max(len(r["como"]) for r in RESULTADOS)
    print(f"{'verificação'.ljust(ln)}  {'método e discretização'.ljust(lc)}  "
          f"{'esperado':>17}  {'obtido':>17}  {'erro':>8}  {'tol':>8}  ok")
    print("-" * (ln + lc + 62))
    for r in RESULTADOS:
        print(f"{r['nome'].ljust(ln)}  {r['como'].ljust(lc)}  "
              f"{r['esperado']:>17.12f}  {r['obtido']:>17.12f}  "
              f"{r['erro']:>8.1e}  {r['tolerancia']:>8.1e}  "
              f"{'ok' if r['passou'] else 'FALHOU'}")


def main():
    acumulador = verificar_acumulador()
    verificar_janela()
    verificar_suporte_fixo()
    uniforme = verificar_suporte_movel()
    verificar_impropria()
    verificar_feynman()
    verificar_dominacao()

    imprimir_resumo(acumulador, uniforme)
    imprimir_tabela()

    falhas = [r for r in RESULTADOS if not r["passou"]]
    print()
    if falhas:
        print(f"FALHOU: {len(falhas)} de {len(RESULTADOS)} verificações "
              "passaram da tolerância.")
        for r in falhas:
            print(f"  - {r['nome']}: erro {r['erro']:.3e} > tol {r['tolerancia']:.1e}")
        return 1
    print(f"OK: {len(RESULTADOS)} verificações dentro da tolerância.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
