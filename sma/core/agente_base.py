import threading
from abc import ABC, abstractmethod
from typing import List
from .tipos import Observacao, Accao
from .politicas import Politica


class Agente(threading.Thread, ABC):
    def __init__(self, id_: str, politica: Politica):
        super().__init__(daemon=True)
        self.id = id_
        self.politica = politica
        self.sensores: List = []
        self.posicao = (0, 0)
        self.posicao_inicial = (0, 0)
        self._observacao_atual = Observacao(dados=None)
        self._accao_pronta = Accao(tipo=None)
        self._barreira_percepcao = None
        self._barreira_acao = None
        self._ativo = True
        self._estado_anterior: Observacao = None
        self._accao_anterior: Accao = None

    def instala(self, sensor):
        self.sensores.append(sensor)

    def observar(self, ambiente) -> Observacao:
        if not self.sensores:
            return Observacao(dados=None)

        if len(self.sensores) == 1:
            dados = self.sensores[0].ler(ambiente, self)
            return Observacao(dados=dados)

        dados = {}
        for i, sensor in enumerate(self.sensores):
            nome = sensor.__class__.__name__
            dados[f"{nome}_{i}"] = sensor.ler(ambiente, self)
        return Observacao(dados=dados)

    def observacao(self, obs: Observacao):
        self._observacao_atual = obs

    @abstractmethod
    def age(self) -> Accao:
        pass

    def avaliacaoEstadoAtual(self, recompensa: float):
        if self._estado_anterior is not None and self._accao_anterior is not None:
            self.politica.atualizar(self._estado_anterior, self._accao_anterior, 
                                   recompensa, self._observacao_atual)

    def parar(self):
        self._ativo = False

    def run(self):
        while self._ativo:
            try:
                if self._barreira_percepcao:
                    self._barreira_percepcao.wait()

                if not self._ativo:
                    break

                self._accao_pronta = self.age()

                if self._barreira_acao:
                    self._barreira_acao.wait()

            except threading.BrokenBarrierError:
                break
            except Exception as e:
                print(f"Erro no agente {self.id}: {e}")
                break
