import json
from pathlib import Path


def analisar_qtables(ambiente: str):
    """
    Carrega todas as Q-tables disponíveis para o ambiente e gera uma análise comparativa.
    Compara:
    1. Estatísticas globais (máx, média, desvio padrão dos Q-values)
    2. Concordância de políticas (quão similares são as melhores ações escolhidas)
    """
    base_path = Path(__file__).parent / "qtables"
    prefixo = "AgenteFarol" if ambiente == "FAROL" else "Forager"
    ficheiros = list(base_path.glob(f"qtable_{prefixo}_*.json"))

    if not ficheiros:
        print(f"Nenhuma Q-table encontrada para {ambiente} em {base_path}")
        return

    print(f"\n--- Analisando {len(ficheiros)} Q-tables para {ambiente} ---")

    tabelas = []
    nomes = []

    for f in ficheiros:
        try:
            with open(f, "r") as file:
                data = json.load(file)
                qdb = data.get("Q", {})
                if qdb:
                    tabelas.append(qdb)
                    nomes.append(f.name)
        except Exception as e:
            print(f"Erro ao ler {f.name}: {e}")

    if not tabelas:
        print("Nenhuma tabela válida carregada.")
        return

    print("\nEstatísticas de Valores Q:")
    print(f"{'Arquivo':<40} {'Estados':<10} {'Q-Max':<10} {'Q-Médio':<10}")
    print("-" * 75)

    for nome, qdb in zip(nomes, tabelas):
        todos_valores = []
        for acoes in qdb.values():
            todos_valores.extend(acoes.values())

        if todos_valores:
            q_max = max(todos_valores)
            q_mean = sum(todos_valores) / len(todos_valores)
            print(f"{nome:<40} {len(qdb):<10} {q_max:<10.2f} {q_mean:<10.2f}")

    if len(tabelas) > 1:
        print("\nComparação de Políticas (Consenso):")

        estados_comuns = set(tabelas[0].keys())
        for qdb in tabelas[1:]:
            estados_comuns &= set(qdb.keys())

        if not estados_comuns:
            print("Não há estados comuns entre todas as tabelas para comparar.")
        else:
            concordancias = 0
            for estado in estados_comuns:
                melhores_acoes = []
                for qdb in tabelas:
                    acoes = qdb[estado]
                    melhor_a = max(acoes, key=acoes.get)
                    melhores_acoes.append(melhor_a)

                if len(set(melhores_acoes)) == 1:
                    concordancias += 1

            porcentagem = (concordancias / len(estados_comuns)) * 100
            print(f"Estados comuns analisados: {len(estados_comuns)}")
            print(
                f"Concordância total (todas escolhem a mesma ação): {porcentagem:.2f}%"
            )

            if porcentagem < 100:
                print("\nExemplo de Divergência:")
                for estado in estados_comuns:
                    melhores_acoes = []
                    valores = []
                    for qdb in tabelas:
                        acoes = qdb[estado]
                        best = max(acoes, key=acoes.get)
                        melhores_acoes.append(best)
                        valores.append(acoes[best])

                    if len(set(melhores_acoes)) > 1:
                        print(f"Estado: {estado[:60]}...")
                        for n, a, v in zip(nomes, melhores_acoes, valores):
                            print(f"  {n}: {a} (Q={v:.2f})")
                        break


if __name__ == "__main__":
    analisar_qtables("FAROL")
