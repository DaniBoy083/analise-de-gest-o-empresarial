# Gestao Financeira Empresarial

Projeto academico para analise estrategica do mercado de veiculos eletricos no Brasil, com foco em decisao de investimento para novos pontos de recarga.

## Informacoes academicas

### Materia
Topicos avancados em computacao.

### Tema
Gestao financeira empresarial.

### Professor
Daniel Brandao.

### Integrantes
- Alawander Fernandes da Silva
- Daniel Costa Carvalho Martins
- Thais Rainara Marques de Morais
- Matheus Mendes
- Eduardo Lins

### Data de entrega
15 de junho de 2026.

### Cliente
Vapt.

### Objetivo de negocio
Descobrir a regiao mais atrativa para investir em novos postos de carregamento de carros eletricos no Brasil.

### Publico-alvo
Direcao financeira da empresa.

## Visao geral da solucao

Ao executar a pipeline, o projeto:
- baixa/atualiza os dados (quando disponivel via KaggleHub);
- faz fallback para arquivos locais quando necessario;
- processa dados de frota, vendas e infraestrutura;
- gera relatorio HTML com dashboard interativo;
- empacota os dados consumidos para auditoria/reprodutibilidade;
- aplica favicon a partir de `public/assets/`.

## Explicacao para o exercicio (1 envio por grupo)

### 1) Origem dos dados (dataset)
- Fonte principal no Kaggle: `nathanrocha/recarga-de-veculos-eltricos-brasil`.
- Arquivos analisados:
	- `carros_eletricos.csv` (frota/modelos/fabricantes);
	- `monitoramento_vendas.csv` (historico de vendas);
	- `charging_stations_2025_world.csv` (infraestrutura de recarga, com filtro para Brasil).
- Estrategia de confiabilidade: quando o download do Kaggle nao estiver disponivel, a pipeline usa os CSVs locais em `docs/` para garantir execucao.

### 2) Validacao da proposta
- Problema de negocio validado: apoiar decisao de investimento em novos pontos de recarga com base em dados reais de mercado e infraestrutura.
- Hipotese central: estados com melhor combinacao de demanda (vendas/frota) e maturidade de infraestrutura tendem a gerar menor risco de investimento.
- Indicadores usados na validacao:
	- crescimento anual (YoY) e CAGR das vendas;
	- concentracao de market share por fabricante/modelo;
	- quantidade de estacoes por estado, taxa de recarga rapida e potencia media.

### 3) Estudo de viabilidade
- Viabilidade tecnica: alta.
	- Pipeline automatizada em Python (pandas) com entrada, analise e geracao web desacopladas.
	- Testes unitarios cobrindo camadas principais.
	- CI no GitHub Actions para prevenir regressao.
- Viabilidade de dados: alta.
	- Ha granularidade suficiente para comparar estados e inferir oportunidade de expansao.
	- Limitacoes conhecidas (como lacunas de origem externa) sao tratadas com normalizacao e fallback.
- Viabilidade operacional: alta.
	- Entrega final e estatico (HTML/CSS/JS), simples de publicar e manter.

### 4) Ideias iniciais da entrega
- Formato escolhido: dashboard interativo (relatorio executivo + visualizacoes).
- Visuais previstos e implementados:
	- market share por fabricante;
	- vendas anuais e variacao YoY;
	- distribuicao mensal de vendas;
	- ranking de estados por score de atratividade.
- Itens de entrega:
	- relatorio web responsivo com identidade visual preto/verde;
	- download do dataset consumido (`dataset_consumido.zip`);
	- link para o Kaggle (origem dos dados);
	- execucao automatizada da pipeline (sem processo manual de montagem de relatorio).

## Stack tecnica

- Python 3.12
- pandas
- kagglehub
- kagglesdk (versao fixada para compatibilidade)
- HTML/CSS/TypeScript (arquivo JS gerado para execucao direta)
- Chart.js local (sem dependencia de CDN em runtime)
- unittest (testes automatizados)
- GitHub Actions (CI)
- Netlify (hospedagem)

## Arquitetura (clean code)

A arquitetura foi separada por responsabilidade para reduzir acoplamento:

- `main.py`: entrypoint CLI, sem regra de negocio.
- `ev_pipeline/pipeline.py`: orquestracao de ponta a ponta.
- `ev_pipeline/data_sources.py`: acesso a dados e assets (download, resolucao de arquivos, favicon, bundle zip).
- `ev_pipeline/analysis.py`: transformacoes e metricas de negocio.
- `ev_pipeline/states.py`: normalizacao de estados.
- `ev_pipeline/site_builder.py`: geracao de artefatos web.
- `web_src/`: fonte dos assets web (template, estilo, dashboard e Chart.js local).
- `tests/`: suite de testes unitarios por camada.

## Estrutura de pastas

```text
analise-de-gestao-empresarial/
|- .github/
|  |- workflows/
|     |- ci.yml
|- docs/
|  |- site/                       # saida gerada da pipeline
|- ev_pipeline/
|  |- analysis.py
|  |- config.py
|  |- data_sources.py
|  |- pipeline.py
|  |- site_builder.py
|  |- states.py
|- public/
|  |- assets/                     # origem oficial do favicon
|- tests/
|  |- test_analysis.py
|  |- test_data_sources.py
|  |- test_pipeline.py
|  |- test_site_builder.py
|  |- test_states.py
|- web_src/
|  |- index.template.html
|  |- styles.css
|  |- dashboard.ts
|  |- chart.umd.min.js
|- main.py
|- netlify.toml
|- requirements.txt
|- README.md
```

## Requisitos

- Python 3.12+
- Ambiente com acesso a internet para download inicial de dependencias

## Instalacao (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Execucao da pipeline

```powershell
.\.venv\Scripts\python.exe main.py
```

Opcional (diretorio customizado de saida):

```powershell
.\.venv\Scripts\python.exe main.py --output-dir docs/site
```

## Execucao dos testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Integracao continua (CI)

Workflow configurado em `.github/workflows/ci.yml` com os passos:
- checkout do repositorio;
- setup de Python 3.12;
- instalacao de dependencias (`requirements.txt`);
- execucao automatica dos testes (`unittest discover`).

## Hospedagem na Netlify (configurada)

O projeto ja esta preparado para deploy automatico na Netlify com o arquivo `netlify.toml`:

- Build command:
	- `python -m pip install --upgrade pip && python -m pip install -r requirements.txt && python main.py --output-dir docs/site`
- Publish directory:
	- `docs/site`
- Versao de Python no build:
	- `3.12`

### Passo a passo na Netlify

1. Criar site em **Add new site > Import an existing project**.
2. Conectar este repositorio GitHub.
3. Confirmar que a Netlify detectou o `netlify.toml` automaticamente.
4. Acionar o deploy.
5. Validar o carregamento de `index.html`, graficos e arquivo de download do dataset.

## Artefatos gerados

A pipeline escreve os arquivos em `docs/site/`:
- `index.html` (relatorio + dashboard)
- `styles.css`
- `dashboard.ts`
- `dashboard.js`
- `analysis.json`
- `dataset_consumido.zip`
- `favicon.png`
- `chart.umd.min.js`

## Dashboard e performance

- O conteudo textual (resumo, KPIs e tabelas) renderiza imediatamente.
- Graficos hidratam de forma assincrona.
- Chart.js e servido localmente (`chart.umd.min.js`), evitando lentidao por CDN.
- Layout responsivo para desktop, tablet e mobile.

## Favicon

- Origem oficial: `public/assets/`.
- A pipeline localiza uma imagem valida e copia para `docs/site/favicon.png`.

## Dados e fallback

- Dataset principal: `nathanrocha/recarga-de-veculos-eltricos-brasil`.
- Em falha de download, a pipeline utiliza arquivos locais (`docs/*.csv`) quando disponiveis.

## Troubleshooting

### ImportError entre kagglehub e kagglesdk

O projeto usa versoes fixadas em `requirements.txt` para evitar incompatibilidade.

### Graficos nao aparecem

Verifique se `web_src/chart.umd.min.js` existe antes de executar a pipeline.

### Favicon nao atualizado

Confirme que existe ao menos uma imagem em `public/assets/` e execute novamente `main.py`.

## Observacoes de manutencao

- Alteracoes visuais devem ser feitas em `web_src/styles.css`.
- Alteracoes do dashboard devem ser feitas em `web_src/dashboard.ts`.
- O diretorio `docs/site/` e artefato gerado; nao e fonte da aplicacao.

