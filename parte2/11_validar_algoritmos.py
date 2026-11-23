from importlib import import_module
from math import inf
from comum import carregar, induzido, amostra_bfs


def validar():
    g = carregar()
    assert g.n == 8846 and g.m == 31839, (g.n, g.m)
    bfs = import_module("01_bfs").bfs
    dfs = import_module("02_dfs").dfs
    euler = import_module("03_eulerianidade").verificar_euleriano_dirigido
    dijkstra = import_module("04_dijkstra").dijkstra
    bf = import_module("05_bellman_ford").bellman_ford
    fw = import_module("06_floyd_warshall").floyd_warshall
    tarjan = import_module("07_tarjan").tarjan
    prim = import_module("08_prim").prim
    kruskal = import_module("09_kruskal").kruskal
    orden, dist_bfs, _ = bfs(g.saida, 0)
    orden_dfs, _ = dfs(g.saida, 0)
    assert set(orden) == set(orden_dfs)
    dist_dj, _ = dijkstra(g.saida, 0)
    assert all(a == b or (a == -1 and b == inf) for a, b in zip(dist_bfs, dist_dj))
    cc = tarjan(g.saida)
    assert len(cc) == 5613 and max(map(len, cc)) == 3234, (len(cc), max(map(len, cc)))
    assert euler(g.saida, g.entrada)[:2] == (False, False)
    p, k = prim(g.nao_dirigido), kruskal(g.nao_dirigido)
    assert (len(p[0]), p[1]) == (8843, 3), (len(p[0]), p[1])
    assert (len(k[0]), k[1]) == (8843, 3), (len(k[0]), k[1])
    nos = amostra_bfs(g, 0, 80)
    adj = induzido(g.saida, nos)
    dist_fw = fw(adj)
    for s in (0, 5, 15):
        _, db, _ = bfs(adj, s)
        assert all(a == b or (b == -1 and a == inf) for a, b in zip(dist_fw[s], db))
    n250 = amostra_bfs(g, 0, 250)
    adj250 = induzido(g.saida, n250)
    arestas = [(u, v, 1.0) for u, vs in enumerate(adj250) for v in vs]
    bf_dist, _, _ = bf(len(adj250), arestas, 0)
    _, b_dist, _ = bfs(adj250, 0)
    assert all(a == b or (b == -1 and a == inf) for a, b in zip(bf_dist, b_dist))
    print("TODOS OS TESTES PASSARAM")
    print("SNAP: 8846 vértices; 31839 arestas dirigidas")
    print(f"BFS/DFS alcançam {len(orden)} vértices desde a origem 0")
    print(f"Tarjan: {len(cc)} SCC; maior SCC = {max(map(len, cc))}")
    print("Prim/Kruskal: 3 árvores e 8843 arestas nas florestas geradoras mínimas")
    print("Dijkstra/Bellman-Ford/Floyd-Warshall concordam com BFS nos casos testados")


if __name__ == "__main__":
    validar()
