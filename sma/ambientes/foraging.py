import numpy as np
from typing import Dict, Tuple
from ..core.ambiente_base import Ambiente
from ..core.tipos import Accao, TipoAccao


class AmbienteForaging(Ambiente):
    def __init__(self, largura: int, altura: int, ninho: Tuple[int, int],
                 recursos: Dict[Tuple[int, int], int],
                 obstaculos: Dict[Tuple[int, int], int] | None = None):
        self.largura = largura
        self.altura = altura
        self.ninho = ninho
        self.recursos = dict(recursos)
        self.recursos_iniciais = dict(recursos)
        self.obstaculos = obstaculos if obstaculos else {}
        self.terminou = False
        self._ultimo_valor_depositado = 0.0
        
        self.matriz = np.zeros((altura, largura), dtype=int)
        for (x, y), _ in self.recursos.items():
            self.matriz[y, x] = 2
        if obstaculos:
            for (x, y), _ in obstaculos.items():
                self.matriz[y, x] = 9
        self.matriz[ninho[1], ninho[0]] = 3

    def vizinhanca(self, pos, raio: int = 1, diagonais: bool = False, agente=None):
        x, y = pos
        dirs = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        if diagonais:
            dirs += [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        viz = {}
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.largura and 0 <= ny < self.altura:
                viz[(dx, dy)] = int(self.matriz[ny, nx])
            else:
                viz[(dx, dy)] = -1

        dir_ninho = (int(np.sign(self.ninho[0] - x)), int(np.sign(self.ninho[1] - y)))
        dist_ninho = abs(self.ninho[0] - x) + abs(self.ninho[1] - y)

        dir_rec, dist_rec = (0, 0), float('inf')
        for rx, ry in self.recursos:
            d = abs(rx - x) + abs(ry - y)
            if d < dist_rec:
                dist_rec = d
                dir_rec = (int(np.sign(rx - x)), int(np.sign(ry - y)))

        return {
            "viz": viz,
            "carregando": getattr(agente, "carregando", 0) if agente else 0,
            "dir_ninho": dir_ninho,
            "dist_ninho": min(dist_ninho, 10),
            "dir_recurso": dir_rec,
            "no_ninho": pos == self.ninho,
            "no_recurso": pos in self.recursos,
        }

    def agir(self, accao: Accao, agente) -> float:
        x, y = agente.posicao
        nx, ny = x, y
        recomp = -0.1
        self._ultimo_valor_depositado = 0.0

        if accao.tipo in {TipoAccao.MoverN, TipoAccao.MoverS, TipoAccao.MoverE, TipoAccao.MoverO, TipoAccao.Stay}:
            if accao.tipo == TipoAccao.MoverN:
                ny = y - 1
            elif accao.tipo == TipoAccao.MoverS:
                ny = y + 1
            elif accao.tipo == TipoAccao.MoverE:
                nx = x + 1
            elif accao.tipo == TipoAccao.MoverO:
                nx = x - 1

            fora = not (0 <= nx < self.largura and 0 <= ny < self.altura)
            obst = not fora and self.matriz[ny, nx] == 9

            if fora or obst:
                return -5.0

            if accao.tipo != TipoAccao.Stay:
                agente.posicao = (nx, ny)
                carga = getattr(agente, "carregando", 0)
                if carga > 0:
                    d_ant = abs(self.ninho[0] - x) + abs(self.ninho[1] - y)
                    d_novo = abs(self.ninho[0] - nx) + abs(self.ninho[1] - ny)
                    if d_novo < d_ant:
                        recomp += 0.5
                elif self.recursos:
                    d_ant = min(abs(rx - x) + abs(ry - y) for rx, ry in self.recursos)
                    d_novo = min(abs(rx - nx) + abs(ry - ny) for rx, ry in self.recursos)
                    if d_novo < d_ant:
                        recomp += 0.3

        elif accao.tipo == TipoAccao.Coletar:
            if agente.posicao in self.recursos and getattr(agente, "carregando", 0) == 0:
                val = self.recursos.pop(agente.posicao)
                self.matriz[agente.posicao[1], agente.posicao[0]] = 0
                agente.carregando = val
                recomp += 5.0
            else:
                return -2.0

        elif accao.tipo == TipoAccao.Depositar:
            carga = getattr(agente, "carregando", 0)
            if carga > 0 and agente.posicao == self.ninho:
                recomp += float(carga) * 2.0
                self._ultimo_valor_depositado = float(carga)
                agente.carregando = 0
            else:
                return -2.0

        if not self.recursos:
            cargas = [getattr(a, "carregando", 0) for a in getattr(self, "_agentes", [agente])]
            if not any(cargas):
                self.terminou = True

        return recomp
    
    def get_ultimo_valor_depositado(self) -> float:
        return self._ultimo_valor_depositado

    def atualizacao(self):
        pass
