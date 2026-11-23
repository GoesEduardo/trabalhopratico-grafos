import argparse
from importlib import import_module
import math
import statistics
import time
import csv
from pathlib import Path
from scipy.stats import t as student
from comum import carregar, argumentos_base, amostra_bfs, induzido
from gerar_grafico_tempos import gerar_grafico


def main():
    parser = argumentos_base("Benchmark dos algoritmos da disciplina")
    parser.add_argument("--repeticoes", type=int, default=30)
    parser.add_argument("--sem-grafico", action="store_true",
                        help="Não gerar a figura de tempos após o benchmark")
    parser.add_argument("--amostra-bellman", type=int, default=250)
    parser.add_argument("--amostra-floyd", type=int, default=80)
    parser.add_argument("--saida", default=str(Path(__file__).resolve().parent.parent / "resultados" / "benchmark_reexecutado.csv"))
    args = parser.parse_args()
    if args.repeticoes < 2:
        parser.error("Use pelo menos 2 repetições")
    if args.amostra_floyd > 500 or min(args.amostra_bellman, args.amostra_floyd) < 1:
        parser.error("Amostras inválidas; Floyd aceita até 500 vértices")
    g = carregar(args.dados)
    s250 = induzido(g.saida, amostra_bfs(g, 0, min(args.amostra_bellman, g.n)))
    s80 = induzido(g.saida, amostra_bfs(g, 0, min(args.amostra_floyd, g.n)))
    arestas250 = [(u, v, 1.0) for u, adj in enumerate(s250) for v in adj]
    bfs = import_module("01_bfs").bfs
    dfs = import_module("02_dfs").dfs
    euler = import_module("03_eulerianidade").verificar_euleriano_dirigido
    dijkstra = import_module("04_dijkstra").dijkstra
    bf = import_module("05_bellman_ford").bellman_ford
    fw = import_module("06_floyd_warshall").floyd_warshall
    tarjan = import_module("07_tarjan").tarjan
    prim = import_module("08_prim").prim
    kruskal = import_module("09_kruskal").kruskal
    metodos = [
        ("BFS (dirigido, completo)", lambda: bfs(g.saida, 0), "O(V+E)"),
        ("DFS (dirigido, completo)", lambda: dfs(g.saida, 0), "O(V+E)"),
        ("Eulerianidade (dirigido, completo)", lambda: euler(g.saida, g.entrada), "O(V+E)"),
        ("Dijkstra (dirigido, completo)", lambda: dijkstra(g.saida, 0), "O((V+E)logV)"),
        (f"Bellman-Ford (induzido {len(s250)})", lambda: bf(len(s250), arestas250, 0), "O(VE)"),
        (f"Floyd-Warshall (induzido {len(s80)})", lambda: fw(s80), "O(V³)"),
        ("Tarjan SCC (dirigido, completo)", lambda: tarjan(g.saida), "O(V+E)"),
        ("Prim (não dirigido, completo)", lambda: prim(g.nao_dirigido), "O((V+E)logV)"),
        ("Kruskal (não dirigido, completo)", lambda: kruskal(g.nao_dirigido), "O(ElogE)"),
    ]
    tabela = []
    for nome, funcao, complexidade in metodos:
        tempos = []
        for _ in range(args.repeticoes):
            comeco = time.perf_counter()
            funcao()
            tempos.append(time.perf_counter() - comeco)
        media = statistics.mean(tempos)
        dp = statistics.stdev(tempos)
        critico = 1.96 if args.repeticoes >= 30 else student.ppf(.975, args.repeticoes-1)
        margem = critico * dp / math.sqrt(args.repeticoes)
        linha = {"algoritmo": nome, "complexidade_teorica": complexidade,
                 "repeticoes": args.repeticoes, "media_s": media, "dp_s": dp,
                 "ic95_inferior_s": max(0, media - margem),
                 "ic95_superior_s": media + margem,
                 "intervalo_teorico_nao_truncado_inferior_s": media - margem}
        tabela.append(linha)
        print(f"{nome:<38} media={media:.6f}s DP={dp:.6f}s IC95=[{max(0, media-margem):.6f}, {media+margem:.6f}]s")
    Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
    with open(args.saida, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=tabela[0].keys())
        writer.writeheader()
        writer.writerows(tabela)
    print(f"\nResultados registrados em: {args.saida}")
    if not args.sem_grafico:
        gerar_grafico(Path(args.saida), Path(args.saida).parent / "tempos_algoritmos.png")


if __name__ == "__main__":
    main()
