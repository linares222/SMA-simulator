from typing import Any


class Sensor:
    """Classe base para sensores."""
    
    def ler(self, ambiente: Any, agente: Any) -> Any:
        raise NotImplementedError


class SensorDirecaoFarol(Sensor):
    """Sensor que indica direcao para o farol e vizinhanca."""
    
    def __init__(self, diagonais: bool = True):
        self.diagonais = diagonais
    
    def ler(self, ambiente, agente) -> Any:
        dir_farol = ambiente.direcao_para_farol(agente.posicao)
        viz = ambiente.vizinhanca(agente.posicao, raio=1, diagonais=self.diagonais, agente=agente)
        return {
            "dir_farol": dir_farol,
            "viz": viz,
            "no_farol": agente.posicao == ambiente.pos_farol,
        }


class SensorVizinhancaGrid(Sensor):
    """Sensor que le celulas vizinhas."""
    
    def __init__(self, raio: int = 1, diagonais: bool = True):
        self.raio = raio
        self.diagonais = diagonais

    def ler(self, ambiente, agente) -> Any:
        return ambiente.vizinhanca(agente.posicao, self.raio, self.diagonais, agente=agente)
