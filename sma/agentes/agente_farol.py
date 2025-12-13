from ..core.agente_base import Agente
from ..core.tipos import Accao


class AgenteFarol(Agente):
    """Agente para o problema do farol."""
    
    def age(self) -> Accao:
        return self.politica.selecionar_acao(self._observacao_atual)
