from ..core.agente_base import Agente
from ..core.tipos import Accao


class AgenteForager(Agente):
    """Agente para foraging (recolha de recursos)."""
    
    def __init__(self, id_: str, politica, ninho_pos=None):
        super().__init__(id_, politica)
        self.ninho_pos = ninho_pos
        self.carregando = 0

    def age(self) -> Accao:
        return self.politica.selecionar_acao(self._observacao_atual)
