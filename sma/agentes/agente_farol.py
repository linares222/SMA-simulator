from ..core.agente_base import Agente
from ..core.tipos import Accao


class AgenteFarol(Agente):
    """Agente para o problema do farol."""
    
    def __init__(self, id_: str, politica):
        super().__init__(id_, politica)
        self._ultima_posicao = None
        self._encontrou_farol = False
    
    def age(self) -> Accao:
        return self.politica.selecionar_acao(self._observacao_atual)
    
    def processar_comunicacao(self, simulador, ambiente):
        """Processa eventos e envia mensagens quando necessário."""
        if hasattr(ambiente, 'pos_farol') and self.posicao == ambiente.pos_farol and not self._encontrou_farol:
            self._encontrou_farol = True
            mensagem = f"Encontrei o farol na posição {self.posicao}!"
            simulador.broadcast_mensagem(self, mensagem)
        
        if simulador and simulador.listaAgentes():
            for outro_agente in simulador.listaAgentes():
                if outro_agente != self:
                    dist = abs(self.posicao[0] - outro_agente.posicao[0]) + abs(self.posicao[1] - outro_agente.posicao[1])
                    if dist <= 2 and self._ultima_posicao != self.posicao:
                        mensagem = f"Estou na posição {self.posicao}, direção do farol: {ambiente.direcao_para_farol(self.posicao)}"
                        simulador.enviar_mensagem(self, outro_agente, mensagem)
        
        self._ultima_posicao = self.posicao
