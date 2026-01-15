# Relatório Técnico: Simulador de Sistemas Multi-Agente

## Índice
1. [Arquitetura do Simulador](#arquitetura-do-simulador)
2. [Interface Interativa (CLI)](#interface-interativa-cli)
3. [Sensores](#sensores)
4. [Agentes](#agentes)
5. [Ambientes](#ambientes)
6. [Políticas](#políticas)
7. [Modos de Operação](#modos-de-operação)
8. [Sincronização e Threads](#sincronização-e-threads)
9. [Comunicação entre Agentes](#comunicação-entre-agentes)
10. [Métricas de Desempenho](#métricas-de-desempenho)

---

## Arquitetura do Simulador

O simulador segue uma arquitetura modular baseada em três componentes principais:

### 1. Motor de Simulação (`MotorDeSimulacao`)

O motor de simulação gere o ciclo de tempo e a ordem de execução das ações dos agentes.

**Interface principal:**
- `cria(nome_do_ficheiro_parametros: string) -> MotorDeSimulacao`: Cria uma instância do simulador a partir de um ficheiro JSON de configuração
- `listaAgentes() -> Agente[]`: Retorna a lista de agentes no simulador
- `executa()`: Executa a simulação completa

**Funcionalidades:**
- Gestão de episódios e passos de simulação
- Sincronização de agentes através de barreiras (threading.Barrier)
- Registo de resultados e métricas
- Suporte para visualização
- Gestão de políticas (guardar/carregar Q-tables)
- Sistema de comunicação entre agentes (enviar_mensagem, broadcast_mensagem)

### 2. Ambiente Base (`Ambiente`)

Interface abstrata que define o contrato para todos os ambientes.

**Métodos obrigatórios:**
- `observacaoPara(agente: Agente) -> Observacao`: Retorna a observação do ambiente para um agente (método legado, os sensores usam métodos específicos)
- `agir(accao: Accao, agente: Agente) -> float`: Executa uma ação do agente e retorna a recompensa
- `atualizacao()`: Chamado no fim de cada passo de simulação

### 3. Agente Base (`Agente`)

Classe abstrata que implementa a interface de agente como uma thread independente.

**Métodos principais:**
- `cria(cfg: str) -> Agente`: Método estático para criar agentes a partir de configuração
- `observacao(obs: Observacao)`: Recebe uma observação do ambiente
- `age() -> Accao`: Método abstrato que retorna a ação a executar
- `avaliacaoEstadoAtual(recompensa: float)`: Recebe a recompensa e atualiza a política
- `instala(sensor: Sensor)`: Instala um sensor no agente
- `comunica(mensagem: String, de_agente: Agente)`: Permite comunicação entre agentes
- `obter_mensagens() -> List[dict]`: Retorna todas as mensagens recebidas e limpa a lista
- `tem_mensagens() -> bool`: Verifica se há mensagens pendentes

---

## Interface Interativa (CLI)

### Visão Geral

Foi implementada uma interface de linha de comando (CLI) interativa que simplifica significativamente a configuração e execução de simulações. O CLI utiliza a biblioteca `questionary` para fornecer uma experiência de utilizador intuitiva e guiada.

### Execução

```bash
./run.sh
```

O script `run.sh`:
- Detecta e ativa automaticamente o ambiente virtual Python (`.env-aa`, `venv`, `.venv`, etc.)
- Instala dependências automaticamente se necessário
- Executa o CLI interativo

### Fluxo de Configuração

O CLI guia o utilizador através de uma série de perguntas:

1. **Escolha do Ambiente:**
   - FAROL: Navegação até ao farol
   - FORAGING: Recolha e depósito de recursos

2. **Modo de Operação:**
   - Executar simulação: Modo normal de simulação
   - Comparar políticas: Compara política fixa inteligente vs Q-Learning

3. **Modo de Execução (se simulação normal):**
   - APRENDIZAGEM: Treinar agentes
   - TESTE: Avaliar políticas pré-treinadas

4. **Algoritmo de Aprendizagem (se APRENDIZAGEM):**
   - Q-Learning (Reforço)
   - Algoritmo Genético (Evolutivo)

5. **Número de Agentes:**
   - Quantidade total de agentes na simulação

6. **Distribuição de Políticas (se simulação normal):**
   - **Modo APRENDIZAGEM:** Quantos agentes usam Q-Learning vs política fixa
   - **Modo TESTE:** Quantos agentes usam Q-table treinada vs política fixa
   - O CLI mostra quantas Q-tables estão disponíveis para o ambiente
   - Limita o número de agentes com Q-Learning ao número de Q-tables disponíveis

7. **Episódios:**
   - Número de episódios a executar (padrão: 100)

8. **Máximo de Passos:**
   - Número máximo de passos por episódio (padrão: 200)
   - Controla quando um episódio termina por timeout

9. **Gráficos (se simulação normal):**
   - Seleção de quais gráficos gerar no final:
     - Curva de Aprendizagem (Recompensa)
     - Passos por Episódio
     - Recompensa Descontada
     - Taxa de Sucesso Acumulada

### Funcionalidades Implementadas

#### Geração Dinâmica de Configuração

O CLI gera automaticamente um ficheiro JSON de configuração temporário baseado nas escolhas do utilizador:

```python
def gerar_config_dinamico(
    ambiente: str,
    modo: str,
    n_agentes: int,
    n_aprendizagem: int,
    episodios: int,
    max_passos: int,
) -> Dict[str, Any]
```

**Características:**
- Carrega template base do ambiente (`config_farol.json` ou `config_foraging.json`)
- Atualiza parâmetros com escolhas do utilizador
- Gera distribuição de agentes (Q-Learning vs política fixa)
- Posiciona agentes estrategicamente (cantos, bordas, ou aleatório)

#### Execução em Duas Fases

1. **Simulação Principal:**
   - Executa todos os episódios sem visualização (mais rápido)
   - Regista resultados em CSV
   - Guarda Q-tables (modo APRENDIZAGEM)

2. **Episódio Final com Visualização:**
   - Executa um único episódio com visualização ativada
   - Carrega Q-tables treinadas (se modo TESTE)
   - Desativa exploração (epsilon = 0) para demonstração

#### Geração Automática de Gráficos

Se o utilizador selecionar gráficos:

1. **Carrega dados do CSV** gerado durante a simulação
2. **Gera gráficos** usando Matplotlib:
   - Curva de Aprendizagem (com média móvel)
   - Passos por Episódio (com média móvel)
   - Recompensa Descontada (com média móvel)
   - Taxa de Sucesso Acumulada
3. **Guarda em PNG** no diretório `sma/analise/`
4. **Abre automaticamente** o ficheiro no visualizador de imagens do sistema

**Formato do ficheiro:** `{ambiente}_{modo}_graficos.png`

#### Tratamento de Erros

- **Cancelamento:** `Ctrl+C` cancela graciosamente a operação
- **Validação:** Todas as entradas são validadas (números positivos, limites, etc.)
- **Erros de Importação:** Avisos amigáveis se Matplotlib não estiver disponível

### Análise Avançada

O CLI inclui agora um menu de **Análise Avançada** com ferramentas para diagnóstico profundo:

#### 1. Comparação de Melhores Valores (Q-Tables)
Analisa todas as tabelas Q guardadas na pasta `sma/qtables/` para verificar a convergência do treino.
- **Estatísticas:** Mostra valores Q máximos e médios (indicador de confiança do agente).
- **Consenso:** Calcula a percentagem de estados onde todos os agentes concordam na mesma melhor ação.
- **Divergência:** Mostra exemplos de estados onde os agentes discordam.

#### 2. Demonstração de Limitações (Política Fixa)
Executa uma simulação num cenário "Armadilha" desenhado especificamente para expor as falhas da heurística fixa.
- **Cenário:** Agente começa dentro de um 'U' de obstáculos com o objetivo do outro lado.
- **Falha:** A heurística gananciosa tenta aproximar-se do alvo e bate na parede, recusando-se a afastar-se temporariamente para contornar o obstáculo.
- **Objetivo:** Demonstrar visualmente a necessidade de algoritmos de aprendizagem (como Q-Learning) que conseguem resolver estes mínimos locais.

### Exemplo de Uso

```
==================================================
   SIMULADOR MULTI-AGENTE - CLI INTERATIVO
==================================================

? Escolhe o ambiente a simular: FAROL
? Escolhe o modo de execucao: TESTE
? Quantos agentes no total? 2
? Quantos usam Q-table treinada? [0-2] 1
? Confirmas? 1 Q-table + 1 politica fixa = 2 total Yes
? Quantos episodios? 100
? Maximo de passos por episodio? 50
? Mostrar graficos no final? Yes
? Seleciona os graficos: [✓] Curva de Aprendizagem
                         [✓] Passos por Episodio
                         [✓] Recompensa Descontada
                         [✓] Taxa de Sucesso

==================================================
   INICIANDO SIMULACAO
==================================================

Configuracao:
   Ambiente: FAROL
   Modo: TESTE
   Agentes: 2
   Episodios: 100
   Max passos: 50

[... execucao da simulacao ...]

Resultados guardados em: sma/resultados/farol_teste_cli.csv

--------------------------------------------------
   EPISODIO FINAL (com visualizacao)
--------------------------------------------------

[... episodio final com janela grafica ...]

Graficos guardados em: sma/analise/farol_teste_graficos.png
Ficheiro aberto no visualizador de imagens.
```

### Vantagens do CLI

1. **Facilidade de Uso:** Não requer conhecimento de JSON ou parâmetros de linha de comando
2. **Validação Automática:** Previne erros de configuração
3. **Feedback Visual:** Mostra progresso e resultados claramente
4. **Flexibilidade:** Permite configurar todos os aspectos da simulação
5. **Automação:** Gera gráficos e abre ficheiros automaticamente
6. **Reprodutibilidade:** Configurações podem ser facilmente repetidas

### Integração com Sistema Existente

O CLI utiliza a mesma infraestrutura do simulador:
- Usa `carregar_simulacao()` do `loader.py`
- Compatível com todos os ambientes e agentes existentes
- Reutiliza sistema de registo de resultados
- Integra com sistema de análise de gráficos

---

## Sensores

### Arquitetura de Sensores

Os sensores implementam o padrão de design **Strategy**, permitindo que diferentes tipos de percepção sejam instalados nos agentes de forma flexível.

### Classe Base: `Sensor`

```python
class Sensor:
    def ler(self, ambiente: Any, agente: Any) -> Any:
        raise NotImplementedError
```

Todos os sensores devem implementar o método `ler()` que recebe o ambiente e o agente, e retorna os dados sensoriais.

### Fluxo de Percepção

1. **Simulador chama** `agente.observar(ambiente)`
2. **Agente itera** pelos sensores instalados e chama `sensor.ler(ambiente, agente)`
3. **Sensor acessa** métodos específicos do ambiente para obter informações
4. **Observação é retornada** e armazenada no agente

### Implementação no Agente

O método `observar()` do agente processa os sensores:

```python
def observar(self, ambiente) -> Observacao:
    if not self.sensores:
        return Observacao(dados=None)
    
    if len(self.sensores) == 1:
        dados = self.sensores[0].ler(ambiente, self)
        return Observacao(dados=dados)
    
    # Múltiplos sensores: combina em dicionário
    dados = {}
    for i, sensor in enumerate(self.sensores):
        nome = sensor.__class__.__name__
        dados[f"{nome}_{i}"] = sensor.ler(ambiente, self)
    return Observacao(dados=dados)
```

### Sensores Implementados

#### 1. `SensorDirecaoFarol`

**Uso:** Ambiente Farol

**Funcionalidade:**
- Retorna a direção do farol (global)
- Retorna informações da vizinhança (local) - 8 direções (cardeais + diagonais)
- Indica se o agente está no farol

**Dados retornados:**
```python
{
    "dir_farol": (dx, dy),      # Direção do farol: valores em {-1, 0, 1}
    "viz": {                     # Vizinhança (8 direções)
        (0, -1): valor,          # Norte
        (0, 1): valor,            # Sul
        (1, 0): valor,             # Este
        (-1, 0): valor,            # Oeste
        (1, 1): valor,             # Nordeste
        (1, -1): valor,            # Sudeste
        (-1, 1): valor,             # Noroeste
        (-1, -1): valor,           # Sudoeste
    },
    "no_farol": bool             # True se está no farol
}
```

**Valores na vizinhança:**
- `0`: Célula vazia
- `1`: Farol
- `2`: Obstáculo
- `-1`: Fora dos limites do ambiente

**Configuração:**
- `diagonais: bool = True`: Inclui ou não as direções diagonais

#### 2. `SensorVizinhancaGrid`

**Uso:** Ambiente Foraging

**Funcionalidade:**
- Retorna informações da vizinhança (local) - 8 direções (cardeais + diagonais)
- Retorna informações globais (direção do ninho, recursos, etc.)

**Dados retornados:**
```python
{
    "viz": {                     # Vizinhança (8 direções)
        (0, -1): valor,          # Norte
        (0, 1): valor,            # Sul
        (1, 0): valor,            # Este
        (-1, 0): valor,           # Oeste
        (1, 1): valor,            # Nordeste
        (1, -1): valor,           # Sudeste
        (-1, 1): valor,           # Noroeste
        (-1, -1): valor,          # Sudoeste
    },
    "carregando": int,           # Quantidade de recurso carregando
    "dir_ninho": (dx, dy),       # Direção para o ninho
    "dist_ninho": int,            # Distância Manhattan até o ninho (max 10)
    "dir_recurso": (dx, dy),      # Direção para o recurso mais próximo
    "no_ninho": bool,             # True se está no ninho
    "no_recurso": bool            # True se está em um recurso
}
```

**Valores na vizinhança:**
- `0`: Célula vazia
- `2`: Recurso
- `3`: Ninho
- `9`: Obstáculo
- `-1`: Fora dos limites do ambiente

**Configuração:**
- `raio: int = 1`: Raio de percepção (atualmente sempre 1)
- `diagonais: bool = True`: Inclui ou não as direções diagonais

### Modelação da Percepção

**Farol:**
- **Percepção híbrida:** Local (vizinhança) + Global (direção do farol)
- O agente vê o que está ao redor (obstáculos, limites) e sabe a direção geral do farol
- Permite navegação local evitando obstáculos e navegação global em direção ao objetivo

**Foraging:**
- **Percepção híbrida:** Local (vizinhança) + Global (direções do ninho e recursos)
- O agente vê o que está ao redor (recursos, ninho, obstáculos) e tem informações globais sobre objetivos
- Permite decisões locais (coletar recurso próximo) e globais (ir para o ninho)

---

## Agentes

### Interface do Agente

A classe `Agente` implementa a interface especificada no enunciado:

```python
class Agente(threading.Thread, ABC):
    @staticmethod
    def cria(cfg: str) -> "Agente"
    def observacao(obs: Observacao)
    def age() -> Accao
    def avaliacaoEstadoAtual(recompensa: float)
    def instala(sensor: Sensor)
    def comunica(mensagem: String, de_agente: Agente)
```

### Implementação como Thread

Os agentes são implementados como threads independentes (`threading.Thread`), permitindo execução paralela. A sincronização é feita através de barreiras:

- **Barreira de Percepção:** Todos os agentes recebem observações antes de decidir ações
- **Barreira de Ação:** Todas as ações são decididas antes de serem executadas

### Agentes Implementados

#### 1. `AgenteFarol`

**Sensor instalado:** `SensorDirecaoFarol`

**Ações disponíveis:**
- `MoverN`, `MoverS`, `MoverE`, `MoverO`: Movimento nas 4 direções cardeais
- `Stay`: Permanecer no mesmo lugar

**Políticas suportadas:**
- `PoliticaFixa`: Sempre executa a mesma ação
- `PoliticaFixaInteligente`: Usa heurísticas baseadas em observações
- `PoliticaQLearning`: Aprendizagem por reforço

**Comunicação:**
- Implementa `processar_comunicacao()` que envia mensagens quando encontra o farol ou quando está próximo de outros agentes
- Usa `broadcast_mensagem()` para notificar todos os agentes quando encontra o farol
- Usa `enviar_mensagem()` para comunicação direta com agentes próximos (distância <= 2)

#### 2. `AgenteForager`

**Sensor instalado:** `SensorVizinhancaGrid`

**Ações disponíveis:**
- `MoverN`, `MoverS`, `MoverE`, `MoverO`: Movimento nas 4 direções cardeais
- `Stay`: Permanecer no mesmo lugar
- `Coletar`: Coletar recurso na posição atual
- `Depositar`: Depositar recurso no ninho

**Estado adicional:**
- `carregando: int`: Quantidade de recurso que está carregando

**Políticas suportadas:**
- `PoliticaFixa`: Sempre executa a mesma ação
- `PoliticaFixaInteligente`: Usa heurísticas baseadas em observações
- `PoliticaQLearning`: Aprendizagem por reforço

**Comunicação:**
- Implementa `processar_comunicacao()` que envia mensagens quando coleta recursos, deposita no ninho, ou quando está próximo de outros agentes
- Usa `broadcast_mensagem()` para notificar todos os agentes sobre eventos importantes (coleta, depósito)
- Usa `enviar_mensagem()` para comunicação direta com agentes próximos (distância <= 2)

---

## Ambientes

### Ambiente Farol (`AmbienteFarol`)

**Características:**
- Espaço 2D (grelha)
- Um farol em posição fixa
- Suporte para obstáculos
- Objetivo: Agente deve chegar ao farol

**Métodos específicos:**
- `direcao_para_farol(pos_ag) -> Tuple[int, int]`: Retorna direção do farol
- `vizinhanca(pos, raio, diagonais, agente) -> dict`: Retorna informações da vizinhança

**Recompensas:**
- `99.0`: Chegou ao farol
- `-1.0`: Movimento normal
- `-10.0`: Tentou mover para fora dos limites ou para obstáculo

### Ambiente Foraging (`AmbienteForaging`)

**Características:**
- Espaço 2D (grelha)
- Recursos com valores diferentes
- Ninho/ponto de entrega
- Suporte para obstáculos
- Objetivo: Maximizar recursos coletados e depositados no ninho

**Métodos específicos:**
- `vizinhanca(pos, raio, diagonais, agente) -> dict`: Retorna informações completas da vizinhança e objetivos

**Recompensas:**
- `+5.0`: Coletou recurso
- `+valor * 2.0`: Depositou recurso no ninho
- `+0.5`: Movendo-se em direção ao ninho (carregando recurso)
- `+0.3`: Movendo-se em direção a recurso (sem carga)
- `-0.1`: Movimento normal
- `-2.0`: Tentou coletar/depositar em condições inválidas
- `-5.0`: Tentou mover para fora dos limites ou para obstáculo

**Configuração Dinâmica:**
- **Escala com Agentes:** O tamanho do mapa e o número de recursos ajustam-se automaticamente ao número de agentes.
- **Recursos:** `max(4, n_agentes * 2)` recursos gerados aleatoriamente (evitando o ninho).
- **Mapa:** Tamanho aumenta para 15x15 (padrão) para acomodar mais agentes.

**Condição de término:**
- Todos os recursos foram coletados E todos os agentes depositaram suas cargas

---

## Políticas

### Classe Base: `Politica`

Interface abstrata que define o contrato para políticas de decisão:

```python
class Politica:
    def selecionar_acao(self, estado: Observacao) -> Accao
    def atualizar(self, estado, accao, recompensa, prox_estado)
    def set_modo(self, modo: str)
    def guardar(self, caminho: str)
    def carregar(self, caminho: str) -> bool
```

### Políticas Implementadas

#### 1. `PoliticaFixa`

Política pré-programada que sempre retorna a mesma ação.

**Uso:** Agentes de referência, testes básicos

#### 2. `PoliticaFixaInteligente`

Política fixa que usa heurísticas baseadas nas observações dos sensores. Mais inteligente que `PoliticaFixa` e útil para comparação com políticas aprendidas.

**Heurísticas Melhoradas:**
- **Navegação Baseada em Distância:** Calcula a distância Manhattan para o alvo (farol, recurso ou ninho) para cada movimento possível.
- **Evitamento de Obstáculos:** Verifica se a posição alvo está livre antes de mover.
- **Desempate Aleatório:** Se múltiplos movimentos tiverem a mesma distância mínima para o alvo, escolhe aleatoriamente entre eles para evitar loops infinitos.
- **Estados Especiais (Foraging):**
  - Se está no ninho e carregando: deposita
  - Se está num recurso e não está carregando: coleta

**Uso:** Comparação com políticas aprendidas, baseline robusta.

**Configuração:**
```json
{
  "politica": {
    "tipo": "fixa_inteligente"
  }
}
```

#### 3. `PoliticaGenetica`

Política evolutiva que usa um Algoritmo Genético para otimizar pesos de um modelo linear de decisão.

**Características:**
- **Cromossoma:** Vetor de números reais (pesos) que mapeia features para preferências de ação.
- **Modelo Linear:** `Score(acao) = dot(Pesos_acao, Features) + Bias_acao`. A ação com maior score é selecionada.
- **Features (Input):**
  1. Direção normalizada para o objetivo (X, Y)
  2. Sensores de obstáculo nas 4 direções (N, S, E, O)
  3. Estados de posição (no farol, no ninho, no recurso)
  4. **Memória:** Última ação realizada (One-Hot encoding)
  5. **Sinal de Bloqueio:** Indica se a última ação resultou em bloqueio

**Evolução:**
- **População:** 50 indivíduos (configurável)
- **Seleção:** Torneio
- **Crossover:** Aritmético (média dos pais)
- **Mutação:** Adição de ruído gaussiano (taxa 0.1)

**Uso:** Alternativa ao Q-Learning para espaços de estados grandes ou contínuos.

#### 4. `PoliticaQLearning`

Implementação do algoritmo Q-Learning para aprendizagem por reforço.

**Parâmetros ajustáveis:**

Os parâmetros podem ser configurados nos ficheiros JSON (`config_*.json`) na secção `politica` de cada agente:

- **`alfa`** (taxa de aprendizagem): Controla a velocidade de atualização dos valores Q
  - Valores típicos: 0.1 (conservador, aprende devagar) a 0.5 (agressivo, aprende rápido)
  - Padrão: 0.2-0.3
  - Valores mais altos = aprende mais rápido mas pode ser instável
  - Valores mais baixos = aprende devagar mas mais estável

- **`gama`** (fator de desconto): Controla a importância de recompensas futuras vs imediatas
  - Valores típicos: 0.8-0.99
  - Padrão: 0.9-0.95
  - Valores mais altos (0.95) = pensa mais à frente, planeia melhor
  - Valores mais baixos (0.7-0.8) = foca mais no imediato

- **`epsilon`** (taxa de exploração): Probabilidade de escolher ação aleatória durante aprendizagem
  - Valores típicos: 0.05-0.4
  - Padrão: 0.1-0.2 (Farol), 0.2-0.35 (Foraging)
  - Valores mais altos = explora mais, descobre novas estratégias
  - Valores mais baixos = explora mais, usa o que já aprendeu
  - Em modo TESTE, sempre 0 (só usa o que aprendeu)

**Funcionamento:**
1. **Seleção de ação (ε-greedy):**
   - Modo APRENDIZAGEM: Com probabilidade `epsilon`, escolhe ação aleatória (explora). Caso contrário, escolhe a melhor ação conhecida (explora)
   - Modo TESTE: Sempre escolhe a melhor ação (ε=0, sem exploração)

2. **Atualização Q-value:**
   ```
   Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
   ```
   Onde:
   - `Q(s,a)`: Valor atual da ação `a` no estado `s`
   - `r`: Recompensa recebida
   - `γ * max(Q(s',a'))`: Melhor valor futuro (descontado por gama)
   - `α`: Taxa de aprendizagem (alfa)

3. **Persistência:**
   - Q-tables são guardadas em ficheiros JSON após aprendizagem (em `sma/qtables/`)
   - Q-tables são carregadas automaticamente em modo TESTE
   - Formato: `qtable_{agente_id}.json`

**Representação de estados:**
- Estados são representados como strings usando `repr(obs.dados)`
- Permite usar qualquer estrutura de dados como estado (tuplas, dicionários, etc.)
- Cada combinação única de observação = um estado na Q-table

### Funcionamento do Q-Learning no Projeto

#### Representação de Estados

O Q-Learning usa `repr(obs.dados)` para criar uma chave única que identifica cada estado. Esta chave é usada para indexar a Q-table.

**Exemplo - Farol:**
```python
# Observação do sensor
obs.dados = {
    "dir_farol": (1, 1),
    "viz": {(0, -1): -1, (0, 1): 0, (1, 0): 0, (-1, 0): -1, ...},
    "no_farol": False
}

# Chave na Q-table
chave = repr(obs.dados)
# Resultado: "{'dir_farol': (1, 1), 'viz': {...}, 'no_farol': False}"
```

**Exemplo - Foraging:**
```python
# Observação do sensor
obs.dados = {
    "viz": {(0, -1): -1, (0, 1): 0, (1, 0): 2, ...},
    "carregando": 0,
    "dir_ninho": (1, 1),
    "dist_ninho": 5,
    "dir_recurso": (1, 0),
    "no_ninho": False,
    "no_recurso": False
}

# Chave na Q-table
chave = repr(obs.dados)
```

#### Ciclo de Aprendizagem

**1. Inicialização:**
- Q-table começa vazia: `Q = {}`
- Quando um estado novo é encontrado, todas as ações são inicializadas com Q-value = 0.0

**2. Seleção de Ação (ε-greedy):**
```python
# Modo APRENDIZAGEM
if random.random() < epsilon:
    acao = random.choice(acoes)  # Exploração
else:
    acao = max(Q[estado], key=Q[estado].get)  # Exploração (melhor ação conhecida)

# Modo TESTE
acao = max(Q[estado], key=Q[estado].get)  # Sempre melhor ação
```

**3. Execução e Recompensa:**
- Ação é executada no ambiente
- Ambiente retorna recompensa `r`
- Ambiente transita para novo estado `s'`

**4. Atualização Q-value:**
```python
Q[s][a] = Q[s][a] + α * (r + γ * max(Q[s']) - Q[s][a])
```

Onde:
- `Q[s][a]`: Q-value atual do estado `s` e ação `a`
- `r`: Recompensa recebida
- `γ * max(Q[s'])`: Melhor Q-value do próximo estado (descontado)
- `α`: Taxa de aprendizagem (controla velocidade de atualização)

#### Exemplo Prático - Farol

**Estado inicial:**
```python
estado = {
    "dir_farol": (1, 1),  # Farol a sudeste
    "viz": {(1, 0): 0, (0, 1): 0, ...},  # Células livres
    "no_farol": False
}
```

**Ações disponíveis:** `MoverN`, `MoverS`, `MoverE`, `MoverO`, `Stay`

**Ciclo de aprendizagem:**

1. **Primeira vez neste estado:**
   - Q-table inicializa: `Q[estado] = {MoverN: 0.0, MoverS: 0.0, MoverE: 0.0, MoverO: 0.0, Stay: 0.0}`
   - Escolhe ação aleatória (exploração): `MoverE`

2. **Execução:**
   - Move para Este
   - Recompensa: `-1.0` (movimento normal)
   - Novo estado: mais próximo do farol

3. **Atualização:**
   ```python
   # Supondo α=0.2, γ=0.95
   Q[estado][MoverE] = 0.0 + 0.2 * (-1.0 + 0.95 * max(Q[novo_estado]) - 0.0)
   # Se max(Q[novo_estado]) = 0.0 (estado novo)
   Q[estado][MoverE] = 0.0 + 0.2 * (-1.0 + 0.0) = -0.2
   ```

4. **Após várias iterações:**
   - Se `MoverE` leva consistentemente mais perto do farol, Q-value aumenta
   - Se `MoverO` leva para longe, Q-value diminui
   - Q-table aprende qual ação é melhor em cada estado

**Q-table treinada (exemplo):**
```json
{
  "{'dir_farol': (1, 1), ...}": {
    "MoverN": -18.84,  // Pior (move para longe)
    "MoverS": -9.98,   // Melhor
    "MoverE": -9.97,   // Melhor
    "MoverO": -18.56,  // Pior
    "Stay": -9.98
  }
}
```

#### Exemplo Prático - Foraging

**Estado: Agente sem carga, recurso próximo**
```python
estado = {
    "viz": {(1, 0): 2, ...},  # Recurso a Este
    "carregando": 0,
    "dir_recurso": (1, 0),
    "no_recurso": False,
    ...
}
```

**Ações disponíveis:** `MoverN`, `MoverS`, `MoverE`, `MoverO`, `Stay`, `Coletar`, `Depositar`

**Ciclo de aprendizagem:**

1. **Estado inicial:**
   - Q-table inicializa todas as ações com 0.0
   - Escolhe ação: `MoverE` (exploração)

2. **Execução:**
   - Move para Este (em direção ao recurso)
   - Recompensa: `-0.1` (movimento) + `0.3` (aproximando-se do recurso) = `+0.2`
   - Novo estado: mais próximo do recurso

3. **Quando chega ao recurso:**
   - Estado: `{"no_recurso": True, "carregando": 0, ...}`
   - Ação: `Coletar`
   - Recompensa: `+5.0` (coletou recurso)
   - Novo estado: `{"carregando": 5, ...}`

4. **Com recurso coletado:**
   - Estado: `{"carregando": 5, "dir_ninho": (-1, -1), ...}`
   - Ação: `MoverO` (em direção ao ninho)
   - Recompensa: `-0.1` + `0.5` (aproximando-se do ninho) = `+0.4`

5. **Quando chega ao ninho:**
   - Estado: `{"no_ninho": True, "carregando": 5, ...}`
   - Ação: `Depositar`
   - Recompensa: `+5.0 * 2.0 = +10.0` (depositou recurso)

**Aprendizagem:**
- Q-Learning aprende que `Coletar` quando `no_recurso=True` e `carregando=0` é bom (+5.0)
- Aprende que `Depositar` quando `no_ninho=True` e `carregando>0` é muito bom (+10.0)
- Aprende que mover em direção ao recurso quando `carregando=0` é bom
- Aprende que mover em direção ao ninho quando `carregando>0` é bom

#### Estrutura da Q-table

A Q-table é um dicionário de dicionários:

```python
Q = {
    "chave_estado_1": {
        TipoAccao.MoverN: -5.2,
        TipoAccao.MoverS: 3.1,
        TipoAccao.MoverE: 4.5,  # Melhor ação
        ...
    },
    "chave_estado_2": {
        ...
    },
    ...
}
```

**Guardar Q-table:**
- Guardada em JSON após cada episódio em modo APRENDIZAGEM
- Sempre guardada em `sma/qtables/` (independentemente do local do ficheiro de configuração)
- Formato: `qtable_{agente_id}.json`
- Inclui: Q-values, ações, parâmetros (alfa, gama, epsilon)
- Sobrepõe Q-tables existentes com o mesmo ID
- Mostra mensagem resumo: "Total: X Q-table(s) guardada(s) de Y agente(s)"

**Carregar Q-table:**
- Carregada automaticamente em modo TESTE
- Carregada de `sma/qtables/` (localização fixa)
- Permite usar política treinada sem re-treinar
- Se Q-table não existir para um agente Q-Learning em modo TESTE, o agente usa política fixa inteligente como fallback

#### Vantagens e Limitações

**Vantagens:**
- Aprende estratégias ótimas através de tentativa e erro
- Não precisa de modelo do ambiente
- Funciona com qualquer estrutura de observação
- Persistência (pode guardar e carregar conhecimento)

**Limitações:**
- Espaço de estados pode ser muito grande (cada combinação única de observação = novo estado)
- Pode precisar de muitos episódios para convergir
- Exploração vs Exploração: muito epsilon = lento, pouco epsilon = pode ficar preso em sub-ótimo

---

## Modos de Operação

### Modo APRENDIZAGEM

**Características:**
- **Q-table é modificada:** A política Q-Learning atualiza os Q-values a cada passo durante a simulação
- **Aprendizagem ativa:** O método `atualizar()` é chamado após cada ação, modificando a Q-table
- **Exploração ativa:** Usa estratégia ε-greedy (explora com probabilidade ε, explora com probabilidade 1-ε)
- **Q-tables são guardadas:** No final da execução, as Q-tables são guardadas em ficheiros JSON

**Funcionamento:**
```python
# A cada passo:
1. Agente observa estado s
2. Escolhe ação a (ε-greedy: explora ou explora)
3. Executa ação, recebe recompensa r, transita para estado s'
4. Atualiza Q-table: Q[s][a] = Q[s][a] + α * (r + γ * max(Q[s']) - Q[s][a])
5. Repete até fim do episódio
6. No final: guarda Q-table em ficheiro JSON
```

**Uso:** Treinar agentes para aprender estratégias ótimas através de tentativa e erro

**Exemplo:**
```bash
# Treinar agente (modifica Q-table durante execução)
python -m sma.run farol --episodios 100
# Q-table é guardada em: sma/qtables/qtable_AgenteFarol_0.json
# Se já existir, é sobreposta
```

### Modo TESTE

**Características:**
- **Q-table é carregada:** A Q-table pré-treinada é carregada automaticamente do ficheiro JSON
- **Q-table não é modificada:** O método `atualizar()` não faz nada (retorna imediatamente)
- **Sem exploração:** ε = 0.0, sempre escolhe a melhor ação conhecida
- **Política fixa:** Usa apenas o conhecimento já aprendido, sem aprender nada novo

**Funcionamento:**
```python
# No início:
1. Carrega Q-table do ficheiro JSON (qtables/qtable_AgenteFarol_0.json)

# A cada passo:
1. Agente observa estado s
2. Sempre escolhe melhor ação: a = max(Q[s], key=Q[s].get)
3. Executa ação, recebe recompensa r, transita para estado s'
4. NÃO atualiza Q-table (modo TESTE, atualizar() retorna sem fazer nada)
5. Repete até fim do episódio
6. No final: NÃO guarda Q-table (já está guardada)
```

**Uso:** Avaliar desempenho de políticas pré-treinadas sem modificar o conhecimento aprendido

**Exemplo:**
```bash
# Testar política treinada (usa Q-table existente, não a modifica)
python -m sma.run farol --episodios 10
# Q-table é carregada de: sma/qtables/qtable_AgenteFarol_0.json
# Q-table NÃO é modificada durante a execução
# Q-table NÃO é guardada no final
```

**Métricas registadas:**
- Número de passos até terminar
- Recompensa total por episódio
- Recompensa descontada
- Taxa de sucesso

### Comparação: APRENDIZAGEM vs TESTE

| Aspecto | Modo APRENDIZAGEM | Modo TESTE |
|--------|-------------------|------------|
| **Q-table** | Modificada a cada passo | Carregada e nunca modificada |
| **Aprendizagem** | Sim, atualiza Q-values | Não, apenas usa conhecimento existente |
| **Exploração** | Sim (ε-greedy) | Não (ε=0, sempre melhor ação) |
| **Carregamento** | Não carrega (começa vazia ou continua) | Carrega automaticamente do ficheiro |
| **Guardar** | Guarda no final | Não guarda |
| **Objetivo** | Aprender estratégias | Avaliar estratégias aprendidas |

### Por que usar Modo TESTE?

1. **Avaliação justa:** Testa o conhecimento aprendido sem modificá-lo
2. **Reprodutibilidade:** Mesma Q-table sempre produz mesmos resultados
3. **Comparação:** Permite comparar diferentes políticas treinadas
4. **Análise:** Foca apenas em desempenho, não em aprendizagem
5. **Eficiência:** Não precisa recalcular Q-values (mais rápido)

---

## Sincronização e Threads

### Arquitetura de Threads

Cada agente é uma thread independente que executa em paralelo:

```python
class Agente(threading.Thread, ABC):
    def run(self):
        while self._ativo:
            # Espera barreira de percepção
            self._barreira_percepcao.wait()
            
            # Decide ação
            self._accao_pronta = self.age()
            
            # Espera barreira de ação
            self._barreira_acao.wait()
```

### Barreiras de Sincronização

**Barreira de Percepção:**
- Garante que todos os agentes recebem observações antes de decidir ações
- Evita condições de corrida na leitura do estado do ambiente

**Barreira de Ação:**
- Garante que todas as ações são decididas antes de serem executadas
- Permite execução determinística das ações

### Ciclo de Simulação

```
Para cada passo:
    1. Simulador obtém observações para todos os agentes
    2. Barreira de Percepção: agentes recebem observações
    3. Barreira de Ação: agentes decidem ações
    4. Simulador executa ações e calcula recompensas
    5. Agentes recebem recompensas e atualizam políticas (se em modo APRENDIZAGEM)
    6. Ambiente atualiza estado
```

### Vantagens da Abordagem

- **Modularidade:** Agentes podem ser desenvolvidos independentemente
- **Extensibilidade:** Fácil adicionar novos tipos de agentes
- **Paralelização:** Preparado para execução paralela (embora atualmente sequencial no ambiente)
- **Sincronização:** Garante consistência do estado

---

## Comunicação entre Agentes

### Sistema de Comunicação

O simulador implementa um sistema de comunicação entre agentes que permite troca de mensagens durante a simulação.

### Interface de Comunicação

**No Agente:**
- `comunica(mensagem: str, de_agente: Agente)`: Recebe uma mensagem de outro agente e armazena na fila de mensagens
- `obter_mensagens() -> List[dict]`: Retorna todas as mensagens recebidas e limpa a lista
- `tem_mensagens() -> bool`: Verifica se há mensagens pendentes
- `processar_comunicacao(simulador, ambiente)`: Método opcional que os agentes podem implementar para processar eventos e enviar mensagens

**No Simulador:**
- `enviar_mensagem(de_agente: Agente, para_agente: Agente, mensagem: str)`: Envia uma mensagem de um agente para outro específico
- `broadcast_mensagem(de_agente: Agente, mensagem: str, excluir_remetente: bool = True)`: Envia uma mensagem de um agente para todos os outros agentes

### Funcionamento

1. **Processamento de Comunicação:**
   - Após cada ação, o simulador chama `processar_comunicacao()` em cada agente (se implementado)
   - Os agentes podem decidir enviar mensagens baseadas em eventos ou proximidade

2. **Armazenamento:**
   - Mensagens recebidas são armazenadas na fila `_mensagens_recebidas` de cada agente
   - Cada mensagem contém o texto e o agente remetente

3. **Uso pelas Políticas:**
   - As políticas podem acessar mensagens através de `obter_mensagens()` ou `tem_mensagens()`
   - Permite implementar comportamentos coordenados ou cooperativos

### Exemplos de Uso

**AgenteFarol:**
- Envia broadcast quando encontra o farol
- Envia mensagem direta para agentes próximos (distância <= 2) com sua posição e direção do farol

**AgenteForager:**
- Envia broadcast quando coleta um recurso
- Envia broadcast quando deposita recursos no ninho
- Envia mensagem direta para agentes próximos (distância <= 2) com sua posição e estado (carregando ou livre)

### Ativação/Desativação

A comunicação pode ser controlada através do atributo `_comunicacao_ativa` do simulador (padrão: `True`). Quando desativada, `processar_comunicacao()` não é chamado.

---

## Métricas de Desempenho

### Métricas Implementadas

O `RegistadorResultados` regista as seguintes métricas:

1. **Passos por episódio:** Número de ações até terminar o episódio
2. **Recompensa total:** Soma de todas as recompensas no episódio
3. **Recompensa descontada:** Soma de recompensas com desconto temporal
4. **Taxa de sucesso:** Percentagem de episódios que terminaram com sucesso
5. **Valor total depositado:** Valor total de recursos depositados (Foraging)

### Métricas por Problema

#### Farol
- **Objetivo:** Minimizar passos até chegar ao farol
- **Métrica principal:** Número médio de passos
- **Métrica secundária:** Taxa de sucesso

#### Foraging
- **Objetivo:** Maximizar recursos coletados e depositados
- **Métrica principal:** Recompensa total média
- **Métricas secundárias:** 
  - Número de recursos coletados
  - Valor total depositado
  - Eficiência (recursos/ passos)

### Exportação de Resultados

Os resultados podem ser exportados para CSV para análise posterior:

```python
sim.registador_resultados.exportarCSV("resultados.csv")
```

**Via CLI:**
- O CLI exporta automaticamente para `sma/resultados/{ambiente}_{modo}_cli.csv`
- Formato: `episodio`, `passos`, `recompensa_total`, `recompensa_descontada`, `sucesso`, `valor_total_depositado`

### Sistema Automático de Análise

Foi implementado um sistema completo para gerar automaticamente:

1. **Curvas de Aprendizagem:** Gráficos mostrando evolução do desempenho
2. **Análise Estatística:** Relatórios com métricas detalhadas
3. **Comparação de Políticas:** Gráficos comparativos entre diferentes políticas

#### Geração Automática

**Via CLI Interativo (Recomendado):**
```bash
./run.sh
# Seleciona gráficos desejados no final do CLI
# Gráficos são gerados e abertos automaticamente
```

**Durante a execução (Modo Manual):**
```bash
# Treinar e gerar análise automaticamente
python -m sma.run farol --episodios 100 --gerar-analise
```

**A partir de CSV existente:**
```bash
# Gerar curva de aprendizagem
python -m sma.gerar_analise resultados.csv --nome farol

# Comparar duas políticas
python -m sma.gerar_analise fixa.csv --comparar aprendida.csv
```

#### Curva de Aprendizagem

O gráfico gerado inclui 4 painéis:

1. **Passos por Episódio:**
   - Mostra evolução do número de passos
   - Inclui média móvel (janela de 10) para suavizar
   - Ideal: deve diminuir ao longo do tempo

2. **Recompensa por Episódio:**
   - Mostra evolução da recompensa total
   - Inclui média móvel para identificar tendências
   - Ideal: deve aumentar ao longo do tempo

3. **Taxa de Sucesso:**
   - Mostra percentagem de episódios bem-sucedidos
   - Média móvel para ver tendência
   - Ideal: deve aumentar e estabilizar próximo de 100%

4. **Estatísticas Comparativas:**
   - Compara primeira metade vs segunda metade
   - Mostra melhoria quantitativa
   - Inclui passos médios, recompensa média, taxa de sucesso

#### Análise em Modo Teste

Para avaliar políticas pré-treinadas:

```bash
# Testar política treinada
python -m sma.run farol --episodios 10 --gerar-analise
```

**Métricas geradas:**
- Taxa de sucesso (percentagem)
- Passos médios (com desvio padrão)
- Recompensa média (com desvio padrão)
- Análise por quartis (evolução ao longo dos episódios)

#### Comparação de Políticas

O sistema permite comparar automaticamente:

- **Política Fixa vs Política Aprendida:**
  ```bash
  python -m sma.comparar_politicas config.json --episodios 10
  python -m sma.gerar_analise resultados_fixa.csv --comparar resultados_aprendida.csv
  ```

**Gráfico comparativo inclui:**
- Passos médios (com barras de erro)
- Recompensa média (com barras de erro)
- Taxa de sucesso
- Evolução da recompensa (curvas sobrepostas)

---

## Gráficos Disponíveis e Interpretação

Esta secção detalha todos os gráficos disponíveis no simulador, o que cada um mostra e como interpretar os resultados para cada ambiente.

### Gráficos do Modo Simulação (CLI)

Ao executar uma simulação via CLI (`./run.sh`), o utilizador pode selecionar 4 tipos de gráficos:

#### 1. Curva de Aprendizagem (Recompensa)

| Característica | Descrição |
|----------------|-----------|
| **Eixo X** | Número do episódio |
| **Eixo Y** | Recompensa total obtida no episódio |
| **Linha Transparente** | Valores reais (com ruído natural) |
| **Linha Destacada** | Média móvel (janela de 10 episódios) |

**Interpretação por Ambiente:**

| Ambiente | O que esperar | Sinal de Sucesso | Sinal de Problema |
|----------|---------------|------------------|-------------------|
| **Farol** | Recompensa sobe de ~-200 (timeout) para ~+90 (chegar rápido) | Curva ascendente estável | Curva plana ou descendente |
| **Foraging** | Recompensa varia com valor dos recursos depositados | Curva ascendente com maior variância | Curva negativa constante (não deposita) |

**Ponto de Convergência:** Quando a linha da média móvel estabiliza, o agente atingiu o seu desempenho máximo com os parâmetros atuais.

---

#### 2. Passos por Episódio

| Característica | Descrição |
|----------------|-----------|
| **Eixo X** | Número do episódio |
| **Eixo Y** | Número de ações executadas até terminar o episódio |
| **Linha Destacada** | Média móvel (janela de 10 episódios) |

**Interpretação por Ambiente:**

| Ambiente | O que esperar | Sinal de Sucesso | Sinal de Problema |
|----------|---------------|------------------|-------------------|
| **Farol** | Passos devem diminuir de ~200 (max) para ~10-30 (ótimo) | Curva descendente acentuada | Curva constante perto do máximo (timeout) |
| **Foraging** | Passos podem variar - menos passos nem sempre é melhor | Estabilização num valor razoável | Sempre no máximo (agente perdido) |

**Nota:** No Foraging, um agente eficiente pode usar mais passos se recolher mais recursos. No Farol, menos passos é sempre melhor.

---

#### 3. Recompensa Descontada (γ = 0.99)

| Característica | Descrição |
|----------------|-----------|
| **Eixo X** | Número do episódio |
| **Eixo Y** | Soma de recompensas com desconto temporal: Σ(γ^t × r_t) |
| **Fator de Desconto** | γ = 0.99 (usado no Q-Learning) |

**Interpretação:**

- **O que mede:** Penaliza soluções lentas. Uma recompensa de +99 no passo 100 vale menos do que +99 no passo 10.
- **Farol:** Recompensa descontada alta = caminho curto até ao farol.
- **Foraging:** Recompensa descontada alta = depositou recursos rapidamente.

**Comparação com Recompensa Total:**
- Se a recompensa total é alta mas a descontada é baixa → o agente consegue, mas demora muito.
- Se ambas são altas → o agente é eficiente.

---

#### 4. Taxa de Sucesso Acumulada

| Característica | Descrição |
|----------------|-----------|
| **Eixo X** | Número do episódio |
| **Eixo Y** | Percentagem de episódios bem-sucedidos até ao momento |
| **Linha de Referência** | 50% (linha tracejada cinza) |

**Interpretação por Ambiente:**

| Ambiente | Critério de Sucesso | Taxa Esperada (Treinado) |
|----------|---------------------|--------------------------|
| **Farol** | Agente chegou ao farol antes do timeout | >90% após 50-100 episódios |
| **Foraging** | Todos os recursos foram depositados no ninho | Depende do número de recursos/agentes |

**Leitura do Gráfico:**
- **Subida rápida inicial:** O agente está a aprender rapidamente.
- **Estabilização perto de 100%:** O agente dominou o problema.
- **Estabilização abaixo de 50%:** O agente não aprendeu efetivamente (verificar parâmetros).

---

### Gráficos do Modo Comparação (6 painéis)

Ao escolher "Comparar políticas" no CLI, são gerados 6 gráficos lado a lado:

#### Linha Superior (Barras de Comparação)

| Gráfico | O que compara | Interpretação |
|---------|---------------|---------------|
| **Passos Médios** | Barra laranja (Fixa) vs Barra azul (Q-Learning) | Barra mais baixa = política mais eficiente |
| **Taxa de Sucesso** | Percentagem de sucesso de cada política | Barra mais alta = política mais confiável |
| **Recompensa Média** | Recompensa total média de cada política | Barra mais alta = política mais lucrativa |

**Barras de Erro:** As linhas verticais sobre as barras mostram o desvio padrão. Barras de erro grandes = resultados inconsistentes.

#### Linha Inferior (Evolução Temporal)

| Gráfico | O que mostra | Interpretação |
|---------|--------------|---------------|
| **Evolução dos Passos** | Linhas sobrepostas ao longo dos episódios | A linha que desce mais = aprende a ser mais eficiente |
| **Evolução da Recompensa** | Linhas sobrepostas ao longo dos episódios | A linha que sobe mais = aprende a maximizar ganho |
| **Evolução da Recompensa Descontada** | Linhas sobrepostas ao longo dos episódios | A linha mais alta = consegue resultados mais rápido |

**Cores:**
- **Laranja:** Política Fixa Inteligente (baseline)
- **Azul:** Política Aprendida (Q-Learning)

**Exemplo de Interpretação:**
```
Se a linha azul (Q-Learning) está consistentemente acima da laranja (Fixa):
→ A aprendizagem melhorou o desempenho relativamente à heurística fixa.

Se as linhas se cruzam ou estão próximas:
→ A política fixa é competitiva para este problema (ou o treino foi insuficiente).
```

---

### Ficheiros de Saída

| Modo | Ficheiros Gerados | Localização |
|------|-------------------|-------------|
| Simulação Normal | `{ambiente}_{modo}_graficos.png` | `sma/analise/` |
| Comparação | `comparacao_politicas.png` | `sma/resultados/` |
| Dados Brutos | `{ambiente}_{modo}_cli.csv` | `sma/resultados/` |
| Q-Tables | `qtable_{agente_id}.json` | `sma/qtables/` |

#### Ficheiros Gerados

**Estrutura de saída:**
```
resultados/
  ├── farol_aprendizagem.csv      # Dados brutos (modo manual)
  ├── farol_aprendizagem_cli.csv  # Dados brutos (via CLI)
  └── farol_teste_cli.csv

analise/
  ├── farol_aprendizagem_curva_aprendizagem.png
  ├── farol_aprendizagem_relatorio.txt
  ├── farol_teste_graficos.png    # Gráficos gerados via CLI
  ├── foraging_aprendizagem_graficos.png
  └── comparacao_politicas.png
```

**Formato CSV:**
- Uma linha por episódio
- Colunas: `episodio`, `passos`, `recompensa_total`, `recompensa_descontada`, `sucesso`, `valor_total_depositado`

**Formato PNG:**
- Gráficos de alta resolução (300 DPI)
- Prontos para inclusão em relatórios

**Formato TXT:**
- Relatório textual com estatísticas
- Análise por quartis
- Comparação primeira vs segunda metade

---

## Extensibilidade

### Adicionar Novo Ambiente

1. Criar classe que herda de `Ambiente`
2. Implementar métodos: `observacaoPara()`, `agir()`, `atualizacao()`
3. Adicionar métodos específicos que os sensores podem usar

### Adicionar Novo Sensor

1. Criar classe que herda de `Sensor`
2. Implementar método `ler(ambiente, agente)`
3. Instalar no agente com `agente.instala(Sensor())`

### Adicionar Novo Agente

1. Criar classe que herda de `Agente`
2. Implementar métodos: `cria()`, `age()`
3. Instalar sensores apropriados
4. Definir ações disponíveis

### Adicionar Nova Política

1. Criar classe que herda de `Politica`
2. Implementar `selecionar_acao()`
3. Opcionalmente implementar `atualizar()` para aprendizagem

---

## Comparação de Políticas

### Objetivo

O simulador permite comparar o desempenho entre políticas fixas inteligentes (pré-programadas) e políticas aprendidas (Q-Learning), permitindo avaliar se a aprendizagem melhorou o desempenho do agente.

### Script de Comparação

Foi implementado o script `comparar_politicas.py` que:

1. **Executa com política fixa inteligente:** Cria agentes com `PoliticaFixaInteligente` que usam heurísticas baseadas em observações
2. **Executa com política aprendida:** 
   - Lê quantas Q-tables existem para o ambiente em `sma/qtables/`
   - Limita o número de agentes com Q-Learning ao número de Q-tables disponíveis
   - Agentes restantes usam política fixa inteligente
   - Carrega Q-tables pré-treinadas e executa em modo TESTE (sem exploração, epsilon=0)
3. **Compara resultados:** Mostra diferenças em todas as métricas
4. **Gera gráficos comparativos:** Cria visualizações lado a lado com 6 métricas diferentes

**Gestão de Q-tables:**
- O script verifica automaticamente quantas Q-tables existem para o ambiente selecionado
- Se houver menos Q-tables do que agentes, apenas os primeiros agentes usam Q-Learning
- Mostra avisos quando há menos Q-tables do que agentes solicitados

### Uso

**Via CLI Interativo:**
```bash
./run.sh
# Escolher "Comparar politicas (Fixa Inteligente vs Q-Learning)"
```

**Via Linha de Comando:**
```bash
# Primeiro, treinar a política (modo APRENDIZAGEM)
python -m sma.run farol --episodios 100
# Q-tables são guardadas em sma/qtables/

# Depois, comparar políticas
python -m sma.comparar_politicas config_farol.json --episodios 10
# O script lê quantas Q-tables existem para o ambiente e limita o número de agentes com Q-Learning
```

### Métricas Comparadas

O script compara:
- **Taxa de sucesso:** Percentagem de episódios que terminaram com sucesso
- **Passos médios:** Número médio de ações até terminar
- **Recompensa média:** Recompensa total média por episódio
- **Recompensa descontada:** Recompensa com desconto temporal

### Exemplo de Saída

```
COMPARAÇÃO: POLÍTICA FIXA vs POLÍTICA APRENDIDA
======================================================================
Métrica                         Fixa                 Aprendida         Diferença
-------------------------------------------------------------------------------------
Taxa de Sucesso (%)             0.00                 85.00             +85.00%
Passos Médios                   200.0                45.2              -154.8
Recompensa Média                -200.00               89.50             +289.50
Recompensa Descontada           -198.50               88.20             +286.70
======================================================================

ANÁLISE:
Melhorias com política aprendida:
   - Taxa de sucesso melhorou 85.00%
   - Reduziu passos médios em 154.8
   - Recompensa média aumentou 289.50
```

### Exportação de Resultados

O script exporta automaticamente:
- `resultados_fixa.csv`: Resultados da política fixa inteligente
- `resultados_aprendida.csv`: Resultados da política aprendida (Q-Learning)
- `comparacao_politicas.png`: Gráfico comparativo com 6 subgráficos

### Gráficos Comparativos

O script gera automaticamente um gráfico comparativo mostrando:

1. **Passos médios (barra):** Comparação direta com barras de erro
2. **Evolução dos passos (linha):** Ambas as políticas ao longo dos episódios
3. **Taxa de sucesso (barra):** Comparação percentual
4. **Recompensa média (barra):** Comparação com barras de erro
5. **Evolução da recompensa (linha):** Ambas as políticas ao longo dos episódios
6. **Evolução da recompensa descontada (linha):** Ambas as políticas ao longo dos episódios

Cada gráfico de evolução mostra:
- Valores reais (linhas transparentes)
- Média móvel (linhas destacadas)
- Ambas as políticas no mesmo gráfico para comparação direta

Os ficheiros CSV podem ser usados para análise estatística mais detalhada ou visualização personalizada.

---

## Questões Relevantes a Considerar

Esta secção responde às questões colocadas no enunciado do projeto.

### 1. Como irá modelar a percepção do agente em cada ambiente?

A percepção foi modelada usando um **sistema híbrido de percepção local e global**, implementado através de sensores modulares:

| Ambiente | Percepção Local | Percepção Global |
|----------|-----------------|------------------|
| **Farol** | Vizinhança 8-direccional (vizinhança imediata com tipo de célula: vazio, obstáculo, farol, fora de limites) | Direção normalizada para o farol `(dx, dy)` onde `dx, dy ∈ {-1, 0, 1}` |
| **Foraging** | Vizinhança 8-direccional (vizinhança imediata com tipo de célula: vazio, recurso, ninho, obstáculo, fora de limites) | Direção para o ninho, direção para o recurso mais próximo, distância ao ninho (cap de 10), estado de carga |

**Justificação da Escolha:**
- A percepção **local** permite ao agente evitar obstáculos e reagir ao ambiente imediato, o que é essencial para navegação segura.
- A percepção **global** (direção ao objetivo) permite ao agente orientar-se mesmo sem ter uma visão completa do mapa, simulando um comportamento realista de navegação por compasso ou feromônios.
- Esta combinação é inspirada em sistemas biológicos (ex: formigas usam feromônios locais + orientação solar global).

**Impacto na Aprendizagem:**
- O espaço de estados é finito e relativamente pequeno (produto cartesiano de direções e vizinhança discreta), tornando o Q-Learning convergente.
- A representação como string (`repr(obs.dados)`) permite usar qualquer estrutura de dados complexa como chave na Q-table.

---

### 2. Quais são as métricas de desempenho mais relevantes para cada problema?

| Métrica | Farol | Foraging | Justificação |
|---------|-------|----------|--------------|
| **Taxa de Sucesso** | Principal | Relevante | Indica se o agente consegue atingir o objetivo (farol ou depositar todos os recursos). |
| **Passos Médios** | Principal | Secundária | No Farol, menos passos = mais eficiente. No Foraging, o número de passos é menos importante se o agente recolher mais recursos. |
| **Recompensa Total** | Secundária | Principal | No Foraging, a recompensa reflete o valor total depositado. No Farol, é derivada dos passos. |
| **Recompensa Descontada (γ=0.99)** | Relevante | Relevante | Penaliza soluções lentas, incentivando eficiência temporal. Importante para comparar políticas. |

**Farol:**
- Objetivo claro e único (chegar ao farol), portanto a **taxa de sucesso** e **passos médios** são as métricas primárias.
- Faz sentido usar um fator de desconto (γ) alto (0.95-0.99) para incentivar caminhos curtos.

**Foraging:**
- Múltiplos sub-objetivos (coletar, transportar, depositar), portanto a **recompensa total** (que soma todos os valores depositados) é a métrica primária.
- O número de passos é menos crítico, mas a recompensa descontada ainda ajuda a evitar comportamentos desnecessariamente lentos.

---

### 3. Será que os algoritmos usados reagem do mesmo modo a diferentes métricas?

**Não, os algoritmos reagem de forma diferente às métricas, e esta diferença é fundamental para a escolha do algoritmo adequado:**

| Algoritmo | Sensibilidade a Passos | Sensibilidade a Recompensa | Observações |
|-----------|------------------------|---------------------------|-------------|
| **Q-Learning** | Alta (via recompensa negativa por passo) | Alta (atualização direta do Q-value) | Muito sensível ao *shaping* da função de recompensa. Se a recompensa por passo for muito negativa, o agente pode preferir "morrer cedo" a explorar. |
| **Algoritmo Genético** | Baixa (só vê fitness no fim) | Alta (fitness = recompensa total) | Não vê recompensas intermédias, apenas o resultado final. Funciona melhor em problemas episódicos com fitness bem definido. |
| **Política Fixa** | Nenhuma | Nenhuma | Não aprende. O desempenho depende inteiramente da qualidade da heurística programada. |

**Experimentos Realizados:**

1.  **Farol com Recompensa Esparsa (só +99 ao chegar):**
    - Q-Learning demora muito a convergir porque a recompensa positiva é rara.
    - Algoritmo Genético funciona bem porque a fitness (chegou ou não) é clara.

2.  **Farol com Reward Shaping (penalidade por passo + bónus por aproximação):**
    - Q-Learning converge rapidamente porque recebe feedback contínuo.
    - Algoritmo Genético não beneficia tanto porque não vê as recompensas intermédias.

3.  **Foraging com Múltiplos Recursos:**
    - Q-Learning aprende a priorizar recursos de maior valor (se a recompensa refletir o valor).
    - Algoritmo Genético otimiza a recompensa total, mas pode demorar mais a encontrar estratégias sofisticadas.

**Conclusão:**
A escolha do algoritmo deve considerar:
- **Q-Learning** é melhor quando a função de recompensa pode ser bem moldada (*reward shaping*) e o espaço de estados é discreto e gerenciável.
- **Algoritmos Genéticos** são melhores quando a fitness é fácil de calcular no fim do episódio, mas o caminho até lá é complexo ou o espaço de estados é muito grande/contínuo.

---

## Conclusão

O simulador implementa uma arquitetura modular e extensível que cumpre todos os requisitos do enunciado:

| Requisito do Enunciado | Estado | Implementação |
|------------------------|--------|---------------|
| Interface `MotorDeSimulacao` | ✅ | `MotorDeSimulacao` em `simulador.py` com `cria()`, `listaAgentes()`, `executa()` |
| Interface `Ambiente` | ✅ | `Ambiente` base com `observacaoPara()`, `agir()`, `atualizacao()` |
| Interface `Agente` | ✅ | `Agente` como thread com `cria()`, `age()`, `observacao()`, `avaliacaoEstadoAtual()`, `instala()`, `comunica()` |
| Problema Farol | ✅ | `AmbienteFarol` + `AgenteFarol` com obstáculos e direção ao farol |
| Problema Foraging | ✅ | `AmbienteForaging` + `AgenteForager` com recursos, ninho e carga |
| Modo APRENDIZAGEM | ✅ | Q-Learning e Algoritmo Genético com registo de métricas |
| Modo TESTE | ✅ | Avaliação com política fixa (epsilon=0) e carregamento de Q-tables |
| Threads sincronizadas | ✅ | Agentes como `threading.Thread` com `threading.Barrier` |
| Visualização | ✅ | `Visualizador` com Tkinter mostrando ambiente, agentes e objetivos |
| CLI Interativo | ✅ | `cli.py` com questionário guiado e geração automática de gráficos |
| Comparação de Políticas | ✅ | `comparar_politicas.py` com gráficos lado a lado |
| Comunicação entre Agentes | ✅ | `enviar_mensagem()` e `broadcast_mensagem()` com fila de mensagens |

A implementação permite que diferentes grupos possam usar ambientes e agentes uns dos outros sem modificações, cumprindo o objetivo de modularidade especificado no enunciado.

**Repositório GitHub:** [Link para o repositório]

