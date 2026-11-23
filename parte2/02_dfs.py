from comum import carregar, argumentos_base


def dfs(adjacencia: list[list[int]], origem: int):
    n = len(adjacencia)
    if not 0 <= origem < n:
        raise ValueError("Origem inválida")
    visitado = [False] * n
    pai = [None] * n
    ordem = []
    pilha = [(origem, None)]
    while pilha:
        u, anterior = pilha.pop()
        if visitado[u]:
            continue
        visitado[u] = True
        pai[u] = anterior
        ordem.append(u)
        for v in reversed(adjacencia[u]):
            if not visitado[v]:
                pilha.append((v, u))
    return ordem, pai


if __name__ == "__main__":
    parser = argumentos_base("Busca em profundidade no grafo original dirigido")
    parser.add_argument("--origem", type=int, default=0)
    args = parser.parse_args()
    g = carregar(args.dados)
    ordem, pai = dfs(g.saida, args.origem)
    print(f"DFS dirigido a partir de {args.origem}")
    print(f"Vértices alcançados: {len(ordem)} de {g.n}")
    print(f"Primeiros 20 vértices visitados: {ordem[:20]}")
