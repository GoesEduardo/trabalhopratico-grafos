from pathlib import Path
import gzip
import re
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'dados'
ORIGINAL = DATA / 'p2p-Gnutella05.txt.gz'

def escrever_gzip(arquivo, g, descricao):
    with gzip.open(arquivo, 'wt', encoding='utf-8') as saida:
        saida.write('# ' + descricao + '\n')
        saida.write(f'# Nodes: {g.number_of_nodes()} Edges: {g.number_of_edges()}\n')
        saida.write('# FromNodeId\tToNodeId\n')
        for origem, destino in sorted(tuple(sorted(aresta)) for aresta in g.edges()):
            saida.write(f'{origem}\t{destino}\n')


def main():
    dirigido = nx.DiGraph()
    vertices_declarados = None
    with gzip.open(ORIGINAL, 'rt', encoding='utf-8') as arquivo:
        for linha in arquivo:
            if linha.startswith('#'):
                achado = re.search(r'\bNodes:\s*(\d+)', linha)
                if achado:
                    vertices_declarados = int(achado.group(1))
                continue
            if not linha.strip():
                continue
            origem, destino = map(int, linha.split()[:2])
            dirigido.add_edge(origem, destino)
    total = max(vertices_declarados or 0, max(dirigido.nodes(), default=-1) + 1)
    dirigido.add_nodes_from(range(total))
    nao_dirigido = dirigido.to_undirected()
    nao_dirigido.remove_edges_from(nx.selfloop_edges(nao_dirigido))
    componente = max(nx.connected_components(nao_dirigido), key=len)
    maior_comp = nao_dirigido.subgraph(componente).copy()
    escrever_gzip(DATA / 'p2p-Gnutella05_tratado_nao_dirigido.txt.gz', nao_dirigido,
                  'Projeção simples não direcionada; IDs originais preservados')
    escrever_gzip(DATA / 'p2p-Gnutella05_tratado_maior_componente.txt.gz', maior_comp,
                  'Maior componente conexa da projeção não direcionada; IDs originais preservados')
    print('Original dirigido:', dirigido.number_of_nodes(), dirigido.number_of_edges())
    print('Projeção não direcionada:', nao_dirigido.number_of_nodes(), nao_dirigido.number_of_edges())
    print('Maior componente:', maior_comp.number_of_nodes(), maior_comp.number_of_edges())

if __name__ == '__main__':
    main()
