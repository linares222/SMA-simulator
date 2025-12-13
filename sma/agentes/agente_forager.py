from ..core.agente_base import Agente
from ..core.tipos import Accao


class AgenteForager(Agente):
    """Agente para foraging (recolha de recursos)."""
    
    def __init__(self, id_: str, politica, ninho_pos=None):
        super().__init__(id_, politica)
        self.ninho_pos = ninho_pos
        self.carregando = 0
        self._ultima_carga = 0
        self._ultima_posicao = None

    def age(self) -> Accao:
        return self.politica.selecionar_acao(self._observacao_atual)
    
    def processar_comunicacao(self, simulador, ambiente):
        """Processa eventos e envia mensagens quando necessário."""
        if self.carregando > 0 and self._ultima_carga == 0:
            mensagem = f"Colectei recurso de valor {self.carregando} na posição {self.posicao}!"
            simulador.broadcast_mensagem(self, mensagem)
        
        if self.carregando == 0 and self._ultima_carga > 0:
            mensagem = f"Depositei {self._ultima_carga} no ninho!"
            simulador.broadcast_mensagem(self, mensagem)
        
        if simulador and simulador.listaAgentes():
            for outro_agente in simulador.listaAgentes():
                if outro_agente != self:
                    dist = abs(self.posicao[0] - outro_agente.posicao[0]) + abs(self.posicao[1] - outro_agente.posicao[1])
                    if dist <= 2 and self._ultima_posicao != self.posicao:
                        estado = f"carregando {self.carregando}" if self.carregando > 0 else "livre"
                        mensagem = f"Estou na posição {self.posicao}, {estado}"
                        simulador.enviar_mensagem(self, outro_agente, mensagem)
        
        self._ultima_carga = self.carregando
        self._ultima_posicao = self.posicao
