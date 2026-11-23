from comum import carregar, argumentos_base


def tarjan(adjacencia: list[list[int]]) -> list[list[int]]:
    n = len(adjacencia)
    indices = [-1] * n
    low = [0] * n
    na_pilha = [False] * n
    pilha_ativa = []
    componentes = []
    indice = 0
    for raiz in range(n):
        if indices[raiz] != -1:
            continue
        indices[raiz] = low[raiz] = indice
        indice += 1
        pilha_ativa.append(raiz)
        na_pilha[raiz] = True

        # Iteradores na pilha substituem a DFS recursiva.
        frames = [[raiz, iter(adjacencia[raiz]), None]]
        while frames:
            u, it, pai = frames[-1]
            try:
                v = next(it)
            except StopIteration:
                frames.pop()
                if pai is not None:
                    low[pai] = min(low[pai], low[u])
                if low[u] == indices[u]:
                    comp = []
                    while True:
                        v = pilha_ativa.pop()
                        na_pilha[v] = False
                        comp.append(v)
                        if v == u:
                            break
                    componentes.append(comp)
                continue
            if indices[v] == -1:
                indices[v] = low[v] = indice
                indice += 1
                pilha_ativa.append(v)
                na_pilha[v] = True
                frames.append([v, iter(adjacencia[v]), u])
            elif na_pilha[v]:
                low[u] = min(low[u], indices[v])
    return componentes


if __name__ == "__main__":
    args = argumentos_base("Tarjan (componentes fortemente conexas do grafo dirigido)").parse_args()
    g = carregar(args.dados)
    componentes = tarjan(g.saida)
    tamanhos = sorted((len(comp) for comp in componentes), reverse=True)
    print(f"Tarjan (dirigido): {len(componentes)} componentes fortemente conexas")
    print(f"Maior componente: {tamanhos[0]} vértices; maiores 10: {tamanhos[:10]}")
