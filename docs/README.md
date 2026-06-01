# Infraestrutura e Vendas de Veículos Elétricos - Brasil

## Sobre o Projeto

Análise estratégica da correlação entre o crescimento explosivo das vendas de veículos elétricos e a expansão da infraestrutura de recarga no Brasil. Utilizando técnicas de Data Science e Machine Learning para identificar oportunidades de mercado e otimizar investimentos em infraestrutura.

### Problema de Negócio
- **Desafio:** Crescimento desigual entre vendas de VE e infraestrutura
- **Oportunidade:** Identificar lacunas de mercado para expansão inteligente
- **Solução:** Modelo preditivo para otimização de novos postos

## Estrutura do Dataset

### Arquivos Principais:

| Arquivo                            | Descrição |
|------------------------------------|-----------|
| `carros_eletricos.csv`             | Frota de Veículos Elétricos em circulação |
| `charging_stations_2025_world.csv` | Postos de recarga global |
| `monitoramento_vendas.csv`         | Evolução temporal de vendas no Brasil|
| `webscraping.py`                   | Script de coleta de dados |

### Variáveis Principais:
- **Localização** (lat/long, estados, cidades)
- **Vendas** (mensal, anual, por fabricante)
- **Infraestrutura** (tipos de conectores, potência, disponibilidade)
- **Características** de veículos (autonomia, preço, categoria)

## Notebooks de Análise

### 1. `analise_exploratoria.ipynb` - Análise Exploratória
**Objetivo:** Entender o panorama atual do mercado
- Estatísticas descritivas
- Visualizações geográficas
- Correlação vendas vs infraestrutura
- Identificação de "desertos de recarga"

### 2. `vendas_veiculos_eletricos.ipynb` - Tendências de Mercado
**Objetivo:** Analisar evolução e projeções
- Série temporal de vendas
- Growth analysis
- Market share por fabricante
- Análise sazonal

### 3. `clusterizacao_kmeans.ipynb` - Machine Learning
**Objetivo:** Otimizar expansão da infraestrutura
- Clusterização com K-means
- Identificação de regiões prioritárias
- Recomendações estratégicas
- Mapa de calor de demanda

## Principais Insights

### Descobertas Críticas:
1. **Crescimento Explosivo:** Vendas aumentaram 89% em relação 2023 para 2024
2. **Concentração Geográfica:** 52,19% dos postos de recarga estão nos 10 estados com maior número de estações
3. **Lacuna de Infraestrutura:** Para cada 758 carros, há apenas 1 posto de recarga no Brasil
4. **Oportunidades:** 10 regiões identificadas como prioritárias

### Clusters Identificados:
- **Cluster 1:** Regiões metropolitanas (alta densidade)
- **Cluster 2:** Corredores rodoviários (conectividade)
- **Cluster 3:** Cidades emergentes (crescimento potencial)
