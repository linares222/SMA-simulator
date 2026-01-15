#!/usr/bin/env python3
"""
CLI Interativo para o Simulador Multi-Agente.
Uso: python -m sma.cli
"""

import json
import random
import sys
from pathlib import Path
from typing import Dict, Any, List

import questionary
from questionary import Style

from sma.analise_limitacoes import demonstrar_limitacoes
from sma.analise_qtables import analisar_qtables

CLI_STYLE = Style(
    [
        ("qmark", "fg:cyan bold"),
        ("question", "bold"),
        ("answer", "fg:green bold"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "fg:cyan bold"),
        ("selected", "fg:green"),
        ("separator", "fg:gray"),
        ("instruction", "fg:gray"),
    ]
)


def mostrar_banner():
    """Mostra o banner inicial."""
    banner = """
==================================================
   SIMULADOR MULTI-AGENTE - CLI INTERATIVO
==================================================
"""
    print(banner)


def perguntar_modo_operacao() -> str:
    """Pergunta se quer executar simulação normal ou comparar políticas."""
    escolha = questionary.select(
        "Escolhe o modo de operacao:",
        choices=[
            "Executar simulacao",
            "Comparar politicas (Fixa Inteligente vs Q-Learning)",
            "Analise Avancada",
        ],
        style=CLI_STYLE,
    ).ask()

    if escolha is None:
        print("\nOperacao cancelada.")
        sys.exit(0)

    return escolha


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


def perguntar_distribuicao_aprendizagem(total: int, algoritmo: str) -> int:
    """Pergunta quantos agentes aprendem."""
    nome_alg = "Q-Learning" if algoritmo == "qlearning" else "Algoritmo Genetico"
    while True:
        resposta = questionary.text(
            f"Quantos agentes aprendem ({nome_alg})? [0-{total}]",
            default=str(total),
            validate=lambda x: x.isdigit()
            and 0 <= int(x) <= total
            or f"Introduz um numero entre 0 e {total}",
            style=CLI_STYLE,
        ).ask()

        if resposta is None:
            print("\nOperacao cancelada.")
            sys.exit(0)

        n_aprendizagem = int(resposta)
        n_fixa = total - n_aprendizagem

        confirmacao = questionary.confirm(
            f"Confirmas? {n_aprendizagem} {nome_alg} + {n_fixa} politica fixa = {total} total",
            default=True,
            style=CLI_STYLE,
        ).ask()

        if confirmacao is None:
            print("\nOperacao cancelada.")
            sys.exit(0)

        if confirmacao:
            return n_aprendizagem


def perguntar_algoritmo_aprendizagem() -> str:
    """Pergunta qual algoritmo de aprendizagem usar."""
    escolha = questionary.select(
        "Escolhe o algoritmo de aprendizagem:",
        choices=[
            questionary.Choice("Q-Learning (Reforco)", value="qlearning"),
            questionary.Choice("Algoritmo Genetico (Evolutivo)", value="genetico"),
        ],
        style=CLI_STYLE,
    ).ask()

    if escolha is None:
        print("\nOperacao cancelada.")
        sys.exit(0)

    return escolha


def perguntar_snapshot_interval(episodios: int) -> int:
    """Pergunta intervalo de snapshots para Q-Learning."""
    usar = questionary.confirm(
        "Guardar snapshots da Q-table durante treino?",
        default=False,
        style=CLI_STYLE,
    ).ask()

    if not usar:
        return 0

    resposta = questionary.text(
        "Guardar snapshot a cada quantos episodios?",
        default="20",
        validate=lambda x: x.isdigit() and int(x) > 0 or "Introduz um numero > 0",
        style=CLI_STYLE,
    ).ask()

    return int(resposta)


def contar_qtables_disponiveis(ambiente: str) -> int:
    """Conta quantas Q-tables existem para o ambiente especificado."""
    base_path = Path(__file__).parent
    qtables_dir = base_path / "qtables"

    if not qtables_dir.exists():
        return 0

    prefixo = "AgenteFarol" if ambiente == "FAROL" else "Forager"
    return sum(1 for _ in qtables_dir.glob(f"qtable_{prefixo}_*.json"))


def perguntar_distribuicao_teste(total: int, ambiente: str) -> int:
    """Pergunta quantos agentes usam Q-table treinada (modo teste)."""
    n_qtables = contar_qtables_disponiveis(ambiente)
    max_agentes = min(total, n_qtables) if n_qtables > 0 else 0

    base_path = Path(__file__).parent
    qtables_dir = base_path / "qtables"
    total_qtables = (
        sum(1 for _ in qtables_dir.glob("qtable_*.json")) if qtables_dir.exists() else 0
    )

    if n_qtables == 0:
        print(f"\nAviso: Nao foram encontradas Q-tables para o ambiente {ambiente}.")
        if total_qtables > 0:
            print(
                f"   (Existem {total_qtables} Q-table(s) no total, mas nenhuma para {ambiente})"
            )
        print("   Todos os agentes usarao politica fixa inteligente.")
        return 0

    print(f"\nQ-tables disponiveis para {ambiente}: {n_qtables}")
    if total_qtables > n_qtables:
        print(f"   (Total de Q-tables no sistema: {total_qtables})")
    if n_qtables < total:
        print(f"Aviso: Tens {total} agentes mas apenas {n_qtables} Q-table(s).")
        print(f"   O maximo de agentes com Q-Learning sera {max_agentes}.")

    while True:
        resposta = questionary.text(
            f"Quantos usam Q-table treinada? [0-{max_agentes}]",
            default=str(max_agentes),
            validate=lambda x: x.isdigit()
            and 0 <= int(x) <= max_agentes
            or f"Introduz um numero entre 0 e {max_agentes}",
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
        questionary.Choice(
            "Curva de aprendizagem (recompensa)", value="recompensa", checked=True
        ),
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
    algoritmo: str = "qlearning",
    snapshot_interval: int = 0,
) -> Dict[str, Any]:
    """Gera configuracao dinamica baseada nas escolhas do utilizador."""

    base_path = Path(__file__).parent

    template_path = base_path / f"config_{ambiente.lower()}.json"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        if ambiente == "FAROL":
            config = {
                "ambiente": {
                    "tipo": "FAROL",
                    "largura": 10,
                    "altura": 8,
                    "pos_farol": [7, 6],
                    "obstaculos": [[3, 3], [4, 4], [5, 3], [2, 5], [6, 2]],
                }
            }
        else:
            config = {
                "ambiente": {
                    "tipo": "FORAGING",
                    "largura": 15,
                    "altura": 15,
                    "ninho": [7, 7],
                    "recursos": [],
                }
            }
            n_recursos = max(4, n_agentes * 2)
            for _ in range(n_recursos):
                while True:
                    rx = random.randint(0, 14)
                    ry = random.randint(0, 14)
                    if (rx, ry) != (7, 7):
                        config["ambiente"]["recursos"].append(
                            {"x": rx, "y": ry, "valor": random.randint(5, 15)}
                        )
                        break

    config["modo_execucao"] = modo
    config["episodios"] = episodios
    config["max_passos"] = max_passos
    config["visualizar"] = False
    config["snapshot_interval"] = snapshot_interval

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
            if algoritmo == "qlearning":
                agente["politica"] = {
                    "tipo": "qlearning",
                    "alfa": 0.3,
                    "gama": 0.9,
                    "epsilon": 0.2 if modo == "APRENDIZAGEM" else 0.0,
                }
            else:  # genetico
                agente["politica"] = {
                    "tipo": "genetico",
                    "pop_size": 50,
                    "taxa_mutacao": 0.1,
                    "taxa_crossover": 0.7,
                }
        else:
            agente["politica"] = {"tipo": "fixa_inteligente"}

        agentes.append(agente)

    config["agentes"] = agentes

    return config


def executar_simulacao(config: Dict[str, Any], graficos: List[str]):
    """Executa a simulação com a configuração fornecida."""
    import tempfile
    from sma.loader import carregar_simulacao

    base_path = Path(__file__).parent

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
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
    if config.get("snapshot_interval", 0) > 0:
        print(f"   Snapshot Q-table: a cada {config['snapshot_interval']} eps")
    print("\n" + "-" * 50 + "\n")

    try:
        sim = carregar_simulacao(
            config_path, visual=False, episodios=config["episodios"]
        )
        if "snapshot_interval" in config:
            sim.snapshot_interval = config["snapshot_interval"]

        sim.executa()

        resultados_dir = base_path / "resultados"
        resultados_dir.mkdir(exist_ok=True)

        modo = config["modo_execucao"].lower()
        ambiente = config["ambiente"]["tipo"].lower()
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
        sim = carregar_simulacao(config_path, visual=True, episodios=1)

        sim.carregar_politicas()

        for ag in sim.agentes:
            if hasattr(ag.politica, "epsilon"):
                ag.politica.epsilon = 0.0

        sim.executa()

    except Exception as e:
        print(f"Aviso: Nao foi possivel mostrar visualizacao final: {e}")


def gerar_graficos_selecionados(
    csv_path: str, graficos: List[str], config: Dict[str, Any]
):
    """Gera os graficos selecionados e guarda em ficheiro PNG."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import subprocess
        import platform
        from sma.gerar_analise import carregar_csv, calcular_media_movel

        dados = carregar_csv(csv_path)

        if not dados:
            print("Aviso: Sem dados para gerar graficos.")
            return

        episodios = [d["episodio"] for d in dados]

        n_graficos = len(graficos)
        if n_graficos == 0:
            return

        cols = min(2, n_graficos)
        rows = (n_graficos + 1) // 2

        fig, axes = plt.subplots(rows, cols, figsize=(7 * cols, 5 * rows))
        if n_graficos == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

        ambiente = config["ambiente"]["tipo"]
        modo = config["modo_execucao"]
        fig.suptitle(f"Analise - {ambiente} ({modo})", fontsize=14, fontweight="bold")

        idx = 0

        if "recompensa" in graficos:
            recompensas = [d["recompensa_total"] for d in dados]
            recompensas_media = calcular_media_movel(recompensas, janela=10)
            ax = axes[idx]
            ax.plot(
                episodios, recompensas, alpha=0.3, color="green", label="Valor real"
            )
            ax.plot(
                episodios,
                recompensas_media,
                color="green",
                linewidth=2,
                label="Media movel (10)",
            )
            ax.set_xlabel("Episodio")
            ax.set_ylabel("Recompensa Total")
            ax.set_title("Curva de Aprendizagem (Recompensa)")
            ax.legend()
            ax.grid(True, alpha=0.3)
            idx += 1

        if "passos" in graficos:
            passos = [d["passos"] for d in dados]
            passos_media = calcular_media_movel(passos, janela=10)
            ax = axes[idx]
            ax.plot(episodios, passos, alpha=0.3, color="blue", label="Valor real")
            ax.plot(
                episodios,
                passos_media,
                color="blue",
                linewidth=2,
                label="Media movel (10)",
            )
            ax.set_xlabel("Episodio")
            ax.set_ylabel("Passos")
            ax.set_title("Passos por Episodio")
            ax.legend()
            ax.grid(True, alpha=0.3)
            idx += 1

        if "descontada" in graficos:
            descontada = [d["recompensa_descontada"] for d in dados]
            descontada_media = calcular_media_movel(descontada, janela=10)
            ax = axes[idx]
            ax.plot(
                episodios, descontada, alpha=0.3, color="purple", label="Valor real"
            )
            ax.plot(
                episodios,
                descontada_media,
                color="purple",
                linewidth=2,
                label="Media movel (10)",
            )
            ax.set_xlabel("Episodio")
            ax.set_ylabel("Recompensa Descontada")
            ax.set_title("Recompensa Descontada")
            ax.legend()
            ax.grid(True, alpha=0.3)
            idx += 1

        if "sucesso" in graficos:
            sucessos = [1 if d["sucesso"] else 0 for d in dados]
            taxa_acumulada = []
            for i in range(len(sucessos)):
                taxa_acumulada.append(sum(sucessos[: i + 1]) / (i + 1))
            ax = axes[idx]
            ax.plot(episodios, taxa_acumulada, color="red", linewidth=2)
            ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="50%")
            ax.set_xlabel("Episodio")
            ax.set_ylabel("Taxa de Sucesso")
            ax.set_title("Taxa de Sucesso Acumulada")
            ax.set_ylim([0, 1.1])
            ax.legend()
            ax.grid(True, alpha=0.3)
            idx += 1

        for i in range(idx, len(axes)):
            axes[i].axis("off")

        plt.tight_layout()

        base_path = Path(__file__).parent
        analise_dir = base_path / "analise"
        analise_dir.mkdir(exist_ok=True)

        output_file = analise_dir / f"{ambiente.lower()}_{modo.lower()}_graficos.png"
        plt.savefig(output_file, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()

        print(f"\nGraficos guardados em: {output_file}")

        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(output_file)], check=True)
            elif platform.system() == "Windows":
                subprocess.run(["start", "", str(output_file)], shell=True, check=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(output_file)], check=True)
            print("Ficheiro aberto no visualizador de imagens.")
        except Exception:
            print("Abre o ficheiro manualmente para ver os graficos.")

    except ImportError:
        print(
            "\nAviso: Nao foi possivel gerar graficos. Instale matplotlib: pip install matplotlib"
        )
    except Exception as e:
        print(f"\nAviso: Erro ao gerar graficos: {e}")


def executar_comparacao_politicas():
    """Executa comparação entre política fixa e aprendida."""
    from sma.comparar_politicas import (
        executar_com_politica_fixa,
        executar_com_politica_aprendida,
        comparar_resultados,
    )
    from sma.loader import carregar_simulacao

    mostrar_banner()
    print("\n" + "=" * 70)
    print("COMPARACAO DE POLITICAS")
    print("=" * 70)
    print("\nEste modo compara a politica fixa inteligente com Q-Learning.")
    print("NOTA: A Q-table deve ter sido treinada previamente em modo APRENDIZAGEM\n")

    ambiente = perguntar_ambiente()
    n_qtables = contar_qtables_disponiveis(ambiente)

    if n_qtables == 0:
        print(f"\nErro: Nao foram encontradas Q-tables para o ambiente {ambiente}.")
        print("   Treina primeiro os agentes em modo APRENDIZAGEM.")
        return

    print(f"\nQ-tables disponiveis para {ambiente}: {n_qtables}")
    n_agentes = perguntar_num_agentes()

    if n_agentes > n_qtables:
        print(f"\nAviso: Tens {n_agentes} agentes mas apenas {n_qtables} Q-table(s).")
        print(f"   Limitando a {n_qtables} agentes para comparacao.")
        n_agentes = n_qtables

    episodios = perguntar_episodios()
    max_passos = perguntar_max_passos()

    config = gerar_config_dinamico(
        ambiente=ambiente,
        modo="TESTE",
        n_agentes=n_agentes,
        n_aprendizagem=n_agentes,
        episodios=episodios,
        max_passos=max_passos,
    )

    base_path = Path(__file__).parent
    config_path = base_path / "temp_comparacao.json"

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    try:
        stats_fixa, historico_fixa = executar_com_politica_fixa(
            str(config_path), episodios
        )

        stats_aprendida, historico_aprendida = executar_com_politica_aprendida(
            str(config_path), episodios
        )

        comparar_resultados(stats_fixa, stats_aprendida)

        resultados_dir = base_path / "resultados"
        resultados_dir.mkdir(exist_ok=True)

        sim_temp = carregar_simulacao(str(config_path), visual=False, episodios=1)
        sim_temp.registador_resultados.historico = historico_fixa
        csv_fixa = str(resultados_dir / "comparacao_fixa.csv")
        sim_temp.registador_resultados.exportarCSV(csv_fixa)

        sim_temp.registador_resultados.historico = historico_aprendida
        csv_aprendida = str(resultados_dir / "comparacao_aprendida.csv")
        sim_temp.registador_resultados.exportarCSV(csv_aprendida)

        print("\nResultados exportados:")
        print(f"  - Política Fixa: {csv_fixa}")
        print(f"  - Política Aprendida: {csv_aprendida}")

        try:
            from sma.gerar_analise import gerar_comparacao
            import subprocess
            import platform

            print("\n" + "=" * 70)
            print("GERANDO GRAFICOS COMPARATIVOS")
            print("=" * 70)
            gerar_comparacao(csv_fixa, csv_aprendida, resultados_dir)
            print(
                f"\nGrafico de comparacao guardado em: {resultados_dir / 'comparacao_politicas.png'}"
            )

            grafico_path = resultados_dir / "comparacao_politicas.png"
            try:
                if platform.system() == "Darwin":
                    subprocess.run(["open", str(grafico_path)], check=True)
                elif platform.system() == "Windows":
                    subprocess.run(
                        ["start", "", str(grafico_path)], shell=True, check=True
                    )
                else:
                    subprocess.run(["xdg-open", str(grafico_path)], check=True)
                print("Grafico aberto no visualizador de imagens.")
            except Exception:
                print("Abre o ficheiro manualmente para ver os graficos.")
        except ImportError:
            print("\nAviso: matplotlib e numpy sao necessarios para gerar graficos.")
            print("   Instale com: pip install matplotlib numpy")
            print("   Os CSVs foram gerados, mas os graficos nao puderam ser criados.")
        except Exception as e:
            print(f"\nAviso: Erro ao gerar graficos: {e}")
            print("   Os CSVs foram gerados, mas os graficos nao puderam ser criados.")

    finally:
        if config_path.exists():
            config_path.unlink()

    if config.get("snapshot_interval", 0) > 0:
        print(f"   Snapshot Q-table: a cada {config['snapshot_interval']} eps")
    print("\n" + "-" * 50 + "\n")


def menu_analise():
    """Sub-menu de análises avançadas."""
    print("\n" + "=" * 50)
    print("   ANÁLISE AVANÇADA")
    print("=" * 50)

    ambiente_analise = perguntar_ambiente()

    opcao = questionary.select(
        "Escolhe a ferramenta de análise:",
        choices=[
            "Comparar Melhores Valores (Q-Tables)",
            "Demonstrar Limitações (Política Fixa)",
            "Voltar",
        ],
        style=CLI_STYLE,
    ).ask()

    if opcao == "Comparar Melhores Valores (Q-Tables)":
        analisar_qtables(ambiente_analise)
    elif opcao == "Demonstrar Limitações (Política Fixa)":
        demonstrar_limitacoes(ambiente_analise)

    print("\n")
    questionary.text(
        "Pressiona Enter para voltar ao menu principal...", style=CLI_STYLE
    ).ask()
    main()


def main():
    """Função principal do CLI."""
    mostrar_banner()

    modo_operacao = perguntar_modo_operacao()

    if modo_operacao == "Analise Avancada":
        menu_analise()
        return

    if modo_operacao == "Comparar politicas (Fixa Inteligente vs Q-Learning)":
        executar_comparacao_politicas()
        return

    ambiente = perguntar_ambiente()
    modo = perguntar_modo()

    if modo == "TESTE":
        n_qtables = contar_qtables_disponiveis(ambiente)
        if n_qtables > 0:
            print(f"\nQ-tables disponiveis para {ambiente}: {n_qtables}")

    n_agentes = perguntar_num_agentes()

    if modo == "APRENDIZAGEM":
        algoritmo = perguntar_algoritmo_aprendizagem()
        n_aprendizagem = perguntar_distribuicao_aprendizagem(n_agentes, algoritmo)
    else:
        algoritmo = "qlearning"  # Default para teste
        n_aprendizagem = perguntar_distribuicao_teste(n_agentes, ambiente)

    episodios = perguntar_episodios()
    max_passos = perguntar_max_passos()

    snapshot_interval = 0
    if modo == "APRENDIZAGEM" and algoritmo == "qlearning":
        snapshot_interval = perguntar_snapshot_interval(episodios)

    graficos = perguntar_graficos()

    config = gerar_config_dinamico(
        ambiente=ambiente,
        modo=modo,
        n_agentes=n_agentes,
        n_aprendizagem=n_aprendizagem,
        episodios=episodios,
        max_passos=max_passos,
        algoritmo=algoritmo,
        snapshot_interval=snapshot_interval,
    )

    executar_simulacao(config, graficos)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulacao cancelada pelo utilizador (Ctrl+C).")
        sys.exit(0)
