# G56 — Análise de grafos: rede Gnutella05

**Estudante:** Eduardo dos Santos Góes  
**Matrícula:** 217125521  
**Instituição:** Universidade Federal da Bahia (UFBA)  
**Dataset:** [Stanford SNAP — p2p-Gnutella05](https://snap.stanford.edu/data/p2p-Gnutella05.html)

Este repositório contém os **códigos e scripts utilizados no trabalho**, o **dataset original e suas versões tratadas** e as instruções para **reproduzir os experimentos das Partes I, II e III**. O artigo em LaTeX e o relatório PDF são mantidos fora deste repositório, pois são entregues separadamente.

## Como reproduzir o trabalho (comandos principais)

Abra o terminal **na pasta raiz deste repositório**. Após instalar as dependências, os três comandos abaixo executam **as análises computacionais exigidas em cada parte**:

| Parte do enunciado | Arquivo executor | O que executa |
|---|---|---|
| **Parte I — Análise Estrutural Obrigatória** | `parte1/reproduzir_estrutura.py` | Calcula as métricas estruturais obrigatórias e gera distribuição de graus e visualização da rede. |
| **Parte II — Algoritmos da Disciplina** | `parte2/10_benchmark.py` | Executa os **nove algoritmos**, mede seus tempos repetidamente, calcula média, desvio padrão e IC95% e **gera o gráfico de desempenho**. |
| **Parte III — Análise Estrutural** | `parte3/12_propriedades_rede.py` | Executa **Small-World, investigação de lei de potência e robustez** (remoção aleatória e direcionada de 5%). |

### 1. Instalar as dependências

É necessário **Python 3.10 ou superior**. Execute uma única vez:

```bash
python -m pip install -r requirements.txt
```

> No Windows, caso `python` não seja reconhecido, use `py` no lugar de `python`.

### 2. Executar as três partes

```bash
# Parte I: métricas estruturais e gráficos
python parte1/reproduzir_estrutura.py

# Parte II: nove algoritmos, 30 medições por algoritmo, estatísticas e gráfico
python parte2/10_benchmark.py --repeticoes 30

# Parte III: pequeno mundo, lei de potência e robustez
python parte3/12_propriedades_rede.py
```

**Os três comandos são independentes:** cada executor lê o arquivo original localizado em `dados/` e realiza internamente as transformações necessárias. Não é preciso executar `00_preparar_dados.py` antes deles.

Todos os resultados gerados são armazenados automaticamente em **`resultados/`**, pasta criada na primeira execução. Essa pasta é ignorada pelo Git porque pode ser recriada. **As três execuções não escrevem automaticamente o texto do relatório científico**: o relatório interpreta e apresenta os resultados produzidos pelos scripts.

> **Tempo de execução:** as rotinas podem demorar, especialmente as distâncias exatas da Parte I, as 30 repetições da Parte II e os experimentos da Parte III. Os tempos dependem do computador.

## Como o grafo foi atribuído

Conforme a regra do enunciado, a soma dos dígitos da matrícula **217125521** é 26 e os últimos dois dígitos são 21:

```text
f(M) = (26 × (21 + 1)) mod 129 = 56
```

O cálculo determina o **índice G56**, cuja correspondência com **p2p-Gnutella05** foi informada a partir da planilha `ANALISANDO-SNAP-DATASET` da disciplina. **A fórmula escolhe o índice; a planilha identifica o dataset correspondente.**

## Organização dos arquivos

```text
G56_Gnutella05/
├── README.md
├── requirements.txt
├── .gitignore
├── dados/
│   ├── p2p-Gnutella05.txt.gz
│   ├── p2p-Gnutella05_tratado_nao_dirigido.txt.gz
│   └── p2p-Gnutella05_tratado_maior_componente.txt.gz
├── parte1/
│   ├── 00_preparar_dados.py
│   └── reproduzir_estrutura.py            # EXECUTOR DA PARTE I
├── parte2/
│   ├── comum.py
│   ├── 01_bfs.py
│   ├── 02_dfs.py
│   ├── 03_eulerianidade.py
│   ├── 04_dijkstra.py
│   ├── 05_bellman_ford.py
│   ├── 06_floyd_warshall.py
│   ├── 07_tarjan.py
│   ├── 08_prim.py
│   ├── 09_kruskal.py
│   ├── 10_benchmark.py                      # EXECUTOR DA PARTE II
│   ├── 11_validar_algoritmos.py
│   └── gerar_grafico_tempos.py
└── parte3/
    ├── 12_propriedades_rede.py            # EXECUTOR DA PARTE III
    └── 13_modelos_classicos.py             # Questão extra (opcional)
```

### Parte I — Análise Estrutural Obrigatória

**Executor:** `python parte1/reproduzir_estrutura.py`

Calcula número de vértices e arestas, grau mínimo/máximo/médio, distribuição de graus, densidade, quantidade e tamanho das componentes conexas, diâmetro, raio, comprimento médio dos caminhos, clusterização média e triângulos. Também produz uma visualização reduzida. Os arquivos principais são:

- `resultados/resultados_estrutura.json`: métricas numéricas;
- `resultados/frequencias_graus.csv`: distribuição de graus;
- `resultados/distribuicao_graus.png`: histograma;
- `resultados/visualizacao_rede.png`: representação do subgrafo de visualização.

**Tratamento:** o grafo original é direcionado (8.846 vértices e 31.839 arestas). A projeção simples não direcionada mantém esses quantitativos, e apresenta três componentes conexas de tamanhos 8.842, 2 e 2. As distâncias, o diâmetro e o raio são **calculados exatamente na maior componente conexa**, pois a rede completa não é conexa.

**Arquivo auxiliar:** `parte1/00_preparar_dados.py` **não é necessário antes do executor**. Sua finalidade é refazer e salvar as duas versões tratadas do grafo; use-o apenas se quiser regenerar esses arquivos:

```bash
python parte1/00_preparar_dados.py
```

Os arquivos `dados/p2p-Gnutella05_tratado_nao_dirigido.txt.gz` e `dados/p2p-Gnutella05_tratado_maior_componente.txt.gz` foram incluídos para disponibilizar os dados após tratamento, conforme o enunciado. Os scripts carregam o original e refazem as projeções em memória.

### Parte II — Algoritmos da Disciplina

**Executor:** `python parte2/10_benchmark.py --repeticoes 30`

Este script executa **BFS, DFS, Eulerianidade, Dijkstra, Bellman-Ford, Floyd-Warshall, Tarjan, Prim e Kruskal**, usando as implementações separadas. Também mede os tempos com `time.perf_counter()`, calcula **média, desvio padrão amostral e IC95%** e agora produz automaticamente:

- `resultados/benchmark_reexecutado.csv`: tabela dos tempos, complexidades e intervalos de confiança;
- `resultados/tempos_algoritmos.png`: gráfico dos tempos com IC95%.

Com **30 ou mais repetições**, o IC95% usa o valor crítico normal **Z = 1,96**; com menos de 30 e desvio populacional desconhecido, utiliza **t-Student**. O programa aceita `--sem-grafico` para executar apenas o benchmark.

Cada algoritmo pode ser executado individualmente, por exemplo:

```bash
python parte2/01_bfs.py --origem 0
python parte2/04_dijkstra.py --origem 0
python parte2/07_tarjan.py
```

**Arquivo compartilhado:** `parte2/comum.py` lê o dataset e constrói as listas de adjacência. Não é um algoritmo e não precisa ser executado sozinho.

**Verificação opcional de correção:**

```bash
python parte2/11_validar_algoritmos.py
```

O validador compara resultados de buscas e caminhos mínimos e confere propriedades conhecidas da rede e das florestas geradoras. **Não substitui o benchmark** e não representa uma prova formal de correção geral.

**Gráfico isoladamente (opcional):**

```bash
python parte2/gerar_grafico_tempos.py
```

Não é necessário após o benchmark atualizado: o gráfico já é gerado automaticamente.

**Limitações importantes:** as arestas recebem peso unitário porque o dataset não informa pesos. Bellman-Ford é medido em um subgrafo induzido de **250 vértices** e Floyd-Warshall em um de **80 vértices**, para limitar o custo computacional. Seus tempos **não devem ser comparados diretamente** aos dos algoritmos executados no grafo inteiro.

### Parte III — Análise Estrutural

**Executor:** `python parte3/12_propriedades_rede.py`

Esse comando executa todas as **análises computacionais obrigatórias da Parte III**:

1. **Rede de pequeno mundo (Small-World):** compara coeficiente de clusterização e comprimento médio dos caminhos com dez grafos aleatórios de mesmo número de vértices e arestas.
2. **Lei de potência:** ajusta exploratoriamente a cauda da distribuição de graus e gera uma figura em escala log-log.
3. **Robustez:** remove 5% dos vértices em 30 ensaios aleatórios e uma remoção direcionada por grau, comparando tamanho da maior componente, número de componentes, distâncias e vértices isolados.

Os arquivos principais são `resultados/resultados_propriedades.json`, `resultados/smallworld_comparacao.png`, `resultados/powerlaw_ccdf.png`, `resultados/robustez_comparacao.png` e os CSVs com dados dos ensaios.

**Ressalvas metodológicas:** as distâncias das referências aleatórias e dos experimentos de robustez são estimadas por amostragem; o ajuste exploratório de lei de potência não demonstra aderência estatística definitiva. A interpretação, a descoberta principal e a discussão das limitações são redigidas no artigo.

**Questão extra, opcional:** a comparação com Erdős–Rényi, Barabási–Albert e Watts–Strogatz é executada separadamente:

```bash
python parte3/13_modelos_classicos.py
```

O script adicional salva `resultados/comparacao_modelos_classicos.csv` e `.json`. Por ser uma **questão extra**, não faz parte do executor principal dos requisitos obrigatórios.

## Publicação e entrega

O repositório contém somente os códigos, os dados e as instruções necessários à reprodução. O PDF científico deve ser enviado separadamente pelo Moodle, como **`217125521.pdf`**, incluindo no próprio artigo o link público deste repositório.
