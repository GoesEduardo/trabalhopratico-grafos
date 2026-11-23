from comum import carregar, argumentos_base, conjunto_alcancavel


def verificar_euleriano_dirigido(saida, entrada):
    n = len(saida)
    und = [set(saida[u]) | set(entrada[u]) for u in range(n)]
    ativos = {u for u in range(n) if saida[u] or entrada[u]}
    if not ativos:
        return True, True, "Sem arestas: existe circuito trivial"
    origem = min(ativos)
    if len(ativos.intersection(conjunto_alcancavel([list(x) for x in und], origem))) != len(ativos):
        return False, False, "Os vértices incidentes não são fracamente conexos"
    deltas = [len(saida[u]) - len(entrada[u]) for u in range(n)]
    circuito = all(d == 0 for d in deltas)
    positivos = sum(d == 1 for d in deltas)
    negativos = sum(d == -1 for d in deltas)
    trilha = circuito or (positivos == 1 and negativos == 1 and all(abs(d) <= 1 for d in deltas))
    return circuito, trilha, "Condições de grau e conectividade verificadas"


def verificar_euleriano_nao_dirigido(adjacencia):
    ativos = {u for u, adj in enumerate(adjacencia) if adj}
    if not ativos:
        return True, True
    inicio = min(ativos)
    if len(ativos.intersection(conjunto_alcancavel(adjacencia, inicio))) != len(ativos):
        return False, False
    impares = sum(len(adjacencia[u]) % 2 for u in ativos)
    return impares == 0, impares in (0, 2)


if __name__ == "__main__":
    args = argumentos_base("Verificação de eulerianidade dirigida e não dirigida").parse_args()
    g = carregar(args.dados)
    circuito_d, trilha_d, motivo = verificar_euleriano_dirigido(g.saida, g.entrada)
    circuito_u, trilha_u = verificar_euleriano_nao_dirigido(g.nao_dirigido)
    print("Grafo original dirigido:", "circuito=", circuito_d, "trilha=", trilha_d)
    print("Projeção não dirigida:", "circuito=", circuito_u, "trilha=", trilha_u)
    print("Nota:", motivo)
