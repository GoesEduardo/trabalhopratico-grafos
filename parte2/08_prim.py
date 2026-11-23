import heapq
from comum import carregar, argumentos_base


def prim(adjacencia: list[list[int]]):
    visitado = [False] * len(adjacencia)
    floresta = []
    componentes = 0
    for raiz in range(len(adjacencia)):
        if visitado[raiz]:
            continue
        componentes += 1
        visitado[raiz] = True
        heap = [(1, raiz, v) for v in adjacencia[raiz]]
        heapq.heapify(heap)
        while heap:
            peso, u, v = heapq.heappop(heap)
            if visitado[v]:
                continue
            visitado[v] = True
            floresta.append((u, v, peso))
            for w in adjacencia[v]:
                if not visitado[w]:
                    heapq.heappush(heap, (1, v, w))
    return floresta, componentes


if __name__ == "__main__":
    args = argumentos_base("Prim: floresta geradora mínima não dirigida").parse_args()
    g = carregar(args.dados)
    arestas, comp = prim(g.nao_dirigido)
    print(f"Prim: {comp} árvores, {len(arestas)} arestas, peso total={sum(w for _, _, w in arestas)}")
