import numpy as np
from typing import Tuple, List, Optional, Set
from ..core.ambiente_base import Ambiente
from ..core.tipos import Accao, TipoAccao


class AmbienteFarol(Ambiente):
    def __init__(self, largura: int, altura: int, pos_farol: Tuple[int, int], 
                 obstaculos: Optional[List[Tuple[int, int]]] = None):
        self.largura = largura
        self.altura = altura
        self.pos_farol = pos_farol
        self.matriz = np.zeros((altura, largura), dtype=int)
        self.terminou = False
        self.obstaculos: Set[Tuple[int, int]] = set(map(tuple, obstaculos or []))
        
        for ox, oy in self.obstaculos:
            if 0 <= ox < largura and 0 <= oy < altura:
                self.matriz[oy, ox] = 2

    def direcao_para_farol(self, pos_ag) -> Tuple[int, int]:
        dx = np.sign(self.pos_farol[0] - pos_ag[0])
        dy = np.sign(self.pos_farol[1] - pos_ag[1])
        return int(dx), int(dy)

    def vizinhanca(self, pos, raio: int = 1, diagonais: bool = True, agente=None):
        """Retorna informações sobre as células ao redor do agente."""
        x, y = pos
        dirs = [(0, -1), (0, 1), (1, 0), (-1, 0)]  # N, S, E, O
        if diagonais:
            dirs += [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # NE, SE, NO, SO

        viz = {}
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.largura and 0 <= ny < self.altura:
                # 0 = vazio, 2 = obstáculo, 1 = farol
                if (nx, ny) in self.obstaculos:
                    viz[(dx, dy)] = 2  # obstáculo
                elif (nx, ny) == self.pos_farol:
                    viz[(dx, dy)] = 1  # farol
                else:
                    viz[(dx, dy)] = 0  # vazio
            else:
                viz[(dx, dy)] = -1  # fora dos limites

        return viz

    def agir(self, accao: Accao, agente) -> float:
        x, y = agente.posicao
        nx, ny = x, y

        if accao.tipo == TipoAccao.MoverN:
            ny = y - 1
        elif accao.tipo == TipoAccao.MoverS:
            ny = y + 1
        elif accao.tipo == TipoAccao.MoverE:
            nx = x + 1
        elif accao.tipo == TipoAccao.MoverO:
            nx = x - 1

        fora = not (0 <= nx < self.largura and 0 <= ny < self.altura)
        if fora or (nx, ny) in self.obstaculos:
            return -10.0

        agente.posicao = (nx, ny)
        if agente.posicao == self.pos_farol:
            self.terminou = True
            return 99.0
        return -1.0

    def atualizacao(self):
        pass
