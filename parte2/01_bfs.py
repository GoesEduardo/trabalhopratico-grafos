from collections import deque
from comum import carregar, argumentos_base


def bfs(adjacencia: list[list[int]], origem: int):
    n = len(adjacencia)
    if not 0 <= origem < n:
        raise ValueError("Origem inválida")
    distancia = [-1] * n
    pai = [None] * n
    ordem = []
    fila = deque([origem])
    distancia[origem] = 0
    while fila:
        u = fila.popleft()
        ordem.append(u)
        for v in adjacencia[u]:
            if distancia[v] == -1:
                distancia[v] = distancia[u] + 1
                pai[v] = u
                fila.append(v)
    return ordem, distancia, pai


if __name__ == "__main__":
    parser = argumentos_base("Busca em largura no grafo original dirigido")
    parser.add_argument("--origem", type=int, default=0)
    args = parser.parse_args()
    g = carregar(args.dados)
    ordem, dist, pai = bfs(g.saida, args.origem)
    print(f"BFS dirigido a partir de {args.origem}")
    print(f"Vértices alcançados: {len(ordem)} de {g.n}")
    print(f"Distância máxima alcançada: {max(dist)}")
    print(f"Primeiros 20 vértices visitados: {ordem[:20]}")
