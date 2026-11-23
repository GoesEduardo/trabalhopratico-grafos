from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
import argparse
import gzip
import re

DADOS_PADRAO = Path(__file__).resolve().parent.parent / "dados" / "p2p-Gnutella05.txt.gz"


@dataclass
class Grafo:
    n: int
    arestas: list[tuple[int, int]]
    saida: list[list[int]]
    entrada: list[list[int]]
    nao_dirigido: list[list[int]]

    @property
    def m(self) -> int:
        return len(self.arestas)


def carregar(caminho: str | Path = DADOS_PADRAO) -> Grafo:
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(f"Dataset não encontrado: {caminho}")
    abrir = gzip.open if caminho.suffix == ".gz" else open
    arestas: list[tuple[int, int]] = []
    declarados: int | None = None
    with abrir(caminho, "rt", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha:
                continue
            if linha.startswith("#"):
                achado = re.search(r"\bNodes:\s*(\d+)", linha)
                if achado:
                    declarados = int(achado.group(1))
                continue
            u, v = (int(x) for x in linha.split()[:2])
            if u < 0 or v < 0:
                raise ValueError("Este carregador espera IDs de vértices não negativos")
            arestas.append((u, v))
    maximo = max((max(u, v) for u, v in arestas), default=-1)
    n = max(maximo + 1, declarados or 0)
    saida = [[] for _ in range(n)]
    entrada = [[] for _ in range(n)]
    und = [set() for _ in range(n)]
    arestas_unicas: list[tuple[int, int]] = []
    vistos: set[tuple[int, int]] = set()
    for u, v in arestas:
        if (u, v) in vistos:
            continue
        vistos.add((u, v))
        saida[u].append(v)
        entrada[v].append(u)
        arestas_unicas.append((u, v))
        if u != v:
            und[u].add(v)
            und[v].add(u)
    return Grafo(n, arestas_unicas,
                 [sorted(v) for v in saida],
                 [sorted(v) for v in entrada],
                 [sorted(v) for v in und])


def argumentos_base(descricao: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=descricao)
    parser.add_argument("--dados", default=str(DADOS_PADRAO),
                        help="Arquivo p2p-Gnutella05.txt.gz ou .txt")
    return parser


def conjunto_alcancavel(adjacencia: list[list[int]], origem: int) -> list[int]:
    if origem < 0 or origem >= len(adjacencia):
        raise ValueError("ID de origem fora do intervalo")
    visitados = {origem}
    fila = deque([origem]); ordem = []
    while fila:
        u = fila.popleft(); ordem.append(u)
        for v in adjacencia[u]:
            if v not in visitados:
                visitados.add(v)
                fila.append(v)
    return ordem


def amostra_bfs(grafo: Grafo, origem: int, quantidade: int) -> list[int]:
    if quantidade < 1:
        raise ValueError("A quantidade deve ser positiva")
    ordem = conjunto_alcancavel(grafo.nao_dirigido, origem)
    if len(ordem) < quantidade:
        outros = [u for u in range(grafo.n) if u not in set(ordem)]
        ordem.extend(outros)
    return ordem[:quantidade]


def induzido(adjacencia: list[list[int]], nos: list[int]) -> list[list[int]]:
    mapa = {u: i for i, u in enumerate(nos)}
    return [[mapa[v] for v in adjacencia[u] if v in mapa] for u in nos]
