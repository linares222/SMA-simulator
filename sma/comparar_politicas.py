"""
Script para comparar desempenho entre política fixa e política aprendida.
Executa a mesma simulação com ambas as políticas e compara os resultados.
"""
import json
import copy
from pathlib import Path
from sma.loader import carregar_simulacao


def executar_com_politica_fixa(cfg_path: str, num_episodios: int = 10):
    """Executa simulação com política fixa."""
    print("\n" + "="*70)
    print("EXECUTANDO COM POLÍTICA FIXA")
    print("="*70)
    
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    cfg_modificada = json.loads(json.dumps(cfg))
    
    if isinstance(cfg_modificada.get("agentes"), list):
        for ag_cfg in cfg_modificada["agentes"]:
            ag_cfg["politica"] = {
                "tipo": "fixa_inteligente"
            }
    
    cfg_modificada["modo_execucao"] = "TESTE"
    cfg_modificada["episodios"] = num_episodios
    
    temp_cfg = Path(cfg_path).parent / "temp_fixa.json"
    with open(temp_cfg, "w", encoding="utf-8") as f:
        json.dump(cfg_modificada, f, indent=2)
    
    try:
        sim = carregar_simulacao(str(temp_cfg), visual=False, episodios=num_episodios)
        sim.executa()
        stats = sim.registador_resultados.obter_estatisticas()
        return stats, copy.deepcopy(sim.registador_resultados.historico)
    finally:
        if temp_cfg.exists():
            temp_cfg.unlink()


def executar_com_politica_aprendida(cfg_path: str, num_episodios: int = 10):
    """Executa simulação com política aprendida (Q-Learning)."""
    print("\n" + "="*70)
    print("EXECUTANDO COM POLÍTICA APRENDIDA (Q-LEARNING)")
    print("="*70)
    print("NOTA: A Q-table deve ter sido treinada previamente em modo APRENDIZAGEM")
    
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    cfg_modificada = json.loads(json.dumps(cfg))
    
    if isinstance(cfg_modificada.get("agentes"), list):
        for ag_cfg in cfg_modificada["agentes"]:
            pol_original = ag_cfg.get("politica", {})
            ag_cfg["politica"] = {
                "tipo": "qlearning",
                "alfa": pol_original.get("alfa", 0.2),
                "gama": pol_original.get("gama", 0.95),
                "epsilon": 0.0  # Sem exploração em teste
            }
    
    cfg_modificada["modo_execucao"] = "TESTE"
    cfg_modificada["episodios"] = num_episodios
    
    temp_cfg = Path(cfg_path).parent / "temp_aprendida.json"
    with open(temp_cfg, "w", encoding="utf-8") as f:
        json.dump(cfg_modificada, f, indent=2)
    
    try:
        sim = carregar_simulacao(str(temp_cfg), visual=False, episodios=num_episodios)
        sim.executa()
        stats = sim.registador_resultados.obter_estatisticas()
        return stats, copy.deepcopy(sim.registador_resultados.historico)
    finally:
        if temp_cfg.exists():
            temp_cfg.unlink()


def comparar_resultados(stats_fixa: dict, stats_aprendida: dict):
    """Compara e imprime os resultados das duas políticas."""
    print("\n" + "="*70)
    print("COMPARAÇÃO: POLÍTICA FIXA vs POLÍTICA APRENDIDA")
    print("="*70)
    
    print(f"\n{'Métrica':<30} {'Fixa':<20} {'Aprendida':<20} {'Diferença':<15}")
    print("-" * 85)
    
    # Taxa de sucesso
    taxa_fixa = stats_fixa.get('taxa_sucesso', 0) * 100
    taxa_aprendida = stats_aprendida.get('taxa_sucesso', 0) * 100
    diff_taxa = taxa_aprendida - taxa_fixa
    print(f"{'Taxa de Sucesso (%)':<30} {taxa_fixa:<20.2f} {taxa_aprendida:<20.2f} {diff_taxa:+.2f}%")
    
    # Passos médios
    passos_fixa = stats_fixa.get('passos_medio', 0)
    passos_aprendida = stats_aprendida.get('passos_medio', 0)
    diff_passos = passos_aprendida - passos_fixa
    print(f"{'Passos Médios':<30} {passos_fixa:<20.1f} {passos_aprendida:<20.1f} {diff_passos:+.1f}")
    
    # Recompensa média
    recomp_fixa = stats_fixa.get('recompensa_media', 0)
    recomp_aprendida = stats_aprendida.get('recompensa_media', 0)
    diff_recomp = recomp_aprendida - recomp_fixa
    print(f"{'Recompensa Média':<30} {recomp_fixa:<20.2f} {recomp_aprendida:<20.2f} {diff_recomp:+.2f}")
    
    # Recompensa descontada
    recomp_desc_fixa = stats_fixa.get('recompensa_descontada_media', 0)
    recomp_desc_aprendida = stats_aprendida.get('recompensa_descontada_media', 0)
    diff_recomp_desc = recomp_desc_aprendida - recomp_desc_fixa
    print(f"{'Recompensa Descontada':<30} {recomp_desc_fixa:<20.2f} {recomp_desc_aprendida:<20.2f} {diff_recomp_desc:+.2f}")
    
    print("\n" + "="*70)
    
    print("\nANÁLISE:")
    melhoras = []
    pioras = []
    
    if diff_taxa > 0:
        melhoras.append(f"Taxa de sucesso melhorou {diff_taxa:.2f}%")
    elif diff_taxa < 0:
        pioras.append(f"Taxa de sucesso piorou {abs(diff_taxa):.2f}%")
    
    if diff_passos < 0:
        melhoras.append(f"Reduziu passos médios em {abs(diff_passos):.1f}")
    elif diff_passos > 0:
        pioras.append(f"Aumentou passos médios em {diff_passos:.1f}")
    
    if diff_recomp > 0:
        melhoras.append(f"Recompensa média aumentou {diff_recomp:.2f}")
    elif diff_recomp < 0:
        pioras.append(f"Recompensa média diminuiu {abs(diff_recomp):.2f}")
    
    if melhoras:
        print("✅ Melhorias com política aprendida:")
        for m in melhoras:
            print(f"   - {m}")
    
    if pioras:
        print("❌ Piorias com política aprendida:")
        for p in pioras:
            print(f"   - {p}")
    
    if not melhoras and not pioras:
        print("➡️  Desempenho similar entre as duas políticas")
    
    print()


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Compara política fixa vs política aprendida"
    )
    parser.add_argument(
        "config",
        type=str,
        help="Ficheiro de configuração (ex: config_farol.json)"
    )
    parser.add_argument(
        "--episodios", "-e",
        type=int,
        default=10,
        help="Número de episódios para teste (padrão: 10)"
    )
    
    args = parser.parse_args()
    
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"Erro: Ficheiro não encontrado: {cfg_path}")
        return 1
    
    stats_fixa, historico_fixa = executar_com_politica_fixa(
        str(cfg_path),
        args.episodios
    )
    
    stats_aprendida, historico_aprendida = executar_com_politica_aprendida(
        str(cfg_path),
        args.episodios
    )
    
    comparar_resultados(stats_fixa, stats_aprendida)
    
    base = Path(cfg_path).parent
    base.mkdir(parents=True, exist_ok=True)
    
    sim_temp = carregar_simulacao(str(cfg_path), visual=False, episodios=1)
    sim_temp.registador_resultados.historico = historico_fixa
    sim_temp.registador_resultados.exportarCSV(str(base / "resultados_fixa.csv"))
    
    sim_temp.registador_resultados.historico = historico_aprendida
    sim_temp.registador_resultados.exportarCSV(str(base / "resultados_aprendida.csv"))
    
    print("\nResultados exportados:")
    print(f"  - Política Fixa: {base / 'resultados_fixa.csv'}")
    print(f"  - Política Aprendida: {base / 'resultados_aprendida.csv'}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

