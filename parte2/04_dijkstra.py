import heapq
from math import inf
from comum import carregar, argumentos_base


def dijkstra(adjacencia: list[list[int]], origem: int):
    n = len(adjacencia)
    if not 0 <= origem < n:
        raise ValueError("Origem inválida")
    dist = [inf] * n
    pai = [None] * n
    dist[origem] = 0
    heap = [(0, origem)]
    while heap:
        d, u = heapq.heappop(heap)
        if d != dist[u]:
            continue
        for v in adjacencia[u]:
            nd = d + 1
            if nd < dist[v]:
                dist[v] = nd
                pai[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, pai


if __name__ == "__main__":
    parser = argumentos_base("Dijkstra no grafo original dirigido; arestas com peso 1")
    parser.add_argument("--origem", type=int, default=0)
    args = parser.parse_args()
    g = carregar(args.dados)
    dist, pai = dijkstra(g.saida, args.origem)
    alcan = [d for d in dist if d < inf]
    print(f"Dijkstra dirigido, origem {args.origem}, peso por aresta = 1")
    print(f"Alcançados: {len(alcan)} de {g.n}; maior distância finita: {max(alcan)}")
