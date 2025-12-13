from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional


class TipoAccao(Enum):
    """Tipos de accao que um agente pode fazer."""
    MoverN = "MoverN"
    MoverS = "MoverS"
    MoverE = "MoverE"
    MoverO = "MoverO"
    Stay = "Stay"
    Coletar = "Coletar"
    Depositar = "Depositar"


@dataclass
class Observacao:
    """Observacao do ambiente."""
    dados: Any


@dataclass
class Accao:
    """Accao a executar."""
    tipo: TipoAccao
    parametros: Optional[Dict[str, Any]] = None
