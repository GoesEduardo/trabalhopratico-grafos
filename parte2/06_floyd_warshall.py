from math import inf
from comum import carregar, argumentos_base, amostra_bfs, induzido


def floyd_warshall(adjacencia: list[list[int]]):
    n = len(adjacencia)
    dist = [[inf] * n for _ in range(n)]
    for u in range(n):
        dist[u][u] = 0
        for v in adjacencia[u]:
            dist[u][v] = 1
    for k in range(n):
        for i in range(n):
            dik = dist[i][k]
            if dik == inf:
                continue
            di = dist[i]
            dk = dist[k]
            for j in range(n):
                candidato = dik + dk[j]
                if candidato < di[j]:
                    di[j] = candidato
    return dist


if __name__ == "__main__":
    parser = argumentos_base("Floyd-Warshall em subgrafo induzido da rede Gnutella05")
    parser.add_argument("--origem-amostra", type=int, default=0)
    parser.add_argument("--amostra", type=int, default=80)
    args = parser.parse_args()
    g = carregar(args.dados)
    if args.amostra > 500:
        parser.error("A amostra deve ter no máximo 500 vértices")
    # A busca em largura define o recorte usado pelo subgrafo induzido.
    nos = amostra_bfs(g, args.origem_amostra, min(args.amostra, g.n))
    adj = induzido(g.saida, nos)
    d = floyd_warshall(adj)
    pares = [valor for i, linha in enumerate(d) for j, valor in enumerate(linha)
             if i != j and valor < inf]
    print(f"Floyd-Warshall: amostra de {len(nos)} vértices")
    print(f"Pares alcançáveis: {len(pares)}; maior distância: {max(pares) if pares else 'N/A'}")
