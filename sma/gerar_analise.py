"""
Script para gerar análise de resultados: curva de aprendizagem e métricas de teste.
Gera gráficos e relatórios a partir dos dados CSV exportados.
"""
import csv
import argparse
from pathlib import Path
from typing import List, Dict
import matplotlib.pyplot as plt
import numpy as np


def carregar_csv(caminho: str) -> List[Dict]:
    """Carrega dados de um ficheiro CSV."""
    dados = []
    with open(caminho, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dados.append({
                'episodio': int(row['episodio']),
                'passos': int(row['passos']),
                'recompensa_total': float(row['recompensa_total']),
                'recompensa_descontada': float(row['recompensa_descontada']),
                'sucesso': row['sucesso'].lower() == 'true',
                'valor_total_depositado': float(row.get('valor_total_depositado', 0))
            })
    return dados


def calcular_media_movel(valores: List[float], janela: int = 10) -> List[float]:
    """Calcula média móvel para suavizar curva."""
    if len(valores) < janela:
        return valores
    
    medias = []
    for i in range(len(valores)):
        inicio = max(0, i - janela + 1)
        medias.append(np.mean(valores[inicio:i+1]))
    return medias


def gerar_curva_aprendizagem(caminho_csv: str, output_dir: Path, nome: str = "aprendizagem"):
    """Gera gráficos da curva de aprendizagem."""
    dados = carregar_csv(caminho_csv)
    
    if not dados:
        print(f"Nenhum dado encontrado em {caminho_csv}")
        return
    
    episodios = [d['episodio'] for d in dados]
    passos = [d['passos'] for d in dados]
    recompensas = [d['recompensa_total'] for d in dados]
    sucessos = [1 if d['sucesso'] else 0 for d in dados]
    
    passos_media = calcular_media_movel(passos, janela=10)
    recompensas_media = calcular_media_movel(recompensas, janela=10)
    taxa_sucesso_media = calcular_media_movel(sucessos, janela=10)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Curva de Aprendizagem - {nome}', fontsize=16, fontweight='bold')
    
    # 1. Passos por episódio
    ax1 = axes[0, 0]
    ax1.plot(episodios, passos, alpha=0.3, color='blue', label='Valor real')
    ax1.plot(episodios, passos_media, color='blue', linewidth=2, label='Média móvel (10)')
    ax1.set_xlabel('Episódio')
    ax1.set_ylabel('Passos')
    ax1.set_title('Passos por Episódio')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Recompensa por episódio
    ax2 = axes[0, 1]
    ax2.plot(episodios, recompensas, alpha=0.3, color='green', label='Valor real')
    ax2.plot(episodios, recompensas_media, color='green', linewidth=2, label='Média móvel (10)')
    ax2.set_xlabel('Episódio')
    ax2.set_ylabel('Recompensa Total')
    ax2.set_title('Recompensa por Episódio')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Taxa de sucesso (média móvel)
    ax3 = axes[1, 0]
    ax3.plot(episodios, taxa_sucesso_media, color='red', linewidth=2, label='Taxa de sucesso (média móvel)')
    ax3.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='50%')
    ax3.set_xlabel('Episódio')
    ax3.set_ylabel('Taxa de Sucesso')
    ax3.set_title('Taxa de Sucesso ao Longo do Tempo')
    ax3.set_ylim([0, 1.1])
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Estatísticas finais
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    total_ep = len(dados)
    sucessos_total = sum(sucessos)
    taxa_sucesso_final = sucessos_total / total_ep if total_ep > 0 else 0
    
    # Primeira metade vs segunda metade
    metade = total_ep // 2
    primeira_metade = dados[:metade] if metade > 0 else dados
    segunda_metade = dados[metade:] if metade > 0 else []
    
    stats_text = f"""
ESTATÍSTICAS GERAIS

Total de Episódios: {total_ep}
Taxa de Sucesso: {taxa_sucesso_final:.2%}

PRIMEIRA METADE:
  Passos médios: {np.mean([d['passos'] for d in primeira_metade]):.1f}
  Recompensa média: {np.mean([d['recompensa_total'] for d in primeira_metade]):.2f}
  Taxa sucesso: {sum(1 for d in primeira_metade if d['sucesso']) / len(primeira_metade) if primeira_metade else 0:.2%}

SEGUNDA METADE:
  Passos médios: {np.mean([d['passos'] for d in segunda_metade]):.1f if segunda_metade else 0:.1f}
  Recompensa média: {np.mean([d['recompensa_total'] for d in segunda_metade]):.2f if segunda_metade else 0:.2f}
  Taxa sucesso: {sum(1 for d in segunda_metade if d['sucesso']) / len(segunda_metade) if segunda_metade else 0:.2%}

MELHORIA:
  Passos: {np.mean([d['passos'] for d in primeira_metade]) - (np.mean([d['passos'] for d in segunda_metade]) if segunda_metade else 0):.1f}
  Recompensa: {np.mean([d['recompensa_total'] for d in segunda_metade]) - np.mean([d['recompensa_total'] for d in primeira_metade]) if segunda_metade else 0:.2f}
    """
    
    ax4.text(0.1, 0.5, stats_text, fontsize=10, family='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    output_path = output_dir / f"{nome}_curva_aprendizagem.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Gráfico guardado: {output_path}")
    
    plt.close()


def gerar_comparacao(caminho_fixa: str, caminho_aprendida: str, output_dir: Path):
    """Gera gráficos comparativos entre política fixa e aprendida."""
    dados_fixa = carregar_csv(caminho_fixa)
    dados_aprendida = carregar_csv(caminho_aprendida)
    
    if not dados_fixa or not dados_aprendida:
        print("Dados insuficientes para comparação")
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Comparação: Política Fixa Inteligente vs Q-Learning', fontsize=16, fontweight='bold')
    
    ep_fixa = [d['episodio'] for d in dados_fixa]
    ep_aprendida = [d['episodio'] for d in dados_aprendida]
    
    passos_fixa = [d['passos'] for d in dados_fixa]
    passos_aprendida = [d['passos'] for d in dados_aprendida]
    
    recomp_fixa = [d['recompensa_total'] for d in dados_fixa]
    recomp_aprendida = [d['recompensa_total'] for d in dados_aprendida]
    
    recomp_desc_fixa = [d['recompensa_descontada'] for d in dados_fixa]
    recomp_desc_aprendida = [d['recompensa_descontada'] for d in dados_aprendida]
    
    sucesso_fixa = [1 if d['sucesso'] else 0 for d in dados_fixa]
    sucesso_aprendida = [1 if d['sucesso'] else 0 for d in dados_aprendida]
    
    ax1 = axes[0, 0]
    ax1.bar(['Fixa Inteligente', 'Q-Learning'], 
            [np.mean(passos_fixa), np.mean(passos_aprendida)],
            color=['orange', 'blue'], alpha=0.7)
    ax1.errorbar(['Fixa Inteligente', 'Q-Learning'],
                 [np.mean(passos_fixa), np.mean(passos_aprendida)],
                 yerr=[np.std(passos_fixa), np.std(passos_aprendida)],
                 fmt='none', color='black', capsize=5)
    ax1.set_ylabel('Passos Médios')
    ax1.set_title('Passos Médios (Comparação)')
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax2 = axes[0, 1]
    passos_fixa_media = calcular_media_movel(passos_fixa, janela=5)
    passos_aprendida_media = calcular_media_movel(passos_aprendida, janela=5)
    ax2.plot(ep_fixa, passos_fixa, alpha=0.3, color='orange', label='Fixa (valores)')
    ax2.plot(ep_fixa, passos_fixa_media, color='orange', linewidth=2, label='Fixa Inteligente')
    ax2.plot(ep_aprendida, passos_aprendida, alpha=0.3, color='blue', label='Q-Learning (valores)')
    ax2.plot(ep_aprendida, passos_aprendida_media, color='blue', linewidth=2, label='Q-Learning')
    ax2.set_xlabel('Episódio')
    ax2.set_ylabel('Passos')
    ax2.set_title('Evolução dos Passos')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    ax3 = axes[0, 2]
    taxa_fixa = np.mean(sucesso_fixa)
    taxa_aprendida = np.mean(sucesso_aprendida)
    ax3.bar(['Fixa Inteligente', 'Q-Learning'],
            [taxa_fixa, taxa_aprendida],
            color=['orange', 'blue'], alpha=0.7)
    ax3.set_ylabel('Taxa de Sucesso')
    ax3.set_title('Taxa de Sucesso (Comparação)')
    ax3.set_ylim([0, 1.1])
    ax3.grid(True, alpha=0.3, axis='y')
    
    ax4 = axes[1, 0]
    ax4.bar(['Fixa Inteligente', 'Q-Learning'],
            [np.mean(recomp_fixa), np.mean(recomp_aprendida)],
            color=['orange', 'blue'], alpha=0.7)
    ax4.errorbar(['Fixa Inteligente', 'Q-Learning'],
                 [np.mean(recomp_fixa), np.mean(recomp_aprendida)],
                 yerr=[np.std(recomp_fixa), np.std(recomp_aprendida)],
                 fmt='none', color='black', capsize=5)
    ax4.set_ylabel('Recompensa Média')
    ax4.set_title('Recompensa Média (Comparação)')
    ax4.grid(True, alpha=0.3, axis='y')
    
    ax5 = axes[1, 1]
    recomp_fixa_media = calcular_media_movel(recomp_fixa, janela=5)
    recomp_aprendida_media = calcular_media_movel(recomp_aprendida, janela=5)
    ax5.plot(ep_fixa, recomp_fixa, alpha=0.3, color='orange', label='Fixa (valores)')
    ax5.plot(ep_fixa, recomp_fixa_media, color='orange', linewidth=2, label='Fixa Inteligente')
    ax5.plot(ep_aprendida, recomp_aprendida, alpha=0.3, color='blue', label='Q-Learning (valores)')
    ax5.plot(ep_aprendida, recomp_aprendida_media, color='blue', linewidth=2, label='Q-Learning')
    ax5.set_xlabel('Episódio')
    ax5.set_ylabel('Recompensa Total')
    ax5.set_title('Evolução da Recompensa')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    ax6 = axes[1, 2]
    recomp_desc_fixa_media = calcular_media_movel(recomp_desc_fixa, janela=5)
    recomp_desc_aprendida_media = calcular_media_movel(recomp_desc_aprendida, janela=5)
    ax6.plot(ep_fixa, recomp_desc_fixa, alpha=0.3, color='orange', label='Fixa (valores)')
    ax6.plot(ep_fixa, recomp_desc_fixa_media, color='orange', linewidth=2, label='Fixa Inteligente')
    ax6.plot(ep_aprendida, recomp_desc_aprendida, alpha=0.3, color='blue', label='Q-Learning (valores)')
    ax6.plot(ep_aprendida, recomp_desc_aprendida_media, color='blue', linewidth=2, label='Q-Learning')
    ax6.set_xlabel('Episódio')
    ax6.set_ylabel('Recompensa Descontada')
    ax6.set_title('Evolução da Recompensa Descontada')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_path = output_dir / "comparacao_politicas.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Gráfico de comparação guardado: {output_path}")
    
    plt.close()


def gerar_relatorio_texto(caminho_csv: str, output_dir: Path, nome: str = "relatorio"):
    """Gera relatório textual com estatísticas."""
    dados = carregar_csv(caminho_csv)
    
    if not dados:
        return
    
    total_ep = len(dados)
    sucessos = sum(1 for d in dados if d['sucesso'])
    taxa_sucesso = sucessos / total_ep if total_ep > 0 else 0
    
    passos = [d['passos'] for d in dados]
    recompensas = [d['recompensa_total'] for d in dados]
    
    # Dividir em quartis
    quartil = total_ep // 4
    q1 = dados[:quartil] if quartil > 0 else []
    q2 = dados[quartil:2*quartil] if quartil > 0 else []
    q3 = dados[2*quartil:3*quartil] if quartil > 0 else []
    q4 = dados[3*quartil:] if quartil > 0 else []
    
    relatorio = f"""
{'='*70}
RELATÓRIO DE ANÁLISE: {nome.upper()}
{'='*70}

ESTATÍSTICAS GERAIS
{'-'*70}
Total de Episódios: {total_ep}
Taxa de Sucesso: {taxa_sucesso:.2%} ({sucessos}/{total_ep})

Passos:
  Média: {np.mean(passos):.1f}
  Desvio Padrão: {np.std(passos):.1f}
  Mínimo: {min(passos)}
  Máximo: {max(passos)}

Recompensa:
  Média: {np.mean(recompensas):.2f}
  Desvio Padrão: {np.std(recompensas):.2f}
  Mínimo: {min(recompensas):.2f}
  Máximo: {max(recompensas):.2f}

ANÁLISE POR QUARTIS
{'-'*70}
"""
    
    for i, quartil_dados in enumerate([q1, q2, q3, q4], 1):
        if quartil_dados:
            q_passos = [d['passos'] for d in quartil_dados]
            q_recomp = [d['recompensa_total'] for d in quartil_dados]
            q_sucesso = sum(1 for d in quartil_dados if d['sucesso']) / len(quartil_dados)
            
            relatorio += f"""
Quartil {i} (Episódios {i*quartil-quartil+1 if quartil > 0 else 1} a {i*quartil if quartil > 0 else total_ep}):
  Passos médios: {np.mean(q_passos):.1f}
  Recompensa média: {np.mean(q_recomp):.2f}
  Taxa de sucesso: {q_sucesso:.2%}
"""
    
    relatorio += f"""
{'='*70}
"""
    
    output_path = output_dir / f"{nome}_relatorio.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print(relatorio)
    print(f"\nRelatório guardado: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Gera análise de resultados: curvas de aprendizagem e comparações"
    )
    parser.add_argument(
        "csv",
        type=str,
        help="Ficheiro CSV com resultados (ou 'comparar' para comparar dois ficheiros)"
    )
    parser.add_argument(
        "--comparar",
        type=str,
        help="Segundo ficheiro CSV para comparação"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="analise",
        help="Diretório de saída (padrão: analise)"
    )
    parser.add_argument(
        "--nome",
        type=str,
        help="Nome para identificar a análise"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.comparar:
        # Modo comparação
        nome = args.nome or "comparacao"
        gerar_comparacao(args.csv, args.comparar, output_dir)
        gerar_relatorio_texto(args.csv, output_dir, f"{nome}_fixa")
        gerar_relatorio_texto(args.comparar, output_dir, f"{nome}_aprendida")
    else:
        # Modo análise simples
        nome = args.nome or Path(args.csv).stem
        gerar_curva_aprendizagem(args.csv, output_dir, nome)
        gerar_relatorio_texto(args.csv, output_dir, nome)
    
    print(f"\n✅ Análise completa! Ficheiros guardados em: {output_dir}")


if __name__ == "__main__":
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("ERRO: matplotlib e numpy são necessários para gerar gráficos.")
        print("Instale com: pip install matplotlib numpy")
        exit(1)
    
    main()

