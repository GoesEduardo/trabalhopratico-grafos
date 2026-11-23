from pathlib import Path
import argparse
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent


def gerar_grafico(entrada: Path, saida: Path) -> Path:
    entrada, saida = Path(entrada), Path(saida)
    if not entrada.is_file():
        raise FileNotFoundError(f'CSV não encontrado: {entrada}')
    with entrada.open('r', encoding='utf-8', newline='') as arquivo:
        linhas = list(csv.DictReader(arquivo))
    if not linhas:
        raise ValueError(f'CSV vazio: {entrada}')

    nomes = [r['algoritmo'] for r in linhas]
    medias = [1000 * float(r['media_s']) for r in linhas]
    limites = [1000 * max(0, float(r['ic95_inferior_s'])) for r in linhas]
    superiores = [1000 * float(r['ic95_superior_s']) for r in linhas]
    fig, ax = plt.subplots(figsize=(10, 6.3))
    ax.barh(
        range(len(nomes)), medias,
        xerr=[[m-l for m, l in zip(medias, limites)],
              [s-m for m, s in zip(medias, superiores)]],
        capsize=3
    )
    ax.set_yticks(range(len(nomes)), nomes, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Tempo médio em milissegundos (IC 95%)')
    ax.set_title('Tempos dos algoritmos — Gnutella05 (escopos distintos)')
    ax.grid(axis='x', alpha=.2)
    fig.tight_layout()
    saida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(saida, dpi=190, bbox_inches='tight')
    plt.close(fig)
    print('Gráfico gerado:', saida)
    return saida


def main():
    parser = argparse.ArgumentParser(description="Gráfico dos tempos dos algoritmos")
    parser.add_argument('--entrada', type=Path,
                        default=ROOT / 'resultados' / 'benchmark_reexecutado.csv')
    parser.add_argument('--saida', type=Path,
                        default=ROOT / 'resultados' / 'tempos_algoritmos.png')
    args = parser.parse_args()
    gerar_grafico(args.entrada, args.saida)


if __name__ == '__main__':
    main()
