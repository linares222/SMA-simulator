from typing import Any
from .tipos import Observacao, Accao


class Ambiente:
    """Classe base para ambientes."""
    
    def agir(self, accao: Accao, agente: Any) -> float:
        """Executa accao e retorna recompensa."""
        raise NotImplementedError

    def atualizacao(self):
        """Chamado no fim de cada passo."""
        pass
