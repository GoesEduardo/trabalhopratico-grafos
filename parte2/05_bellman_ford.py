from math import inf
from comum import carregar, argumentos_base, amostra_bfs, induzido


def bellman_ford(n: int, arestas_pesadas: list[tuple[int, int, float]], origem: int):
    dist = [inf] * n
    pai = [None] * n
    dist[origem] = 0
    passos = 0
    for _ in range(n - 1):
        alterou = False
        for u, v, peso in arestas_pesadas:
            if dist[u] != inf and dist[u] + peso < dist[v]:
                dist[v] = dist[u] + peso
                pai[v] = u
                alterou = True
        passos += 1
        if not alterou:
            break
    for u, v, peso in arestas_pesadas:
        if dist[u] != inf and dist[u] + peso < dist[v]:
            raise ValueError("Ciclo de peso negativo alcançável pela origem")
    return dist, pai, passos


if __name__ == "__main__":
    parser = argumentos_base("Bellman-Ford na rede Gnutella05 (pesos 1)")
    parser.add_argument("--origem", type=int, default=0)
    parser.add_argument("--amostra", type=int, default=250,
                        help="Número de vértices na amostra induzida (250); use 0 para grafo completo")
    args = parser.parse_args()
    g = carregar(args.dados)
    if args.amostra:
        # A busca em largura define o recorte usado pelo subgrafo induzido.
        nos = amostra_bfs(g, args.origem, min(args.amostra, g.n))
        adj = induzido(g.saida, nos)
        origem = 0
        escopo = f"amostra de {len(nos)} vértices"
    else:
        adj = g.saida
        origem = args.origem
        escopo = "grafo completo"
    arestas = [(u, v, 1.0) for u, vs in enumerate(adj) for v in vs]
    dist, pai, iteracoes = bellman_ford(len(adj), arestas, origem)
    alcancados = sum(d < inf for d in dist)
    print(f"Bellman-Ford: {escopo}; origem={args.origem}")
    print(f"Alcançados: {alcancados}; arestas: {len(arestas)}; iterações: {iteracoes}")
