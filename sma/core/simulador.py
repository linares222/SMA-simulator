import json
import threading
import numpy as np
from pathlib import Path
from typing import List, Optional
from .ambiente_base import Ambiente
from .agente_base import Agente
from .resultados import RegistadorResultados
from .politicas import ModoExecucao


class MotorDeSimulacao:
    def __init__(self):
        self.ambiente: Ambiente = None
        self.agentes: List[Agente] = []
        self.modo = ModoExecucao.TESTE
        self.episodios = 1
        self.max_passos = 200
        self.barreira_percepcao = None
        self.barreira_acao = None
        self.registador_resultados = RegistadorResultados()
        self.visualizador = None
        self.diretorio_qtables: Optional[str] = None

    @staticmethod
    def cria(cfg_path: str) -> "MotorDeSimulacao":
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        sim = MotorDeSimulacao()
        sim.episodios = cfg.get("episodios", 1)
        sim.max_passos = cfg.get("max_passos", 200)
        sim.modo = cfg.get("modo_execucao", ModoExecucao.TESTE)
        return sim

    def _propagar_modo(self):
        for ag in self.agentes:
            if hasattr(ag, 'politica'):
                ag.politica.set_modo(self.modo)

    def _caminho_qtable(self, ag: Agente) -> str:
        if self.diretorio_qtables:
            dir_ = self.diretorio_qtables
        else:
            dir_ = str(Path(__file__).parent.parent / "qtables")
        return str(Path(dir_) / f"qtable_{ag.id}.json")

    def guardar_politicas(self):
        from .politicas import PoliticaQLearning
        guardadas = 0
        for ag in self.agentes:
            if isinstance(ag.politica, PoliticaQLearning):
                ag.politica.guardar(self._caminho_qtable(ag))
                guardadas += 1
        if guardadas > 0:
            print(f"\nTotal: {guardadas} Q-table(s) guardada(s) de {len(self.agentes)} agente(s)")

    def carregar_politicas(self):
        from .politicas import PoliticaFixaInteligente, PoliticaQLearning
        
        for ag in self.agentes:
            if isinstance(ag.politica, PoliticaQLearning):
                sucesso = ag.politica.carregar(self._caminho_qtable(ag))
                if not sucesso and self.modo == ModoExecucao.TESTE:
                    tipo_agente = "FAROL" if "Farol" in ag.__class__.__name__ or "FAROL" in str(ag.id).upper() else "FORAGER"
                    print(f"Aviso: Agente {ag.id} sem Q-table, usando politica fixa inteligente")
                    ag.politica = PoliticaFixaInteligente(tipo_agente)

    def _reset_episodio(self):
        self.ambiente.terminou = False
        for ag in self.agentes:
            ag.posicao = ag.posicao_inicial
            if hasattr(ag, 'carregando'):
                ag.carregando = 0

        if hasattr(self.ambiente, 'recursos_iniciais'):
            self.ambiente.recursos = dict(self.ambiente.recursos_iniciais)
            self.ambiente.matriz = np.zeros((self.ambiente.altura, self.ambiente.largura), dtype=int)
            for (x, y), _ in self.ambiente.recursos.items():
                self.ambiente.matriz[y, x] = 2
            if hasattr(self.ambiente, 'obstaculos'):
                for (x, y), _ in self.ambiente.obstaculos.items():
                    self.ambiente.matriz[y, x] = 9
            if hasattr(self.ambiente, 'ninho'):
                self.ambiente.matriz[self.ambiente.ninho[1], self.ambiente.ninho[0]] = 3

    def executa(self):
        self._propagar_modo()
        
        if self.modo == ModoExecucao.TESTE:
            self.carregar_politicas()

        n_participantes = len(self.agentes) + 1
        self.barreira_percepcao = threading.Barrier(n_participantes)
        self.barreira_acao = threading.Barrier(n_participantes)

        for a in self.agentes:
            a._barreira_percepcao = self.barreira_percepcao
            a._barreira_acao = self.barreira_acao
            if not a.is_alive():
                a.start()

        try:
            for ep in range(self.episodios):
                self.registador_resultados.iniciar_episodio()
                sucesso = False
                self._reset_episodio()

                for _ in range(self.max_passos):
                    for ag in self.agentes:
                        obs = ag.observar(self.ambiente)
                        ag.observacao(obs)
                        ag._estado_anterior = ag._observacao_atual

                    self.barreira_percepcao.wait()
                    self.barreira_acao.wait()

                    if hasattr(self.ambiente, '_agentes'):
                        self.ambiente._agentes = self.agentes
                    
                    for ag in self.agentes:
                        accao = ag._accao_pronta
                        ag._accao_anterior = accao
                        recomp = self.ambiente.agir(accao, ag)
                        novo_obs = ag.observar(self.ambiente)
                        ag.observacao(novo_obs)
                        ag.avaliacaoEstadoAtual(recomp)
                        val_dep = getattr(self.ambiente, 'get_ultimo_valor_depositado', lambda: 0.0)()
                        self.registador_resultados.registar_passo(recomp, val_dep)

                    self.ambiente.atualizacao()
                    
                    if hasattr(self.ambiente, 'verificar_termino'):
                        self.ambiente.verificar_termino(self.agentes)

                    if self.visualizador:
                        self.visualizador.render(self.ambiente, self.agentes)

                    if getattr(self.ambiente, "terminou", False):
                        sucesso = True
                        break

                met = self.registador_resultados.fechar_episodio()
                met.sucesso = sucesso

                if self.visualizador:
                    self.visualizador.render(self.ambiente, self.agentes)

                print(f"Ep {ep+1}/{self.episodios}: passos={met.passos}, recomp={met.recompensa_total:.2f}, sucesso={met.sucesso}", flush=True)

        finally:
            for a in self.agentes:
                a.parar()
            try:
                self.barreira_percepcao.abort()
                self.barreira_acao.abort()
            except threading.BrokenBarrierError:
                pass

        self.registador_resultados.imprimir_resumo()
        
        if self.modo == ModoExecucao.APRENDIZAGEM:
            self.guardar_politicas()

        if self.visualizador:
            self.visualizador.finalizar()
