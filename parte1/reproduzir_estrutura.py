from pathlib import Path
import argparse
import gzip
import json
import re
from collections import Counter

import networkx as nx
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.sparse.csgraph import shortest_path

PASTA = Path(__file__).resolve().parent.parent
SAIDA = PASTA / "resultados"
SAIDA.mkdir(exist_ok=True)


def carregar(caminho):
    abre = gzip.open if str(caminho).lower().endswith('.gz') else open
    D = nx.DiGraph()
    arestas = []
    vertices_declarados = None
    with abre(caminho, 'rt', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith('#'):
                achado = re.search(r'\bNodes:\s*(\d+)', linha)
                if achado:
                    vertices_declarados = int(achado.group(1))
                continue
            if not linha:
                continue
            origem, destino = map(int, linha.split()[:2])
            arestas.append((origem, destino))
    D.add_edges_from(arestas)

    total = max(vertices_declarados or 0, max(D.nodes(), default=-1) + 1)
    D.add_nodes_from(range(total))
    return D, arestas


def distancias_completas(C):
    matriz = nx.to_scipy_sparse_array(C, format='csr', dtype=np.int8)
    soma, pares, excentricidades = 0, 0, []
    # Uma origem por vez evita guardar todas as distâncias em memória.
    for indice in range(matriz.shape[0]):
        dist = shortest_path(matriz, directed=False, unweighted=True, indices=indice)
        finitas = dist[np.isfinite(dist)]
        soma += float(finitas.sum())
        pares += len(finitas) - 1
        excentricidades.append(int(finitas.max()))
    return max(excentricidades), min(excentricidades), soma / pares


def figuras(G, graus, pasta):
    cont = Counter(int(k) for k in graus)
    ordem = sorted(cont)
    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    ax.bar(ordem, [cont[k] for k in ordem], width=0.85, linewidth=0)
    ax.set_yscale('log')
    ax.set_xlabel('Grau k (projeção não direcionada)')
    ax.set_ylabel('Número de vértices (escala logarítmica)')
    ax.set_title('Distribuição de graus da rede Gnutella05')
    ax.set_xlim(0, 90)
    ax.grid(axis='y', alpha=0.15)
    fig.tight_layout()
    fig.savefig(pasta / 'distribuicao_graus.png', dpi=220, bbox_inches='tight')
    plt.close(fig)

    central = max(G.degree(), key=lambda item: item[1])[0]
    vertices = {central} | set(G.neighbors(central))
    H = G.subgraph(vertices).copy()
    pos = nx.spring_layout(H, seed=217125521, iterations=110)
    fig, ax = plt.subplots(figsize=(7.0, 6.4))
    nx.draw_networkx_edges(H, pos, width=0.55, alpha=0.36, ax=ax)
    nx.draw_networkx_nodes(H, pos, nodelist=[u for u in H if u != central],
                           node_size=34, ax=ax, alpha=0.85)
    nx.draw_networkx_nodes(H, pos, nodelist=[central], node_size=165,
                           node_color='#c34b37', ax=ax)
    ax.annotate(f'Vértice {central}', xy=pos[central], xytext=(8, 8),
                textcoords='offset points', fontsize=10, weight='bold')
    ax.set_title('Vizinhança do vértice de maior grau (subgrafo induzido)')
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(pasta / 'visualizacao_rede.png', dpi=220, bbox_inches='tight')
    plt.close(fig)
    with (pasta / 'frequencias_graus.csv').open('w', encoding='utf-8') as arq:
        arq.write('grau,numero_de_vertices\n')
        for k in ordem:
            arq.write(f'{k},{cont[k]}\n')
    return central, H.number_of_nodes(), H.number_of_edges()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('arquivo', nargs='?', default=str(PASTA / 'dados' / 'p2p-Gnutella05.txt.gz'))
    args = parser.parse_args()
    D, arestas = carregar(Path(args.arquivo))
    G = D.to_undirected()
    loops = nx.number_of_selfloops(G)
    G.remove_edges_from(nx.selfloop_edges(G))
    componentes = sorted(nx.connected_components(G), key=len, reverse=True)
    C = G.subgraph(componentes[0]).copy()
    graus = np.asarray([k for _, k in G.degree()], dtype=np.int64)
    print('Calculando distâncias na maior componente...')
    diam, raio, caminho = distancias_completas(C)
    centro, nsub, msub = figuras(G, graus, SAIDA)

    E = set(arestas)
    dados = {
       'nome': 'p2p-Gnutella05', 
       'vertices': G.number_of_nodes(), 'arestas_dirigidas': D.number_of_edges(),
       'arestas_projecao': G.number_of_edges(), 'loops_encontrados': loops,
       'duplicatas_lista_original': len(arestas)-len(E),
       'arestas_reciprocas_lista_original': sum((v,u) in E for u,v in E),
       'grau_min': int(graus.min()), 'grau_max': int(graus.max()),
       'grau_medio': float(graus.mean()), 'grau_mediano': float(np.median(graus)),
       'densidade': nx.density(G),
       'numero_componentes': len(componentes),
       'tamanhos_componentes': [len(c) for c in componentes],
       'maior_componente_arestas': C.number_of_edges(),
       'diametro_maior_componente': diam,
       'raio_maior_componente': raio,
       'caminho_medio_maior_componente': caminho,
       'coeficiente_clusterizacao_medio': nx.average_clustering(G),
       'triangulos': sum(nx.triangles(G).values())//3,
       'visualizacao_vertice_central': centro,
       'visualizacao_vertices': nsub,
       'visualizacao_arestas': msub,
    }
    (SAIDA / 'resultados_estrutura.json').write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(dados, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
