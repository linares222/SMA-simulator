import json
from pathlib import Path

from sma.core.simulador import MotorDeSimulacao
from sma.core.politicas import PoliticaFixa, PoliticaFixaInteligente, PoliticaQLearning, ModoExecucao
from sma.core.tipos import TipoAccao
from sma.core.sensores import SensorDirecaoFarol, SensorVizinhancaGrid
from sma.ambientes.farol import AmbienteFarol
from sma.ambientes.foraging import AmbienteForaging
from sma.agentes.agente_farol import AgenteFarol
from sma.agentes.agente_forager import AgenteForager


ACOES_FAROL = (TipoAccao.MoverN, TipoAccao.MoverS, TipoAccao.MoverE, TipoAccao.MoverO, TipoAccao.Stay)
ACOES_FORAGER = (*ACOES_FAROL, TipoAccao.Coletar, TipoAccao.Depositar)


def criar_politica(cfg_pol, modo, tipo_agente):
    tipo = cfg_pol.get("tipo", "fixa")
    
    if tipo == "qlearning":
        acoes = ACOES_FAROL if tipo_agente == "FAROL" else ACOES_FORAGER
        pol = PoliticaQLearning(
            acoes,
            cfg_pol.get("alfa", 0.2),
            cfg_pol.get("gama", 0.95),
            cfg_pol.get("epsilon", 0.1),
        )
        pol.set_modo(modo)
        return pol
    
    if tipo == "fixa_inteligente":
        return PoliticaFixaInteligente(tipo_agente)
    
    acao_str = cfg_pol.get("acao_default", "Stay")
    acao = TipoAccao[acao_str] if isinstance(acao_str, str) else acao_str
    return PoliticaFixa(acao)


def criar_agente_farol(cfg, modo, idx):
    cfg_pol = cfg.get("politica", {"tipo": "fixa"})
    pol = criar_politica(cfg_pol, modo, "FAROL")
    
    ag = AgenteFarol(cfg.get("id", f"A{idx}"), pol)
    pos = tuple(cfg.get("posicao_inicial", [0, 0]))
    ag.posicao = pos
    ag.posicao_inicial = pos
    ag.instala(SensorDirecaoFarol(diagonais=cfg.get("sensor_diagonais", True)))
    return ag


def criar_agente_forager(cfg, modo, ninho, idx):
    cfg_pol = cfg.get("politica", {"tipo": "fixa"})
    pol = criar_politica(cfg_pol, modo, "FORAGER")
    
    ag = AgenteForager(cfg.get("id", f"F{idx}"), pol, ninho_pos=ninho)
    pos = tuple(cfg.get("posicao_inicial", [0, 0]))
    ag.posicao = pos
    ag.posicao_inicial = pos
    ag.instala(SensorVizinhancaGrid(
        raio=cfg.get("sensor_raio", 1),
        diagonais=cfg.get("sensor_diagonais", True),
    ))
    return ag


def carregar_simulacao(cfg_path, visual=None, episodios=None):
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    sim = MotorDeSimulacao.cria(cfg_path)
    tipo = cfg["ambiente"]["tipo"]
    modo = cfg.get("modo_execucao", ModoExecucao.TESTE)
    agentes_cfg = cfg.get("agentes", {})
    
    if episodios is not None:
        sim.episodios = episodios
    
    if tipo == "FAROL":
        obs_cfg = cfg["ambiente"].get("obstaculos", [])
        sim.ambiente = AmbienteFarol(
            largura=cfg["ambiente"]["largura"],
            altura=cfg["ambiente"]["altura"],
            pos_farol=tuple(cfg["ambiente"]["pos_farol"]),
            obstaculos=[tuple(o) for o in obs_cfg] if obs_cfg else None,
        )
        
        if isinstance(agentes_cfg, dict) and "pos_iniciais" in agentes_cfg:
            for i, pos in enumerate(agentes_cfg["pos_iniciais"]):
                sim.agentes.append(criar_agente_farol({"posicao_inicial": pos}, modo, i))
        else:
            for i, ac in enumerate(agentes_cfg):
                sim.agentes.append(criar_agente_farol(ac, modo, i))
    
    elif tipo == "FORAGING":
        recursos = {(r["x"], r["y"]): r["valor"] for r in cfg["ambiente"]["recursos"]}
        ninho = tuple(cfg["ambiente"]["ninho"])
        sim.ambiente = AmbienteForaging(
            largura=cfg["ambiente"]["largura"],
            altura=cfg["ambiente"]["altura"],
            ninho=ninho,
            recursos=recursos,
        )
        
        if isinstance(agentes_cfg, dict) and "pos_iniciais" in agentes_cfg:
            for i, pos in enumerate(agentes_cfg["pos_iniciais"]):
                sim.agentes.append(criar_agente_forager({"posicao_inicial": pos}, modo, ninho, i))
        else:
            for i, ac in enumerate(agentes_cfg):
                sim.agentes.append(criar_agente_forager(ac, modo, ninho, i))
    
    usar_visual = visual if visual is not None else cfg.get("visualizar", False)
    if usar_visual:
        from sma.core.visualizador import Visualizador2D
        sim.visualizador = Visualizador2D()
    
    sim.modo = modo
    
    if "diretorio_qtables" in cfg:
        sim.diretorio_qtables = cfg["diretorio_qtables"]
    else:
        sim.diretorio_qtables = str(Path(__file__).parent / "qtables")
    
    return sim

