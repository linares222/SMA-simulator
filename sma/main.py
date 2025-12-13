"""
Ponto de entrada principal do simulador.
"""
from pathlib import Path
from sma.loader import carregar_simulacao


if __name__ == "__main__":
    base = Path(__file__).parent
    
    sim = carregar_simulacao(str(base / "config_farol.json"))
    sim.executa()
    sim.registador_resultados.exportarCSV(str(base / "resultados.csv"))
