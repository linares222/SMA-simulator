#!/usr/bin/env python3
"""
CLI Interativo para o Simulador Multi-Agente.
Uso: python -m sma.cli
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

import questionary
from questionary import Style

# Estilo personalizado para o CLI
CLI_STYLE = Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'bold'),
    ('answer', 'fg:green bold'),
    ('pointer', 'fg:cyan bold'),
    ('highlighted', 'fg:cyan bold'),
    ('selected', 'fg:green'),
    ('separator', 'fg:gray'),
    ('instruction', 'fg:gray'),
])


def mostrar_banner():
    """Mostra o banner inicial."""
    banner = """
==================================================
   SIMULADOR MULTI-AGENTE - CLI INTERATIVO
==================================================
"""
    print(banner)


def perguntar_ambiente() -> str:
    """Pergunta qual ambiente simular."""
    escolha = questionary.select(
        "Escolhe o ambiente a simular:",
        choices=["FAROL", "FORAGING"],
        style=CLI_STYLE,
    ).ask()
    
    if escolha is None:
        print("\nOperacao cancelada.")
        sys.exit(0)
    
    return escolha


def perguntar_modo() -> str:
    """Pergunta qual modo de execução."""
    escolha = questionary.select(
        "Escolhe o modo de execucao:",
        choices=["APRENDIZAGEM", "TESTE"],
        style=CLI_STYLE,
    ).ask()
    
    if escolha is None:
        print("\nOperacao cancelada.")
        sys.exit(0)
    
    return escolha


def perguntar_num_agentes() -> int:
    """Pergunta quantos agentes no total."""
    resposta = questionary.text(
        "Quantos agentes no total?",
        default="2",
        validate=lambda x: x.isdigit() and int(x) >= 1 or "Introduz um numero >= 1",
        style=CLI_STYLE,
    ).ask()
    
    if resposta is None:
        print("\nOperacao cancelada.")
        sys.exit(0)
    
    return int(resposta)


def perguntar_distribuicao_aprendizagem(total: int) -> int:
    """Pergunta quantos agentes aprendem (modo aprendizagem)."""
    while True:
        resposta = questionary.text(
            f"Quantos agentes aprendem (Q-Learning)? [0-{total}]",
            default=str(total),
            validate=lambda x: x.isdigit() and 0 <= int(x) <= total or f"Introduz um numero entre 0 e {total}",
            style=CLI_STYLE,
        ).ask()
        
        if resposta is None:
            print("\nOperacao cancelada.")
            sys.exit(0)
        
        n_qlearning = int(resposta)
        n_fixa = total - n_qlearning
        
        confirmacao = questionary.confirm(
            f"Confirmas? {n_qlearning} Q-Learning + {n_fixa} politica fixa = {total} total",
            default=True,
            style=CLI_STYLE,
        ).ask()
        
        if confirmacao is None:
            print("\nOperacao cancelada.")
            sys.exit(0)
        
        if confirmacao:
            return n_qlearning


def perguntar_distribuicao_teste(total: int) -> int:
    """Pergunta quantos agentes usam Q-table treinada (modo teste)."""
    while True:
        resposta = questionary.text(
            f"Quantos usam Q-table treinada? [0-{total}]",
            default=str(total),
            validate=lambda x: x.isdigit() and 0 <= int(x) <= total or f"Introduz um numero entre 0 e {total}",
            style=CLI_STYLE,
        ).ask()
        
        if resposta is None:
            print("\nOperacao cancelada.")
            sys.exit(0)
        
        n_qtable = int(resposta)
        n_fixa = total - n_qtable
        
        confirmacao = questionary.confirm(
            f"Confirmas? {n_qtable} Q-table + {n_fixa} politica fixa = {total} total",
            default=True,
            style=CLI_STYLE,
        ).ask()
        
        if confirmacao is None:
            print("\nOperacao cancelada.")
            sys.exit(0)
        
        if confirmacao:
            return n_qtable


def perguntar_episodios() -> int:
    """Pergunta quantos episodios."""
    resposta = questionary.text(
        "Quantos episodios?",
        default="100",
        validate=lambda x: x.isdigit() and int(x) >= 1 or "Introduz um numero >= 1",
        style=CLI_STYLE,
    ).ask()
    
    if resposta is None:
        print("\nOperacao cancelada.")
        sys.exit(0)
    
    return int(resposta)


def perguntar_max_passos() -> int:
    """Pergunta quantos passos maximos por episodio."""
    resposta = questionary.text(
        "Maximo de passos por episodio?",
        default="200",
        validate=lambda x: x.isdigit() and int(x) >= 10 or "Introduz um numero >= 10",
        style=CLI_STYLE,
    ).ask()
    
    if resposta is None:
        print("\nOperacao cancelada.")
        sys.exit(0)
    
    return int(resposta)


def perguntar_graficos() -> List[str]:
    """Pergunta quais gráficos mostrar."""
    mostrar = questionary.confirm(
        "Mostrar graficos no final?",
        default=True,
        style=CLI_STYLE,
    ).ask()
    
    if mostrar is None:
        print("\nOperacao cancelada.")
        sys.exit(0)
    
    if not mostrar:
        return []
    
    opcoes = [
        questionary.Choice("Curva de aprendizagem (recompensa)", value="recompensa", checked=True),
        questionary.Choice("Passos por episodio", value="passos", checked=False),
        questionary.Choice("Recompensa descontada", value="descontada", checked=False),
        questionary.Choice("Taxa de sucesso acumulada", value="sucesso", checked=False),
    ]
    
    selecionados = questionary.checkbox(
        "Seleciona os graficos (ESPACO para selecionar, ENTER para confirmar):",
        choices=opcoes,
        style=CLI_STYLE,
    ).ask()
    
    if selecionados is None:
        print("\nOperacao cancelada.")
        sys.exit(0)
    
    return selecionados


def gerar_config_dinamico(
    ambiente: str,
    modo: str,
    n_agentes: int,
    n_aprendizagem: int,
    episodios: int,
    max_passos: int,
) -> Dict[str, Any]:
    """Gera configuracao dinamica baseada nas escolhas do utilizador."""
    
    base_path = Path(__file__).parent
    
    template_path = base_path / f"config_{ambiente.lower()}.json"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        if ambiente == "FAROL":
            config = {
                "ambiente": {
                    "tipo": "FAROL",
                    "largura": 10,
                    "altura": 8,
                    "pos_farol": [7, 6]
                }
            }
        else:
            config = {
                "ambiente": {
                    "tipo": "FORAGING",
                    "largura": 10,
                    "altura": 8,
                    "ninho": [5, 4],
                    "recursos": [{"x": 2, "y": 2, "valor": 5}, {"x": 7, "y": 6, "valor": 10}]
                }
            }
    
    config["modo_execucao"] = modo
    config["episodios"] = episodios
    config["max_passos"] = max_passos
    config["visualizar"] = False
    
    largura = config["ambiente"]["largura"]
    altura = config["ambiente"]["altura"]
    
    posicoes = []
    for i in range(n_agentes):
        if i == 0:
            posicoes.append([0, 0])
        elif i == 1:
            posicoes.append([0, altura - 1])
        elif i == 2:
            posicoes.append([largura - 1, 0])
        elif i == 3:
            posicoes.append([largura - 1, altura - 1])
        else:
            posicoes.append([i % largura, (i * 2) % altura])
    
    agentes = []
    tipo_agente = "FAROL" if ambiente == "FAROL" else "FORAGER"
    id_prefix = "AgenteFarol" if ambiente == "FAROL" else "Forager"
    
    for i in range(n_agentes):
        agente = {
            "tipo": tipo_agente,
            "id": f"{id_prefix}_{i}",
            "posicao_inicial": posicoes[i],
        }
        
        if i < n_aprendizagem:
            agente["politica"] = {
                "tipo": "qlearning",
                "alfa": 0.3,
                "gama": 0.9,
                "epsilon": 0.2 if modo == "APRENDIZAGEM" else 0.0
            }
        else:
            agente["politica"] = {
                "tipo": "fixa_inteligente"
            }
        
        agentes.append(agente)
    
    config["agentes"] = agentes
    
    return config


def executar_simulacao(config: Dict[str, Any], graficos: List[str]):
    """Executa a simulação com a configuração fornecida."""
    import tempfile
    from sma.loader import carregar_simulacao
    
    base_path = Path(__file__).parent
    
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.json',
        delete=False,
        encoding='utf-8'
    ) as f:
        json.dump(config, f, indent=2)
        config_path = f.name
    
    print("\n" + "=" * 50)
    print("   INICIANDO SIMULACAO")
    print("=" * 50)
    print("\nConfiguracao:")
    print(f"   Ambiente: {config['ambiente']['tipo']}")
    print(f"   Modo: {config['modo_execucao']}")
    print(f"   Agentes: {len(config['agentes'])}")
    print(f"   Episodios: {config['episodios']}")
    print(f"   Max passos: {config['max_passos']}")
    print("\n" + "-" * 50 + "\n")
    
    try:
        sim = carregar_simulacao(
            config_path,
            visual=False,
            episodios=config['episodios']
        )
        sim.executa()
        
        resultados_dir = base_path / "resultados"
        resultados_dir.mkdir(exist_ok=True)
        
        modo = config['modo_execucao'].lower()
        ambiente = config['ambiente']['tipo'].lower()
        csv_path = resultados_dir / f"{ambiente}_{modo}_cli.csv"
        sim.registador_resultados.exportarCSV(str(csv_path))
        
        print(f"\nResultados guardados em: {csv_path}")
        
        print("\n" + "-" * 50)
        print("   EPISODIO FINAL (com visualizacao)")
        print("-" * 50 + "\n")
        
        executar_episodio_final_visual(config_path, config)
        
        if graficos:
            gerar_graficos_selecionados(str(csv_path), graficos, config)
        
    except Exception as e:
        print(f"\nErro durante a simulacao: {e}")
        raise
    finally:
        Path(config_path).unlink(missing_ok=True)


def executar_episodio_final_visual(config_path: str, config: Dict[str, Any]):
    """Executa um episódio final com visualização."""
    from sma.loader import carregar_simulacao
    
    try:
        sim = carregar_simulacao(
            config_path,
            visual=True,
            episodios=1
        )
        
        sim.carregar_politicas()
        
        for ag in sim.agentes:
            if hasattr(ag.politica, 'epsilon'):
                ag.politica.epsilon = 0.0
        
        sim.executa()
        
    except Exception as e:
        print(f"Aviso: Nao foi possivel mostrar visualizacao final: {e}")


def gerar_graficos_selecionados(csv_path: str, graficos: List[str], config: Dict[str, Any]):
    """Gera os graficos selecionados e guarda em ficheiro PNG."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import subprocess
        import platform
        from sma.gerar_analise import carregar_csv, calcular_media_movel
        
        dados = carregar_csv(csv_path)
        
        if not dados:
            print("Aviso: Sem dados para gerar graficos.")
            return
        
        episodios = [d['episodio'] for d in dados]
        
        n_graficos = len(graficos)
        if n_graficos == 0:
            return
        
        cols = min(2, n_graficos)
        rows = (n_graficos + 1) // 2
        
        fig, axes = plt.subplots(rows, cols, figsize=(7 * cols, 5 * rows))
        if n_graficos == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
        
        ambiente = config['ambiente']['tipo']
        modo = config['modo_execucao']
        fig.suptitle(f'Analise - {ambiente} ({modo})', fontsize=14, fontweight='bold')
        
        idx = 0
        
        if "recompensa" in graficos:
            recompensas = [d['recompensa_total'] for d in dados]
            recompensas_media = calcular_media_movel(recompensas, janela=10)
            ax = axes[idx]
            ax.plot(episodios, recompensas, alpha=0.3, color='green', label='Valor real')
            ax.plot(episodios, recompensas_media, color='green', linewidth=2, label='Media movel (10)')
            ax.set_xlabel('Episodio')
            ax.set_ylabel('Recompensa Total')
            ax.set_title('Curva de Aprendizagem (Recompensa)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            idx += 1
        
        if "passos" in graficos:
            passos = [d['passos'] for d in dados]
            passos_media = calcular_media_movel(passos, janela=10)
            ax = axes[idx]
            ax.plot(episodios, passos, alpha=0.3, color='blue', label='Valor real')
            ax.plot(episodios, passos_media, color='blue', linewidth=2, label='Media movel (10)')
            ax.set_xlabel('Episodio')
            ax.set_ylabel('Passos')
            ax.set_title('Passos por Episodio')
            ax.legend()
            ax.grid(True, alpha=0.3)
            idx += 1
        
        if "descontada" in graficos:
            descontada = [d['recompensa_descontada'] for d in dados]
            descontada_media = calcular_media_movel(descontada, janela=10)
            ax = axes[idx]
            ax.plot(episodios, descontada, alpha=0.3, color='purple', label='Valor real')
            ax.plot(episodios, descontada_media, color='purple', linewidth=2, label='Media movel (10)')
            ax.set_xlabel('Episodio')
            ax.set_ylabel('Recompensa Descontada')
            ax.set_title('Recompensa Descontada')
            ax.legend()
            ax.grid(True, alpha=0.3)
            idx += 1
        
        if "sucesso" in graficos:
            sucessos = [1 if d['sucesso'] else 0 for d in dados]
            taxa_acumulada = []
            for i in range(len(sucessos)):
                taxa_acumulada.append(sum(sucessos[:i+1]) / (i + 1))
            ax = axes[idx]
            ax.plot(episodios, taxa_acumulada, color='red', linewidth=2)
            ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='50%')
            ax.set_xlabel('Episodio')
            ax.set_ylabel('Taxa de Sucesso')
            ax.set_title('Taxa de Sucesso Acumulada')
            ax.set_ylim([0, 1.1])
            ax.legend()
            ax.grid(True, alpha=0.3)
            idx += 1
        
        for i in range(idx, len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        
        base_path = Path(__file__).parent
        analise_dir = base_path / "analise"
        analise_dir.mkdir(exist_ok=True)
        
        output_file = analise_dir / f"{ambiente.lower()}_{modo.lower()}_graficos.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"\nGraficos guardados em: {output_file}")
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(output_file)], check=True)
            elif platform.system() == 'Windows':
                subprocess.run(['start', '', str(output_file)], shell=True, check=True)
            else:  # Linux
                subprocess.run(['xdg-open', str(output_file)], check=True)
            print("Ficheiro aberto no visualizador de imagens.")
        except Exception:
            print("Abre o ficheiro manualmente para ver os graficos.")
        
    except ImportError:
        print("\nAviso: Nao foi possivel gerar graficos. Instale matplotlib: pip install matplotlib")
    except Exception as e:
        print(f"\nAviso: Erro ao gerar graficos: {e}")


def main():
    """Função principal do CLI."""
    mostrar_banner()
    
    ambiente = perguntar_ambiente()
    modo = perguntar_modo()
    n_agentes = perguntar_num_agentes()
    
    if modo == "APRENDIZAGEM":
        n_aprendizagem = perguntar_distribuicao_aprendizagem(n_agentes)
    else:
        n_aprendizagem = perguntar_distribuicao_teste(n_agentes)
    
    episodios = perguntar_episodios()
    max_passos = perguntar_max_passos()
    graficos = perguntar_graficos()
    
    config = gerar_config_dinamico(
        ambiente=ambiente,
        modo=modo,
        n_agentes=n_agentes,
        n_aprendizagem=n_aprendizagem,
        episodios=episodios,
        max_passos=max_passos,
    )
    
    executar_simulacao(config, graficos)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulacao cancelada pelo utilizador (Ctrl+C).")
        sys.exit(0)
