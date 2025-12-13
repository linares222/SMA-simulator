# Guia: Análise de Resultados

Este guia explica como gerar curvas de aprendizagem e análises de resultados automaticamente.

## Funcionalidades

### 1. Exportação Automática de Dados

Após cada execução, os dados podem ser exportados automaticamente para CSV:

```bash
# Exportar automaticamente após execução
python -m sma.run farol --auto-export

# Ou especificar ficheiro de saída
python -m sma.run farol --episodios 100 --output resultados_farol.csv
```

Os ficheiros CSV contêm:
- `episodio`: Número do episódio
- `passos`: Número de passos até terminar
- `recompensa_total`: Recompensa total do episódio
- `recompensa_descontada`: Recompensa com desconto temporal
- `sucesso`: True/False se o episódio terminou com sucesso
- `valor_total_depositado`: Valor total depositado (apenas Foraging)

### 2. Geração Automática de Análise

Para gerar automaticamente gráficos e relatórios após a execução:

```bash
# Treinar e gerar análise automaticamente
python -m sma.run farol --episodios 100 --gerar-analise
```

Isto irá:
1. Executar a simulação
2. Exportar CSV automaticamente
3. Gerar gráficos da curva de aprendizagem
4. Gerar relatório textual com estatísticas

### 3. Análise Manual de Dados Existentes

Se já tens ficheiros CSV, podes gerar análise a partir deles:

```bash
# Gerar curva de aprendizagem
python -m sma.gerar_analise resultados_farol.csv --nome farol_aprendizagem

# Comparar duas políticas
python -m sma.gerar_analise resultados_fixa.csv --comparar resultados_aprendida.csv --nome comparacao
```

## Ficheiros Gerados

### Curva de Aprendizagem (`*_curva_aprendizagem.png`)

Gráfico com 4 painéis:
1. **Passos por Episódio**: Evolução do número de passos (com média móvel)
2. **Recompensa por Episódio**: Evolução da recompensa (com média móvel)
3. **Taxa de Sucesso**: Evolução da taxa de sucesso ao longo do tempo
4. **Estatísticas**: Comparação primeira vs segunda metade dos episódios

### Comparação de Políticas (`comparacao_politicas.png`)

Gráfico comparativo com 4 painéis:
1. **Passos Médios**: Comparação entre políticas
2. **Recompensa Média**: Comparação entre políticas
3. **Taxa de Sucesso**: Comparação entre políticas
4. **Evolução da Recompensa**: Curvas sobrepostas

### Relatório Textual (`*_relatorio.txt`)

Relatório com:
- Estatísticas gerais (média, desvio padrão, min, max)
- Análise por quartis (evolução ao longo do tempo)
- Comparação primeira vs segunda metade

## Exemplos de Uso

### 1. Treinar e Analisar (Modo Aprendizagem)

```bash
# Treinar agente
python -m sma.run farol --episodios 100 --gerar-analise

# Resultados em:
# - resultados/farol_aprendizagem.csv
# - analise/farol_aprendizagem_curva_aprendizagem.png
# - analise/farol_aprendizagem_relatorio.txt
```

### 2. Testar Política Treinada (Modo Teste)

```bash
# Testar política treinada
python -m sma.run farol --episodios 10 --gerar-analise

# Resultados em:
# - resultados/farol_teste.csv
# - analise/farol_teste_curva_aprendizagem.png
# - analise/farol_teste_relatorio.txt
```

### 3. Comparar Políticas

```bash
# 1. Executar com política fixa
python -m sma.comparar_politicas sma/config_farol.json --episodios 10

# 2. Gerar análise comparativa
python -m sma.gerar_analise resultados_fixa.csv --comparar resultados_aprendida.csv --nome farol_comparacao
```

## Estrutura de Diretórios

```
AA-Projeto/
├── sma/
│   ├── resultados/          # CSVs exportados automaticamente
│   │   ├── farol_aprendizagem.csv
│   │   └── farol_teste.csv
│   └── analise/             # Gráficos e relatórios
│       ├── farol_aprendizagem_curva_aprendizagem.png
│       ├── farol_aprendizagem_relatorio.txt
│       └── comparacao_politicas.png
```

## Métricas Analisadas

### Curva de Aprendizagem
- **Passos**: Deve diminuir ao longo do tempo (agente aprende a ser mais eficiente)
- **Recompensa**: Deve aumentar ao longo do tempo (agente aprende a maximizar recompensa)
- **Taxa de Sucesso**: Deve aumentar ao longo do tempo (agente aprende a completar tarefas)

### Modo Teste
- **Taxa de Sucesso**: Percentagem de episódios bem-sucedidos
- **Passos Médios**: Eficiência da política
- **Recompensa Média**: Desempenho geral
- **Desvio Padrão**: Consistência da política

## Dicas

1. **Para análise de aprendizagem**: Use muitos episódios (100+)
2. **Para análise de teste**: Use menos episódios (10-20) mas múltiplas execuções
3. **Média móvel**: Suaviza a curva para ver tendências (janela de 10 episódios)
4. **Comparação**: Sempre compare primeira vs segunda metade para ver se há melhoria

## Requisitos

```bash
pip install matplotlib numpy
```

Ou use o `requirements.txt`:
```bash
pip install -r requirements.txt
```

