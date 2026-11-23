from comum import carregar, argumentos_base


class UnionFind:
    def __init__(self, n):
        self.pai = list(range(n))
        self.tamanho = [1] * n
        self.componentes = n

    def encontrar(self, x):
        while self.pai[x] != x:
            self.pai[x] = self.pai[self.pai[x]]
            x = self.pai[x]
        return x

    def unir(self, a, b):
        a, b = self.encontrar(a), self.encontrar(b)
        if a == b:
            return False
        if self.tamanho[a] < self.tamanho[b]:
            a, b = b, a
        self.pai[b] = a
        self.tamanho[a] += self.tamanho[b]
        self.componentes -= 1
        return True


def kruskal(adjacencia):
    n = len(adjacencia)
    arestas = sorted((1, u, v)
                     for u in range(n) for v in adjacencia[u] if u < v)
    uf = UnionFind(n)
    floresta = []
    for peso, u, v in arestas:
        if uf.unir(u, v):
            floresta.append((u, v, peso))
    return floresta, uf.componentes


if __name__ == "__main__":
    args = argumentos_base("Kruskal: floresta geradora mínima não dirigida").parse_args()
    g = carregar(args.dados)
    arestas, comp = kruskal(g.nao_dirigido)
    print(f"Kruskal: {comp} árvores, {len(arestas)} arestas, peso total={sum(w for _, _, w in arestas)}")
