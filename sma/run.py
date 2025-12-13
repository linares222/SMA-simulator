#!/usr/bin/env python3
"""
Script principal para correr as simulacoes.
Uso: python -m sma.run [farol|foraging] [--visual] [--episodios N]
"""
import argparse
import sys
from pathlib import Path

from sma.loader import carregar_simulacao


def main():
    parser = argparse.ArgumentParser(description="Simulador Multi-Agente")
    parser.add_argument("ambiente", choices=["farol", "foraging"], help="Ambiente a simular")
    parser.add_argument("--visual", action="store_true", help="Mostrar visualizacao")
    parser.add_argument("--episodios", "-e", type=int, help="Nr de episodios")
    parser.add_argument("--config", "-c", type=str, help="Ficheiro de config alternativo")
    parser.add_argument("--output", "-o", type=str, help="Ficheiro CSV para resultados")
    parser.add_argument("--auto-export", action="store_true", help="Exportar CSV automaticamente após execução")
    parser.add_argument("--gerar-analise", action="store_true", help="Gerar análise e gráficos automaticamente")
    
    args = parser.parse_args()
    
    base = Path(__file__).parent
    
    if args.config:
        cfg_path = base / args.config
    else:
        cfg_path = base / f"config_{args.ambiente}.json"
    
    if not cfg_path.exists():
        print(f"Erro: config nao encontrado: {cfg_path}")
        return 1
    
    sim = carregar_simulacao(str(cfg_path), visual=args.visual, episodios=args.episodios)
    sim.executa()
    
    if args.output:
        out = base / args.output
        sim.registador_resultados.exportarCSV(str(out))
        csv_path = out
    elif args.auto_export or args.gerar_analise:
        modo = sim.modo.lower()
        timestamp = Path(cfg_path).stem
        csv_path = base / "resultados" / f"{timestamp}_{modo}.csv"
        csv_path.parent.mkdir(exist_ok=True)
        sim.registador_resultados.exportarCSV(str(csv_path))
    else:
        csv_path = None
    
    if args.gerar_analise and csv_path:
        try:
            from sma.gerar_analise import gerar_curva_aprendizagem, gerar_relatorio_texto
            output_dir = base / "analise"
            nome = f"{timestamp}_{modo}"
            gerar_curva_aprendizagem(str(csv_path), output_dir, nome)
            gerar_relatorio_texto(str(csv_path), output_dir, nome)
            print(f"\n✅ Análise gerada em: {output_dir}")
        except ImportError as e:
            print(f"\n⚠️  Não foi possível gerar análise: {e}")
            print("   Instale matplotlib e numpy: pip install matplotlib numpy")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

