# Simulador Multi-Agente

Implementação de um simulador de sistemas multi-agente com Q-Learning para ambientes de navegação e forrageamento.

## 📋 Características

- **Q-Learning**: Implementação completa de aprendizagem por reforço
- **Multi-agente**: Suporte para múltiplos agentes simultâneos
- **Dois ambientes**: Farol (navegação) e Foraging (coleta de recursos)
- **CLI interativo**: Interface amigável para configuração e execução
- **Análise de resultados**: Geração automática de gráficos e métricas
- **Políticas mistas**: Comparação entre agentes com Q-Learning e políticas fixas
- **Visualização**: Representação gráfica dos ambientes e agentes

## 🚀 Requisitos

- Python 3.10+
- NumPy >= 1.21.0
- Matplotlib >= 3.5.0
- Questionary >= 2.0.0

### Instalação

```bash
pip install -r requirements.txt
```

O script `run.sh` instala automaticamente as dependências se necessário.

## 🎮 Como Executar

### CLI Interativo (Recomendado)

O simulador inclui uma interface interativa que guia o utilizador através de todas as opções:

```bash
./run.sh
```

O CLI permite configurar:
- **Ambiente:** FAROL ou FORAGING
- **Modo:** APRENDIZAGEM (treinar) ou TESTE (avaliar política treinada)
- **Número de agentes:** Quantidade total de agentes na simulação
- **Distribuição:** Quantos agentes usam Q-Learning vs política fixa
- **Episódios:** Número de episódios a executar
- **Max passos:** Número máximo de passos por episódio
- **Gráficos:** Selecionar quais gráficos gerar no final

**Funcionalidades:**
- ✅ Ativa automaticamente o ambiente virtual Python
- ✅ Executa simulação principal sem visualização (mais rápido)
- ✅ Mostra visualização apenas no episódio final
- ✅ Gera e abre automaticamente gráficos de análise
- ✅ Guarda resultados em CSV
- ✅ Suporta cancelamento com `Ctrl+C`

### Modo Manual (Legado)

```bash
# ambiente farol (default)
python -m sma.run farol

# ambiente foraging
python -m sma.run foraging

# com visualização
python -m sma.run farol --visual

# especificar número de episódios
python -m sma.run foraging -e 200

# guardar resultados
python -m sma.run farol -o resultados.csv
```

## 📁 Estrutura do Projeto

```
sma/
  core/              # Classes base (agente, ambiente, simulador)
    - agente_base.py      # Classe abstrata de agente
    - ambiente_base.py    # Classe abstrata de ambiente
    - simulador.py        # Motor de simulação
    - politicas.py        # Implementação de Q-Learning
    - sensores.py         # Sistema de sensores
    - visualizador.py     # Visualização gráfica
    - resultados.py       # Gestão de métricas
  agentes/           # Implementações dos agentes
    - agente_farol.py     # Agente para ambiente Farol
    - agente_forager.py   # Agente para ambiente Foraging
  ambientes/         # Implementações dos ambientes
    - farol.py            # Ambiente de navegação ao farol
    - foraging.py         # Ambiente de forrageamento
  cli.py             # Interface interativa (CLI)
  comparar_politicas.py  # Comparação de políticas
  gerar_analise.py   # Geração de análises e gráficos
  config_*.json      # Ficheiros de configuração
  resultados/        # Resultados exportados (CSV)
  analise/           # Gráficos gerados (PNG)
  qtables/           # Q-tables guardadas (JSON)
run.sh               # Script para executar CLI
requirements.txt     # Dependências Python
```

## 🌍 Ambientes

### Farol
Agentes têm de navegar até ao farol usando Q-Learning. Recebem a direção relativa ao farol como observação através de sensores. O objetivo é alcançar o farol no menor número de passos possível.

**Características:**
- Observação: Direção relativa ao farol
- Ações: Mover nas 4 direções (Norte, Sul, Este, Oeste)
- Recompensa: Positiva ao alcançar o farol, negativa por passos sem progresso

### Foraging
Agentes recolhem recursos e depositam no ninho. Ambiente mais complexo que envolve coletar recursos e depositá-los no ninho.

**Características:**
- Observação: Estado do agente (com/sem recurso), posição relativa ao ninho e recursos
- Ações: Mover, coletar recursos, depositar no ninho
- Recompensa: Baseada no valor dos recursos depositados

## ⚙️ Configuração

### Via CLI Interativo

O CLI gera automaticamente a configuração baseada nas escolhas do utilizador. Não é necessário editar ficheiros JSON manualmente.

### Via Ficheiros JSON (Modo Manual)

Os ficheiros `config_*.json` definem os parâmetros da simulação:
- `modo_execucao`: APRENDIZAGEM ou TESTE
- `episodios`: Número de episódios
- `max_passos`: Passos por episódio
- `visualizar`: true/false
- Parâmetros do ambiente e agentes

## 📊 Análise de Resultados

O simulador gera automaticamente:
- **Curvas de aprendizagem**: Evolução da recompensa ao longo dos episódios
- **Métricas de desempenho**: Taxa de sucesso, passos médios, recompensas
- **Comparação de políticas**: Q-Learning vs políticas fixas
- **Exportação CSV**: Dados brutos para análise externa

Consulte `ANALISE_RESULTADOS.md` para mais detalhes sobre análise de resultados.

## 📚 Documentação Adicional

- `relatorio.md`: Relatório técnico completo da arquitetura e implementação
- `CODE_REVIEW.md`: Revisão de código e melhorias
- `ANALISE_RESULTADOS.md`: Guia de análise de resultados
- `TESTES_REALIZADOS.md`: Documentação de testes realizados

## 🔧 Desenvolvimento

### Estrutura Modular

O projeto segue uma arquitetura modular:
- **Core**: Componentes base reutilizáveis
- **Agentes**: Implementações específicas por ambiente
- **Ambientes**: Definições dos espaços de simulação
- **Políticas**: Algoritmos de aprendizagem (Q-Learning)

### Extensibilidade

Para adicionar novos ambientes ou agentes:
1. Criar classe que herda de `Ambiente` ou `Agente`
2. Implementar métodos obrigatórios
3. Adicionar configuração JSON correspondente

## 📄 Licença

Este é um projeto desenvolvido para fins educacionais.
