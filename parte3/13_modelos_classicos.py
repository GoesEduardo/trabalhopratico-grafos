from pathlib import Path
import csv
import json
import random
import statistics
from importlib import import_module

import networkx as nx


propriedades = import_module('12_propriedades_rede')
RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / 'resultados'
SAIDA.mkdir(exist_ok=True)

grafo_real = propriedades.carregar_grafo()
comparacoes = []


def adicionar_modelo(nome, grafo):
    graus = [grau for _, grau in grafo.degree()]
    caminho, gigante = propriedades.caminho_medio_amostral(
        grafo, 40,
        random.Random(propriedades.SEED + 791 + len(comparacoes)),
    )
    registro = {
        'modelo': nome,
        'vertices': grafo.number_of_nodes(),
        'arestas': grafo.number_of_edges(),
        'grau_medio': statistics.mean(graus),
        'grau_max': max(graus),
        'dp_grau': statistics.stdev(graus),
        'clusterizacao': propriedades.clusterizacao_media(grafo),
        'caminho_medio_maior_comp_amostral': caminho,
        'tam_maior_comp': gigante,
    }
    comparacoes.append(registro)
    print(
        nome, 'm=', registro['arestas'],
        'kmax=', registro['grau_max'],
        'C=', round(registro['clusterizacao'], 6),
        'L=', round(caminho, 4), flush=True,
    )


adicionar_modelo('Gnutella05', grafo_real)
adicionar_modelo(
    'Erdos-Renyi G(n,m)',
    nx.gnm_random_graph(
        grafo_real.number_of_nodes(), grafo_real.number_of_edges(),
        seed=propriedades.SEED + 1100,
    ),
)
adicionar_modelo(
    'Barabasi-Albert m=4',
    nx.barabasi_albert_graph(
        grafo_real.number_of_nodes(), 4, seed=propriedades.SEED + 1101,
    ),
)
adicionar_modelo(
    'Watts-Strogatz k=8 p=0.70',
    nx.watts_strogatz_graph(
        grafo_real.number_of_nodes(), 8, 0.70,
        seed=propriedades.SEED + 1102,
    ),
)

colunas = list(comparacoes[0].keys())
with open(
    SAIDA / 'comparacao_modelos_classicos.csv',
    'w', newline='', encoding='utf-8',
) as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=colunas)
    escritor.writeheader()
    escritor.writerows(comparacoes)

with open(
    SAIDA / 'comparacao_modelos_classicos.json', 'w', encoding='utf-8'
) as arquivo:
    json.dump(comparacoes, arquivo, indent=2, ensure_ascii=False)
