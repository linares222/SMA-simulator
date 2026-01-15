import json
from pathlib import Path
from sma.loader import carregar_simulacao


def demonstrar_limitacoes(ambiente: str = "FAROL"):
    """
    Demonstra as limitações da Política Fixa comparando-a num cenário 'armadilha'.
    Cria um ambiente temporário com obstáculos em U (Cul-de-sac) onde a heurística gulosa falha.
    """
    print(f"\n--- Analisando Limitações da Política Fixa ({ambiente}) ---")

    # Agente no (1,1), Farol no (1,4), Obstáculo em U bloqueando o caminho direto
    config = {
        "ambiente": {
            "tipo": "FAROL",
            "largura": 10,
            "altura": 10,
            "obstaculos": [[0, 3], [1, 3], [2, 3], [0, 2], [2, 2]],
            "farol_pos": [1, 5],
        },
        "agentes": [
            {
                "tipo": "AgenteFarol",
                "posicao": [1, 1],
                "politica": {"tipo": "fixa_inteligente"},
            }
        ],
        "modo_execucao": "TESTE",
        "episodios": 1,
        "max_passos": 50,
    }

    if ambiente == "FORAGING":
        print(
            "Nota: Demonstração de limitações otimizada para cenário FAROL (Navegação)."
        )
        config["ambiente"]["tipo"] = "FORAGING"
        config["ambiente"]["recursos"] = [{"pos": [1, 5], "valor": 10}]
        config["ambiente"]["ninho_pos"] = [8, 8]
        del config["ambiente"]["farol_pos"]
        config["agentes"][0]["tipo"] = "AgenteForager"

    temp_path = Path("temp_limitacoes.json")
    with open(temp_path, "w") as f:
        json.dump(config, f, indent=2)

    try:
        print("\nExecutando Simulação em Cenário 'Armadilha' (Cul-de-sac)...")
        sim = carregar_simulacao(str(temp_path), visual=False, episodios=1)
        sim.executa()

        hist = sim.registador_resultados.historico[0]
        passos = hist["passos"]
        sucesso = hist["sucesso"]

        print("\nResultados Política Fixa:")
        print(f"Sucesso: {sucesso}")
        print(f"Passos usados: {passos}")

        if not sucesso:
            print("\nANÁLISE: A política fixa falhou ou demorou muito.")
            print("Causa Probável: Mínimo Local.")
            print("A heurística tenta minimizar a distância ao alvo a cada passo.")
            print(
                "No cenário 'U', ir para baixo (S) aproxima do alvo mas bate no muro."
            )
            print(
                "Para sair, o agente precisaria se afastar do alvo (Norte) temporariamente,"
            )
            print("o que uma heurística gananciosa simples recusa-se a fazer.")
        else:
            print(
                "\nANÁLISE: A política fixa conseguiu resolver (talvez por sorte ou heurística melhorada)."
            )

    except Exception as e:
        print(f"Erro na execução: {e}")
    finally:
        if temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    demonstrar_limitacoes()
