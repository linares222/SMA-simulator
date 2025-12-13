# Multi-Agent Simulator

Implementation of a multi-agent system simulator with Q-Learning for navigation and foraging environments.

## Features

- **Q-Learning**: Complete reinforcement learning implementation
- **Multi-agent**: Support for multiple simultaneous agents
- **Two environments**: Farol (navigation) and Foraging (resource collection)
- **Interactive CLI**: User-friendly interface for configuration and execution
- **Results analysis**: Automatic generation of graphs and metrics
- **Mixed policies**: Comparison between Q-Learning agents and fixed policies
- **Visualization**: Graphical representation of environments and agents

## Requirements

- Python 3.10+
- NumPy >= 1.21.0
- Matplotlib >= 3.5.0
- Questionary >= 2.0.0

### Installation

```bash
pip install -r requirements.txt
```

The `run.sh` script automatically installs dependencies if needed.

## How to Run

### Interactive CLI (Recommended)

The simulator includes an interactive interface that guides the user through all options:

```bash
./run.sh
```

The CLI allows you to configure:
- **Operation mode:** Execute simulation or compare policies
- **Environment:** FAROL or FORAGING
- **Mode:** LEARNING (train) or TEST (evaluate trained policy)
- **Number of agents:** Total number of agents in the simulation
- **Distribution:** How many agents use Q-Learning vs fixed policy
- **Episodes:** Number of episodes to run
- **Max steps:** Maximum number of steps per episode
- **Graphs:** Select which graphs to generate at the end

**Policy Comparison Mode:**
- Compares Fixed Intelligent policy vs Q-Learning
- Automatically detects available Q-tables for the selected environment
- Limits Q-Learning agents to the number of available Q-tables
- Executes both policies with the same configuration
- Generates comparative graphs showing both policies side-by-side
- Exports separate CSV files for each policy

**Features:**
- Automatically activates Python virtual environment
- Runs main simulation without visualization (faster)
- Shows visualization only on the final episode
- Automatically generates and opens analysis graphs
- Saves results to CSV
- Supports cancellation with `Ctrl+C`

### Manual Mode (Legacy)

```bash
# farol environment (default)
python -m sma.run farol

# foraging environment
python -m sma.run foraging

# with visualization
python -m sma.run farol --visual

# specify number of episodes
python -m sma.run foraging -e 200

# save results
python -m sma.run farol -o results.csv
```

## Project Structure

```
sma/
  core/              # Base classes (agent, environment, simulator)
    - agente_base.py      # Abstract agent class
    - ambiente_base.py    # Abstract environment class
    - simulador.py        # Simulation engine
    - politicas.py        # Q-Learning implementation
    - sensores.py         # Sensor system
    - visualizador.py     # Graphical visualization
    - resultados.py       # Metrics management
  agentes/           # Agent implementations
    - agente_farol.py     # Agent for Farol environment
    - agente_forager.py   # Agent for Foraging environment
  ambientes/         # Environment implementations
    - farol.py            # Farol navigation environment
    - foraging.py         # Foraging environment
  cli.py             # Interactive interface (CLI)
  comparar_politicas.py  # Policy comparison
  gerar_analise.py   # Analysis and graph generation
  config_*.json      # Configuration files
  resultados/        # Exported results (CSV)
  analise/           # Generated graphs (PNG)
  qtables/           # Saved Q-tables (JSON)
run.sh               # Script to run CLI
requirements.txt     # Python dependencies
```

## Environments

### Farol
Agents must navigate to the farol using Q-Learning. They receive the relative direction to the farol as observation through sensors. The goal is to reach the farol in the minimum number of steps.

**Characteristics:**
- Observation: Relative direction to farol
- Actions: Move in 4 directions (North, South, East, West)
- Reward: Positive when reaching the farol, negative for steps without progress

### Foraging
Agents collect resources and deposit them in the nest. More complex environment that involves collecting resources and depositing them in the nest.

**Characteristics:**
- Observation: Agent state (with/without resource), relative position to nest and resources
- Actions: Move, collect resources, deposit in nest
- Reward: Based on the value of deposited resources

## Configuration

### Via Interactive CLI

The CLI automatically generates configuration based on user choices. It is not necessary to edit JSON files manually.

### Via JSON Files (Manual Mode)

The `config_*.json` files define simulation parameters:
- `modo_execucao`: LEARNING or TEST
- `episodios`: Number of episodes
- `max_passos`: Steps per episode
- `visualizar`: true/false
- Environment and agent parameters

## Results Analysis

The simulator automatically generates:
- **Learning curves**: Reward evolution over episodes
- **Performance metrics**: Success rate, average steps, rewards
- **Policy comparison**: Q-Learning vs fixed policies with side-by-side graphs
- **CSV export**: Raw data for external analysis

### Policy Comparison

Compare Fixed Intelligent policy with Q-Learning:

```bash
# Via CLI (interactive)
./run.sh
# Select "Comparar politicas (Fixa Inteligente vs Q-Learning)"

# Via command line
python -m sma.comparar_politicas config_farol.json --episodios 10
```

**Q-table Management:**
- Q-tables are always saved to `sma/qtables/` after training (overwrites existing ones)
- The comparison script automatically detects how many Q-tables exist for the environment
- Limits Q-Learning agents to the number of available Q-tables
- Remaining agents use Fixed Intelligent policy

This generates:
- Comparative statistics in terminal
- Two CSV files (one for each policy)
- Comparative graphs showing 6 metrics side-by-side

## Additional Documentation

- `relatorio.md`: Complete technical report on architecture and implementation

## Development

### Modular Structure

The project follows a modular architecture:
- **Core**: Reusable base components
- **Agents**: Environment-specific implementations
- **Environments**: Simulation space definitions
- **Policies**: Learning algorithms (Q-Learning)

### Extensibility

To add new environments or agents:
1. Create a class that inherits from `Ambiente` or `Agente`
2. Implement required methods
3. Add corresponding JSON configuration

## License

This is a project developed for educational purposes.
