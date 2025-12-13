import csv
import math
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class MetricasEpisodio:
    passos: int = 0
    recompensa_total: float = 0.0
    recompensa_descontada: float = 0.0
    sucesso: bool = False
    valor_total_depositado: float = 0.0


class RegistadorResultados:
    def __init__(self, gama: float = 0.99):
        self.gama = gama
        self.ep = MetricasEpisodio()
        self._fator = 1.0
        self.historico: List[MetricasEpisodio] = []

    def iniciar_episodio(self):
        self.ep = MetricasEpisodio()
        self._fator = 1.0

    def registar_passo(self, recompensa: float, valor_depositado: float = 0.0):
        self.ep.passos += 1
        self.ep.recompensa_total += recompensa
        self.ep.recompensa_descontada += self._fator * recompensa
        self._fator *= self.gama
        self.ep.valor_total_depositado += valor_depositado

    def fechar_episodio(self) -> MetricasEpisodio:
        self.historico.append(self.ep)
        return self.ep

    def obter_estatisticas(self) -> dict:
        if not self.historico:
            return {}

        def media(lst):
            return sum(lst) / len(lst) if lst else 0

        def desvio(lst):
            if not lst:
                return 0
            m = media(lst)
            return math.sqrt(sum((x - m) ** 2 for x in lst) / len(lst))

        n = len(self.historico)
        sucessos = sum(1 for ep in self.historico if ep.sucesso)
        passos = [ep.passos for ep in self.historico]
        recomp = [ep.recompensa_total for ep in self.historico]
        recomp_desc = [ep.recompensa_descontada for ep in self.historico]

        return {
            'total_episodios': n,
            'taxa_sucesso': sucessos / n if n > 0 else 0,
            'passos_medio': media(passos),
            'passos_desvio': desvio(passos),
            'passos_min': min(passos, default=0),
            'passos_max': max(passos, default=0),
            'recompensa_media': media(recomp),
            'recompensa_desvio': desvio(recomp),
            'recompensa_descontada_media': media(recomp_desc),
            'recompensa_descontada_desvio': desvio(recomp_desc),
        }

    def imprimir_resumo(self):
        if not self.historico:
            print("\nNenhum episodio executado.")
            return

        stats = self.obter_estatisticas()
        print("\n" + "=" * 50)
        print("RESUMO")
        print("=" * 50)
        print(f"Episodios: {stats['total_episodios']}")
        print(f"Taxa sucesso: {stats['taxa_sucesso']:.2%}")
        print(f"\nPassos: {stats['passos_medio']:.1f} +/- {stats['passos_desvio']:.1f}")
        print(f"  min: {stats['passos_min']}, max: {stats['passos_max']}")
        print(f"\nRecompensa: {stats['recompensa_media']:.2f} +/- {stats['recompensa_desvio']:.2f}")
        print(f"Recompensa desc (g={self.gama}): {stats['recompensa_descontada_media']:.2f}")
        print("=" * 50)

    def exportarCSV(self, path: str):
        if not self.historico:
            print(f"Nada para exportar")
            return

        with open(path, 'w', newline='', encoding='utf-8') as f:
            campos = ['episodio'] + list(asdict(self.historico[0]).keys())
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for i, m in enumerate(self.historico, 1):
                writer.writerow({'episodio': i, **asdict(m)})

        print(f"Resultados exportados: {path}")
