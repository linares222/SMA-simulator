import json
import random
from pathlib import Path
from typing import Any, Dict, Tuple
from .tipos import Observacao, Accao, TipoAccao


class ModoExecucao:
    APRENDIZAGEM = "APRENDIZAGEM"
    TESTE = "TESTE"


class Politica:
    def selecionar_acao(self, estado: Observacao) -> Accao:
        raise NotImplementedError

    def atualizar(self, estado: Observacao, accao: Accao, recompensa: float, prox_estado: Observacao):
        pass

    def set_modo(self, modo: str):
        pass

    def guardar(self, caminho: str):
        pass

    def carregar(self, caminho: str) -> bool:
        return False


class PoliticaFixa(Politica):
    def __init__(self, default: TipoAccao = TipoAccao.Stay):
        self.default = default

    def selecionar_acao(self, estado: Observacao) -> Accao:
        return Accao(self.default)


class PoliticaFixaInteligente(Politica):
    """
    Política fixa que usa heurísticas baseadas nas observações.
    Útil para comparação com políticas aprendidas.
    """
    
    def __init__(self, tipo_ambiente: str = "FAROL"):
        """
        Args:
            tipo_ambiente: "FAROL" ou "FORAGING"
        """
        self.tipo_ambiente = tipo_ambiente
    
    def selecionar_acao(self, estado: Observacao) -> Accao:
        dados = estado.dados
        
        if self.tipo_ambiente == "FAROL":
            return self._acao_farol(dados)
        elif self.tipo_ambiente == "FORAGING":
            return self._acao_foraging(dados)
        else:
            return Accao(TipoAccao.Stay)
    
    def _acao_farol(self, dados: dict) -> Accao:
        """Heurística para o problema do farol."""
        if not isinstance(dados, dict):
            return Accao(TipoAccao.Stay)
        
        # Se está no farol, fica parado
        if dados.get("no_farol", False):
            return Accao(TipoAccao.Stay)
        
        # Obter direção do farol
        dir_farol = dados.get("dir_farol", (0, 0))
        viz = dados.get("viz", {})
        
        # Prioridade: mover na direção do farol
        dx, dy = dir_farol
        
        # Tentar mover na direção do farol (prioridade horizontal, depois vertical)
        if dx > 0:  # Farol a Este
            if viz.get((1, 0), -1) not in {2, -1}:  # Não é obstáculo nem fora
                return Accao(TipoAccao.MoverE)
        elif dx < 0:  # Farol a Oeste
            if viz.get((-1, 0), -1) not in {2, -1}:
                return Accao(TipoAccao.MoverO)
        
        if dy > 0:  # Farol a Sul
            if viz.get((0, 1), -1) not in {2, -1}:
                return Accao(TipoAccao.MoverS)
        elif dy < 0:  # Farol a Norte
            if viz.get((0, -1), -1) not in {2, -1}:
                return Accao(TipoAccao.MoverN)
        
        # Se não pode ir diretamente, tenta contornar obstáculos
        # Prioridade: Este/Oeste primeiro, depois Norte/Sul
        for direcao, acao in [
            ((1, 0), TipoAccao.MoverE),
            ((-1, 0), TipoAccao.MoverO),
            ((0, -1), TipoAccao.MoverN),
            ((0, 1), TipoAccao.MoverS),
        ]:
            if viz.get(direcao, -1) not in {2, -1}:
                return Accao(acao)
        
        # Se tudo está bloqueado, fica parado
        return Accao(TipoAccao.Stay)
    
    def _acao_foraging(self, dados: dict) -> Accao:
        """Heurística para o problema de foraging."""
        if not isinstance(dados, dict):
            return Accao(TipoAccao.Stay)
        
        carregando = dados.get("carregando", 0)
        viz = dados.get("viz", {})
        no_ninho = dados.get("no_ninho", False)
        no_recurso = dados.get("no_recurso", False)
        
        # Se está no ninho e está carregando, deposita
        if no_ninho and carregando > 0:
            return Accao(TipoAccao.Depositar)
        
        # Se está num recurso e não está carregando, coleta
        if no_recurso and carregando == 0:
            return Accao(TipoAccao.Coletar)
        
        # Se está carregando, vai para o ninho
        if carregando > 0:
            dir_ninho = dados.get("dir_ninho", (0, 0))
            dx, dy = dir_ninho
            
            # Tentar mover na direção do ninho
            if dx > 0:  # Ninho a Este
                if viz.get((1, 0), -1) not in {9, -1}:  # Não é obstáculo nem fora
                    return Accao(TipoAccao.MoverE)
            elif dx < 0:  # Ninho a Oeste
                if viz.get((-1, 0), -1) not in {9, -1}:
                    return Accao(TipoAccao.MoverO)
            
            if dy > 0:  # Ninho a Sul
                if viz.get((0, 1), -1) not in {9, -1}:
                    return Accao(TipoAccao.MoverS)
            elif dy < 0:  # Ninho a Norte
                if viz.get((0, -1), -1) not in {9, -1}:
                    return Accao(TipoAccao.MoverN)
        
        # Se não está carregando, vai buscar recursos
        else:
            dir_recurso = dados.get("dir_recurso", (0, 0))
            dx, dy = dir_recurso
            
            # Tentar mover na direção do recurso mais próximo
            if dx > 0:  # Recurso a Este
                if viz.get((1, 0), -1) not in {9, -1}:
                    return Accao(TipoAccao.MoverE)
            elif dx < 0:  # Recurso a Oeste
                if viz.get((-1, 0), -1) not in {9, -1}:
                    return Accao(TipoAccao.MoverO)
            
            if dy > 0:  # Recurso a Sul
                if viz.get((0, 1), -1) not in {9, -1}:
                    return Accao(TipoAccao.MoverS)
            elif dy < 0:  # Recurso a Norte
                if viz.get((0, -1), -1) not in {9, -1}:
                    return Accao(TipoAccao.MoverN)
            
            # Se há recurso na vizinhança, tenta ir para ele
            for direcao, acao in [
                ((1, 0), TipoAccao.MoverE),
                ((-1, 0), TipoAccao.MoverO),
                ((0, -1), TipoAccao.MoverN),
                ((0, 1), TipoAccao.MoverS),
            ]:
                if viz.get(direcao, -1) == 2:  # Recurso na célula
                    return Accao(acao)
        
        # Se não pode ir diretamente, tenta contornar obstáculos
        for direcao, acao in [
            ((1, 0), TipoAccao.MoverE),
            ((-1, 0), TipoAccao.MoverO),
            ((0, -1), TipoAccao.MoverN),
            ((0, 1), TipoAccao.MoverS),
        ]:
            if viz.get(direcao, -1) not in {9, -1}:
                return Accao(acao)
        
        # Se tudo está bloqueado, fica parado
        return Accao(TipoAccao.Stay)


class PoliticaQLearning(Politica):
    def __init__(self, acoes: Tuple[TipoAccao, ...], alfa=0.2, gama=0.95, epsilon=0.1):
        # Q-table: guarda o valor de cada ação em cada estado
        self.Q: Dict[Any, Dict[TipoAccao, float]] = {}
        self.acoes = acoes
        
        # alfa: velocidade de aprendizagem (0.1-0.5, mais alto = aprende mais rápido)
        self.alfa = alfa
        
        # gama: importância de recompensas futuras (0.8-0.99, mais alto = pensa mais à frente)
        self.gama = gama
        
        # epsilon: probabilidade de ação aleatória (0.05-0.4, mais alto = explora mais)
        self.eps = epsilon
        
        self._modo = ModoExecucao.APRENDIZAGEM

    def _key(self, obs: Observacao) -> Any:
        return repr(obs.dados)

    def _qmax(self, k: Any) -> float:
        return max(self.Q.get(k, {}).values() or [0.0])

    def selecionar_acao(self, estado: Observacao) -> Accao:
        k = self._key(estado)
        self.Q.setdefault(k, {a: 0.0 for a in self.acoes})
        
        # Epsilon-greedy: durante aprendizagem, às vezes escolhe ação aleatória (explora)
        # A probabilidade é controlada por self.eps
        if self._modo == ModoExecucao.APRENDIZAGEM and random.random() < self.eps:
            a = random.choice(self.acoes)
        else:
            # Escolhe a ação com maior valor Q (a melhor que conhece)
            a = max(self.Q[k], key=self.Q[k].get)
        return Accao(a)

    def atualizar(self, estado: Observacao, accao: Accao, recompensa: float, prox_estado: Observacao):
        # Só atualiza durante aprendizagem
        if self._modo != ModoExecucao.APRENDIZAGEM:
            return
        
        k = self._key(estado)
        k2 = self._key(prox_estado)
        self.Q.setdefault(k, {a: 0.0 for a in self.acoes})
        self.Q.setdefault(k2, {a: 0.0 for a in self.acoes})
        
        # Fórmula Q-Learning: Q(novo) = Q(antigo) + alfa * (recompensa + gama * melhor_Q_futuro - Q(antigo))
        qsa = self.Q[k][accao.tipo]
        alvo = recompensa + self.gama * max(self.Q[k2].values())
        self.Q[k][accao.tipo] = qsa + self.alfa * (alvo - qsa)

    def set_modo(self, modo: str):
        self._modo = modo
        if modo == ModoExecucao.TESTE:
            # Em teste, epsilon = 0 (só usa o que aprendeu, sem exploração)
            self.eps = 0.0

    def guardar(self, caminho: str):
        q_ser = {
            estado: {a.value: v for a, v in acoes.items()}
            for estado, acoes in self.Q.items()
        }
        dados = {
            "Q": q_ser,
            "acoes": [a.value for a in self.acoes],
            "alfa": self.alfa,
            "gama": self.gama,
            "epsilon_original": self.eps if self._modo != ModoExecucao.TESTE else 0.1,
        }
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2)
        print(f"Q-table guardada: {caminho}")

    def carregar(self, caminho: str) -> bool:
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self.Q = {
                estado: {TipoAccao(a): v for a, v in acoes.items()}
                for estado, acoes in dados["Q"].items()
            }
            print(f"Q-table carregada: {caminho} ({len(self.Q)} estados)")
            return True
        except FileNotFoundError:
            print(f"Ficheiro nao encontrado: {caminho}")
            return False
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao carregar: {e}")
            return False
