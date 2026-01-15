import json
import random
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from .tipos import Observacao, Accao, TipoAccao
from .politicas import Politica, ModoExecucao


class PoliticaGenetica(Politica):
    """
    Política que usa algoritmo genético para evoluir comportamento.

    Cromossoma: array de pesos que influenciam a escolha de ação
    baseado nas observações (direção do objetivo, vizinhança).
    """

    def __init__(
        self,
        acoes: Tuple[TipoAccao, ...],
        pop_size: int = 20,
        taxa_mutacao: float = 0.1,
        taxa_crossover: float = 0.7,
    ):
        self.acoes = acoes
        self.n_acoes = len(acoes)
        self.pop_size = pop_size
        self.taxa_mutacao = taxa_mutacao
        self.taxa_crossover = taxa_crossover

        self.n_features = 13
        self.tamanho_cromossoma = (self.n_features * self.n_acoes) + self.n_acoes

        self.populacao: List[np.ndarray] = [
            np.random.randn(self.tamanho_cromossoma) * 0.5 for _ in range(pop_size)
        ]

        self.ultima_accao: Optional[TipoAccao] = None
        self.fitness: List[float] = [0.0] * pop_size
        self.individuo_atual = 0

        self.melhor_cromossoma: np.ndarray = None
        self.melhor_fitness = float("-inf")

        self.geracao = 0
        self.historico_fitness: List[float] = []

        self._modo = ModoExecucao.APRENDIZAGEM

    def _extrair_features(self, obs: Observacao) -> np.ndarray:
        """Extrai features numéricas da observação para usar com cromossoma."""
        dados = obs.dados if hasattr(obs, "dados") else obs
        features = np.zeros(self.n_features)

        # 1-2: Direção do objetivo (normalizada)
        dir_obj = dados.get("dir_farol", dados.get("dir_recurso", (0, 0)))
        if dados.get("carregando", 0) > 0:
            dir_obj = dados.get("dir_ninho", (0, 0))

        features[0] = np.clip(dir_obj[0], -1, 1) if dir_obj else 0
        features[1] = np.clip(dir_obj[1], -1, 1) if dir_obj else 0

        viz = dados.get("viz", {})
        features[2] = 1.0 if viz.get((0, -1), 0) in {2, 9, -1} else 0.0
        features[3] = 1.0 if viz.get((0, 1), 0) in {2, 9, -1} else 0.0
        features[4] = 1.0 if viz.get((1, 0), 0) in {2, 9, -1} else 0.0
        features[5] = 1.0 if viz.get((-1, 0), 0) in {2, 9, -1} else 0.0

        features[6] = (
            1.0 if dados.get("no_farol", False) or dados.get("no_ninho", False) else 0.0
        )
        features[7] = 1.0 if dados.get("no_recurso", False) else 0.0

        if self.ultima_accao == TipoAccao.MoverN:
            features[8] = 1.0
        elif self.ultima_accao == TipoAccao.MoverS:
            features[9] = 1.0
        elif self.ultima_accao == TipoAccao.MoverE:
            features[10] = 1.0
        elif self.ultima_accao == TipoAccao.MoverO:
            features[11] = 1.0

        if self.ultima_accao:
            # Mapear ultima_accao para vetor
            map_dir = {
                TipoAccao.MoverN: (0, -1),
                TipoAccao.MoverS: (0, 1),
                TipoAccao.MoverE: (1, 0),
                TipoAccao.MoverO: (-1, 0),
            }
            d_vec = map_dir.get(self.ultima_accao)
            if d_vec and viz.get(d_vec) in {2, 9, -1}:
                features[12] = 1.0

        return features

    def _calcular_scores(
        self, cromossoma: np.ndarray, features: np.ndarray
    ) -> np.ndarray:
        """Calcula scores para cada ação como um modelo linear multi-classe."""
        offset = self.n_features * self.n_acoes
        bias = cromossoma[offset:]

        scores = np.zeros(self.n_acoes)
        for i in range(self.n_acoes):
            w = cromossoma[i * self.n_features : (i + 1) * self.n_features]
            scores[i] = np.dot(w, features) + bias[i]

        return scores

    def selecionar_acao(self, estado: Observacao) -> Accao:
        """Seleciona ação usando o indivíduo atual da população."""
        if self._modo == ModoExecucao.TESTE and self.melhor_cromossoma is not None:
            cromossoma = self.melhor_cromossoma
        else:
            cromossoma = self.populacao[self.individuo_atual]

        features = self._extrair_features(estado)
        scores = self._calcular_scores(cromossoma, features)

        if self._modo == ModoExecucao.APRENDIZAGEM and random.random() < 0.1:
            idx = random.randrange(self.n_acoes)
        else:
            idx = int(np.argmax(scores))

        self.ultima_accao = self.acoes[idx]
        return Accao(self.ultima_accao)

    def atualizar(
        self,
        estado: Observacao,
        accao: Accao,
        recompensa: float,
        prox_estado: Observacao,
    ):
        """Acumula fitness para o indivíduo atual."""
        if self._modo != ModoExecucao.APRENDIZAGEM:
            return
        self.fitness[self.individuo_atual] += recompensa

    def fim_episodio(self):
        """Chamado no fim de cada episódio para avançar para próximo indivíduo."""
        if self._modo != ModoExecucao.APRENDIZAGEM:
            return

        # Verificar se é o melhor
        if self.fitness[self.individuo_atual] > self.melhor_fitness:
            self.melhor_fitness = self.fitness[self.individuo_atual]
            self.melhor_cromossoma = self.populacao[self.individuo_atual].copy()

        # Avançar para próximo indivíduo
        self.individuo_atual += 1

        # Se avaliou toda a população, evoluir
        if self.individuo_atual >= self.pop_size:
            self._evoluir()

    def _evoluir(self):
        """Cria nova geração usando seleção, crossover e mutação."""
        self.geracao += 1

        # Guardar melhor fitness da geração
        melhor_gen = max(self.fitness)
        media_gen = sum(self.fitness) / len(self.fitness)
        self.historico_fitness.append(melhor_gen)
        print(f"Geração {self.geracao}: melhor={melhor_gen:.2f}, média={media_gen:.2f}")

        # Criar nova população
        nova_pop = []

        # Elitismo: manter os 2 melhores
        indices_ordenados = sorted(
            range(self.pop_size), key=lambda i: self.fitness[i], reverse=True
        )
        nova_pop.append(self.populacao[indices_ordenados[0]].copy())
        nova_pop.append(self.populacao[indices_ordenados[1]].copy())

        # Preencher resto com crossover e mutação
        while len(nova_pop) < self.pop_size:
            # Seleção por torneio
            pai1 = self._selecao_torneio()
            pai2 = self._selecao_torneio()

            # Crossover
            if random.random() < self.taxa_crossover:
                filho = self._crossover(pai1, pai2)
            else:
                filho = pai1.copy()

            # Mutação
            filho = self._mutacao(filho)
            nova_pop.append(filho)

        self.populacao = nova_pop
        self.fitness = [0.0] * self.pop_size
        self.individuo_atual = 0
        self.ultima_accao = None

    def _selecao_torneio(self, k: int = 3) -> np.ndarray:
        """Seleção por torneio: escolhe k indivíduos, retorna o melhor."""
        indices = random.sample(range(self.pop_size), min(k, self.pop_size))
        melhor_idx = max(indices, key=lambda i: self.fitness[i])
        return self.populacao[melhor_idx]

    def _crossover(self, pai1: np.ndarray, pai2: np.ndarray) -> np.ndarray:
        """Crossover de um ponto."""
        ponto = random.randint(1, len(pai1) - 1)
        filho = np.concatenate([pai1[:ponto], pai2[ponto:]])
        return filho

    def _mutacao(self, cromossoma: np.ndarray) -> np.ndarray:
        """Aplica mutação gaussiana a cada gene."""
        for i in range(len(cromossoma)):
            if random.random() < self.taxa_mutacao:
                cromossoma[i] += np.random.randn() * 0.3
        return cromossoma

    def set_modo(self, modo: str):
        """Define modo de execução."""
        self._modo = modo

    def guardar(self, caminho: str):
        """Guarda o melhor cromossoma e estatísticas."""
        dados = {
            "melhor_cromossoma": self.melhor_cromossoma.tolist()
            if self.melhor_cromossoma is not None
            else None,
            "melhor_fitness": self.melhor_fitness,
            "geracao": self.geracao,
            "historico_fitness": self.historico_fitness,
            "acoes": [a.value for a in self.acoes],
            "parametros": {
                "pop_size": self.pop_size,
                "taxa_mutacao": self.taxa_mutacao,
                "taxa_crossover": self.taxa_crossover,
            },
        }
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2)
        print(f"Política genética guardada: {caminho}")

    def carregar(self, caminho: str) -> bool:
        """Carrega o melhor cromossoma."""
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)

            if dados["melhor_cromossoma"] is not None:
                self.melhor_cromossoma = np.array(dados["melhor_cromossoma"])
                self.melhor_fitness = dados["melhor_fitness"]
                self.geracao = dados["geracao"]
                self.historico_fitness = dados.get("historico_fitness", [])
                print(
                    f"Política genética carregada: {caminho} (geração {self.geracao})"
                )
                return True
            return False
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao carregar política genética: {e}")
            return False
