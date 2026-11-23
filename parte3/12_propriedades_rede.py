from __future__ import annotations

from pathlib import Path
import gzip
import json
import math
import random
import re
import statistics

import matplotlib
import networkx as nx
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.sparse.csgraph import shortest_path
from scipy.special import zeta

matplotlib.use('Agg')
import matplotlib.pyplot as plt


RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_DADOS = RAIZ / 'dados' / 'p2p-Gnutella05.txt.gz'
SAIDA = RAIZ / 'resultados'
SAIDA.mkdir(exist_ok=True)

SEED = 217125521
N_REFERENCIAS = 10
N_ORIGENS_REFERENCIA = 64
N_ENSAIOS_ROBUSTEZ = 30
N_ORIGENS_ROBUSTEZ = 40
FRACAO_REMOCAO = 0.05


def carregar_grafo():
    grafo = nx.Graph()
    vertices_declarados = None

    with gzip.open(CAMINHO_DADOS, 'rt', encoding='utf-8') as arquivo:
        for linha in arquivo:
            if linha.startswith('#'):
                achado = re.search(r'\bNodes:\s*(\d+)', linha)
                if achado:
                    vertices_declarados = int(achado.group(1))
                continue
            if not linha.strip():
                continue

            origem, destino = map(int, linha.split()[:2])
            if origem != destino:
                grafo.add_edge(origem, destino)

    total = max(
        vertices_declarados or 0,
        max(grafo.nodes(), default=-1) + 1,
    )
    grafo.add_nodes_from(range(total))
    return grafo


def clusterizacao_media(grafo):
    vizinhos = {vertice: set(grafo[vertice]) for vertice in grafo}
    total = 0.0

    for vertice, adjacentes in vizinhos.items():
        grau = len(adjacentes)
        if grau < 2:
            continue

        ligacoes_duplicadas = sum(
            len(vizinhos[vizinho] & adjacentes) for vizinho in adjacentes
        )
        total += ligacoes_duplicadas / (grau * (grau - 1))

    return total / grafo.number_of_nodes()


def caminho_medio_amostral(grafo, n_origens, gerador):
    maior = max(nx.connected_components(grafo), key=len)
    componente = grafo.subgraph(maior)
    if len(componente) < 2:
        return 0.0, len(componente)

    ordenados = sorted(componente.nodes())
    escolhidos = gerador.sample(
        range(len(ordenados)), min(n_origens, len(componente))
    )
    matriz = nx.to_scipy_sparse_array(
        componente, nodelist=ordenados, format='csr', dtype=np.int8
    )
    distancias = shortest_path(
        matriz, indices=escolhidos, directed=False, unweighted=True
    )
    return (
        float(distancias.sum()) / (len(escolhidos) * (len(componente) - 1)),
        len(componente),
    )


def analise_small_world(grafo):
    gerador = random.Random(SEED + 1)
    n, m = grafo.number_of_nodes(), grafo.number_of_edges()
    clusterizacao_real = clusterizacao_media(grafo)
    caminho_real = 4.596408883463596
    resultados = []

    for indice in range(N_REFERENCIAS):
        aleatorio = nx.gnm_random_graph(n, m, seed=SEED + 1000 + indice)
        clusterizacao = clusterizacao_media(aleatorio)
        caminho, tamanho = caminho_medio_amostral(
            aleatorio, N_ORIGENS_REFERENCIA, gerador
        )
        resultados.append({
            'replica': indice + 1,
            'clusterizacao': clusterizacao,
            'caminho_medio_estimado': caminho,
            'maior_componente': tamanho,
        })
        print(
            f'  Rede ER {indice + 1:2d}/{N_REFERENCIAS}: '
            f'C={clusterizacao:.6f}, L~{caminho:.4f} (LCC={tamanho})',
            flush=True,
        )

    clusterizacao_ref = statistics.mean(
        registro['clusterizacao'] for registro in resultados
    )
    caminho_ref = statistics.mean(
        registro['caminho_medio_estimado'] for registro in resultados
    )
    razao_clusterizacao = clusterizacao_real / clusterizacao_ref
    razao_caminho = caminho_real / caminho_ref
    sigma = razao_clusterizacao / razao_caminho

    with open(
        SAIDA / 'referencias_smallworld.csv', 'w', encoding='utf-8'
    ) as arquivo:
        arquivo.write(
            'replica,clusterizacao,caminho_medio_estimado,maior_componente\n'
        )
        for registro in resultados:
            arquivo.write(
                f"{registro['replica']},{registro['clusterizacao']},"
                f"{registro['caminho_medio_estimado']},"
                f"{registro['maior_componente']}\n"
            )

    figura, eixos = plt.subplots(1, 2, figsize=(10.3, 4.1))
    rotulos = ['Gnutella05', 'Erdos-Renyi\n(média de 10)']
    cores = ['#2872B2', '#A4B6C6']

    eixos[0].bar(
        rotulos, [clusterizacao_real, clusterizacao_ref], color=cores
    )
    eixos[0].set_ylabel('Clusterização média')
    eixos[0].set_title(
        f'Comparação de clusterização (razão {razao_clusterizacao:.1f}x)'
    )
    eixos[1].bar(rotulos, [caminho_real, caminho_ref], color=cores)
    eixos[1].set_ylim(0, max(caminho_real, caminho_ref) * 1.20)
    eixos[1].set_ylabel('Comprimento médio dos caminhos')
    eixos[1].set_title('Gnutella05: exato; ER: amostral')
    figura.suptitle(
        'Small-world: mesma quantidade de vértices e arestas', fontsize=12
    )
    figura.tight_layout()
    figura.savefig(
        SAIDA / 'smallworld_comparacao.png', dpi=200, bbox_inches='tight'
    )
    plt.close(figura)

    return {
        'C_real': clusterizacao_real,
        'L_real': caminho_real,
        'C_ER_media': clusterizacao_ref,
        'C_ER_dp': statistics.stdev(
            registro['clusterizacao'] for registro in resultados
        ),
        'L_ER_media_estimativa': caminho_ref,
        'L_ER_dp': statistics.stdev(
            registro['caminho_medio_estimado'] for registro in resultados
        ),
        'C_relativo': razao_clusterizacao,
        'L_relativo': razao_caminho,
        'sigma': sigma,
        'n_replicas_ER': N_REFERENCIAS,
        'origens_por_rede_ER': N_ORIGENS_REFERENCIA,
        'comparabilidade': (
            'mesmos n,m; C exato; L_Gnutella exato na maior CC; '
            'L_ER estimado por BFS na maior CC'
        ),
    }


def analise_lei_potencia(graus):
    valores = np.asarray(graus, dtype=np.int64)
    melhor = None
    ajustes = []

    for xmin in range(2, 21):
        cauda = valores[valores >= xmin]
        if len(cauda) < 80:
            continue

        soma_log = float(np.log(cauda).sum())

        def menos_log_verossimilhanca(alpha):
            return alpha * soma_log + len(cauda) * math.log(
                float(zeta(alpha, xmin))
            )

        resultado = minimize_scalar(
            menos_log_verossimilhanca,
            bounds=(1.01, 6.0),
            method='bounded',
            options={'xatol': 1e-10},
        )
        alpha = float(resultado.x)
        unicos = np.unique(cauda)
        empirica = np.array([(cauda >= grau).mean() for grau in unicos])
        modelo = zeta(alpha, unicos) / zeta(alpha, xmin)
        ks = float(np.max(np.abs(empirica - modelo)))
        registro = {
            'xmin': xmin,
            'expoente': alpha,
            'n_tail': len(cauda),
            'ks': ks,
            'loglik_powerlaw': -float(resultado.fun),
        }
        ajustes.append(registro)
        if melhor is None or ks < melhor['ks']:
            melhor = registro

    xmin = melhor['xmin']
    alpha = melhor['expoente']
    cauda = valores[valores >= xmin]
    deslocados = cauda - xmin
    q = float(deslocados.mean() / (1 + deslocados.mean()))
    verossimilhanca_geom = (
        len(cauda) * math.log(1 - q)
        + float(deslocados.sum()) * math.log(q)
        if q > 0 else 0.0
    )
    aic_potencia = 2 - 2 * melhor['loglik_powerlaw']
    aic_geometrica = 2 - 2 * verossimilhanca_geom
    valores_k = np.arange(1, valores.max() + 1)
    ccdf = np.array([(valores >= grau).mean() for grau in valores_k])

    from scipy.stats import linregress

    faixa_cauda = valores_k >= xmin
    ajuste_reta = linregress(
        np.log10(valores_k[faixa_cauda]),
        np.log10(ccdf[faixa_cauda]),
    )
    graus_cauda = valores_k[faixa_cauda]
    proporcao_cauda = cauda.size / valores.size
    potencia_teorica = (
        proporcao_cauda * zeta(alpha, graus_cauda) / zeta(alpha, xmin)
    )
    geometrica_teorica = proporcao_cauda * q ** (graus_cauda - xmin)

    figura, eixo = plt.subplots(figsize=(7.8, 5.0))
    eixo.loglog(
        valores_k, ccdf, 'o', ms=3, color='#334E68', alpha=0.75,
        label='CCDF observada',
    )
    eixo.loglog(
        graus_cauda, potencia_teorica, '-', lw=2, color='#D55A3A',
        label=f'Power law discreta (xmin={xmin}, alpha={alpha:.2f})',
    )
    eixo.loglog(
        graus_cauda, geometrica_teorica, '--', lw=1.7, color='#368965',
        label='Alternativa geométrica (cauda)',
    )
    eixo.axvline(xmin, color='gray', ls=':', lw=1)
    eixo.set_xlabel('Grau k, escala logarítmica')
    eixo.set_ylabel('P(K >= k), escala logarítmica')
    eixo.set_title('Cauda da distribuição: evidência exploratória')
    eixo.legend(fontsize=8)
    eixo.grid(which='major', alpha=0.17)
    figura.tight_layout()
    figura.savefig(
        SAIDA / 'powerlaw_ccdf.png', dpi=210, bbox_inches='tight'
    )
    plt.close(figura)

    with open(
        SAIDA / 'ajustes_powerlaw.csv', 'w', encoding='utf-8'
    ) as arquivo:
        arquivo.write(
            'xmin,alpha_mle,n_caudal,estatistica_ks,loglik_powerlaw\n'
        )
        for registro in ajustes:
            arquivo.write(
                f"{registro['xmin']},{registro['expoente']},"
                f"{registro['n_tail']},{registro['ks']},"
                f"{registro['loglik_powerlaw']}\n"
            )

    return {
        'xmin_selecionado': int(xmin),
        'expoente_mle': alpha,
        'n_caudal': int(len(cauda)),
        'fracao_caudal': float(len(cauda) / len(valores)),
        'KS_minimo': melhor['ks'],
        'inclinacao_CCDF_loglog': float(ajuste_reta.slope),
        'R2_CCDF_loglog': float(ajuste_reta.rvalue ** 2),
        'AIC_powerlaw_condicional': aic_potencia,
        'AIC_geometrica_condicional': aic_geometrica,
        'delta_AIC_geometrica_menos_powerlaw': aic_geometrica - aic_potencia,
        'ressalva': (
            'selecao xmin exploratoria; sem GOF bootstrap, '
            'sem prova de lei de potencia'
        ),
    }


def metricas_robustez(grafo, n_original, semente_origens):
    componentes = list(nx.connected_components(grafo))
    maior = max(componentes, key=len)
    n_restantes = grafo.number_of_nodes()
    gerador = random.Random(semente_origens)
    comprimento, _ = caminho_medio_amostral(
        grafo, N_ORIGENS_ROBUSTEZ, gerador
    )
    isolados = sum(grau == 0 for _, grau in grafo.degree())

    return {
        'fracao_gigante_remanescente': len(maior) / n_restantes,
        'fracao_gigante_original': len(maior) / n_original,
        'componentes': len(componentes),
        'distancia_media_amostral_maior_comp': comprimento,
        'fracao_isolados_remanescentes': isolados / n_restantes,
        'qtd_isolados': isolados,
        'tam_maior_comp': len(maior),
    }


def analise_robustez(grafo):
    n = grafo.number_of_nodes()
    r = math.ceil(FRACAO_REMOCAO * n)
    gerador = random.Random(SEED)
    vertices = sorted(grafo.nodes())
    ensaios = []

    for indice in range(N_ENSAIOS_ROBUSTEZ):
        removidos = gerador.sample(vertices, r)
        reduzido = grafo.copy()
        reduzido.remove_nodes_from(removidos)
        registro = metricas_robustez(reduzido, n, SEED + 10000 + indice)
        registro['ensaio'] = indice + 1
        ensaios.append(registro)
        if (indice + 1) % 5 == 0:
            print(
                f'  Robustez: {indice + 1:2d}/{N_ENSAIOS_ROBUSTEZ} '
                'ensaios aleatórios',
                flush=True,
            )

    ranking_graus = sorted(grafo.degree(), key=lambda par: (-par[1], par[0]))
    selecionados = [vertice for vertice, grau in ranking_graus[:r]]
    ataque_grafo = grafo.copy()
    ataque_grafo.remove_nodes_from(selecionados)
    ataque = metricas_robustez(ataque_grafo, n, SEED + 99999)

    componentes_originais = list(nx.connected_components(grafo))
    original = {
        'fracao_gigante_remanescente': max(
            len(componente) for componente in componentes_originais
        ) / n,
        'componentes': len(componentes_originais),
        'distancia_media_amostral_maior_comp': 4.596408883463596,
        'fracao_isolados_remanescentes': sum(
            grau == 0 for _, grau in grafo.degree()
        ) / n,
    }
    metricas = [
        'fracao_gigante_remanescente',
        'componentes',
        'distancia_media_amostral_maior_comp',
        'fracao_isolados_remanescentes',
    ]
    resumos = {}
    for chave in metricas:
        valores = [registro[chave] for registro in ensaios]
        resumos[chave] = {
            'media': statistics.mean(valores),
            'dp': statistics.stdev(valores),
            'min': min(valores),
            'max': max(valores),
            'ataque': ataque[chave],
            'original': original[chave],
        }

    with open(
        SAIDA / 'robustez_30_ensaios_com_distancias.csv',
        'w', encoding='utf-8',
    ) as arquivo:
        colunas = ['ensaio'] + list(ensaios[0].keys())[:-1]
        arquivo.write(','.join(colunas) + '\n')
        for registro in ensaios:
            arquivo.write(
                ','.join(str(registro[chave]) for chave in colunas) + '\n'
            )

    rotulos_eixos = [
        (
            'fracao_gigante_remanescente',
            'Maior componente / nós remanescentes',
        ),
        ('componentes', 'Número de componentes'),
        (
            'distancia_media_amostral_maior_comp',
            'Distância média na maior componente (amostra)',
        ),
        (
            'fracao_isolados_remanescentes',
            'Fração de isolados / nós remanescentes',
        ),
    ]
    fig, axs = plt.subplots(2, 2, figsize=(10.5, 7.8))
    for eixo, (chave, rotulo) in zip(axs.flat, rotulos_eixos):
        amostras = [registro[chave] for registro in ensaios]
        eixo.boxplot(
            [amostras], positions=[1], widths=0.35, showmeans=True,
            meanline=False, patch_artist=True,
            boxprops={'facecolor': '#C3D6E8', 'edgecolor': '#3A698E'},
            medianprops={'color': '#234A66'},
        )
        eixo.plot(
            2, ataque[chave], 'D', markersize=8, color='#C24E35',
            label='Ataque por grau',
        )
        eixo.axhline(
            original[chave], color='#76818A', linestyle='--',
            linewidth=1, label='Antes da remoção',
        )
        eixo.set_xlim(0.4, 2.55)
        eixo.set_xticks([1, 2], ['Aleatória (30)', 'Ataque (1)'])
        eixo.set_ylabel(rotulo, fontsize=9)
        eixo.grid(axis='y', alpha=0.15)

    fig.suptitle(
        f'Robustez: retirada de {r} vértices (5% arredondado para cima)',
        fontsize=12,
    )
    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(
        handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.95),
        ncol=2, fontsize=9, frameon=False,
    )
    fig.tight_layout()
    fig.subplots_adjust(top=0.86)
    fig.savefig(
        SAIDA / 'robustez_comparacao.png', bbox_inches='tight', dpi=300
    )
    plt.close(fig)

    return {
        'r_removidos': r,
        'fracao_removida_efetiva': r / n,
        'n_ensaios': N_ENSAIOS_ROBUSTEZ,
        'origens_por_ensaio_distancia': N_ORIGENS_ROBUSTEZ,
        'metricas': resumos,
        'ataque_por_grau': ataque,
        'baseline': original,
        'observacao_distancias': (
            'L apos remocao estimado em 40 origens aleatorias da maior '
            'componente por ensaio; aleatorios variam por semente; '
            'baseline exata'
        ),
        'ranking': (
            'grau total original, ordenacao unica decrescente, '
            'desempate por ID ascendente'
        ),
    }


def main():
    grafo = carregar_grafo()
    print(
        'Grafo:', grafo.number_of_nodes(),
        'vértices,', grafo.number_of_edges(), 'arestas', flush=True,
    )
    print('Small-world: referências Erdős-Rényi', flush=True)
    resultado_small_world = analise_small_world(grafo)
    print('Lei de potência: ajustes de cauda', flush=True)
    resultado_lei_potencia = analise_lei_potencia(
        [grau for _, grau in grafo.degree()]
    )
    print('Robustez: testes', flush=True)
    resultado_robustez = analise_robustez(grafo)
    resultado = {
        'metadata': {
            'dataset': 'p2p-Gnutella05', 'seed': SEED, 'data': '2002-08-05',
        },
        'small_world': resultado_small_world,
        'lei_potencia': resultado_lei_potencia,
        'robustez': resultado_robustez,
    }
    (SAIDA / 'resultados_propriedades.json').write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding='utf-8'
    )
    print(json.dumps(resultado, indent=2, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
