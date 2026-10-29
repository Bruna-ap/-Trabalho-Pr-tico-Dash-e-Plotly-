# Dashboard de Medalhas Olímpicas — Dash e Plotly

Trabalho prático da disciplina de Visualização de Dados. Dashboard feito com Python, Pandas, Dash e Plotly Express, a partir da base `Country_Medals.csv` fornecida junto ao material da atividade.

## Funcionalidades

- Mapa coroplético com totais de medalhas por país entre 1992 e 2020.
- Gráfico de área com os dez países com mais medalhas ao longo das edições olímpicas.
- Gráfico de barras com os dez países com mais medalhas na edição selecionada (ano, cidade e país sede).
- Gráfico de pizza com Ouro, Prata e Bronze acumulados para o país selecionado.
- Filtro global por tipo de medalha (Todas, Ouro, Prata ou Bronze) aplicado aos três gráficos originais: mapa, área e barras.
- Layout responsivo e cores inspiradas nas medalhas olímpicas.

## Requisitos

Python 3.10 ou superior recomendado.

## Executar localmente no Windows (VS Code)

Abra o terminal do VS Code nesta pasta e execute:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Abra o endereço indicado no terminal, normalmente `http://127.0.0.1:8050`.

## Publicar no Render

Crie um **Web Service** conectado a este repositório do GitHub e configure:

- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:server`

Inclua `Country_Medals.csv` na raiz do repositório. Após o deploy, substitua a linha abaixo pelo link público real do serviço Render e informe-o no SIGAA.

**Dashboard publicado no Render:** preencher após a implantação.

## Base de dados

`Country_Medals.csv` foi extraído do arquivo `Summer_olympic_Medals.csv` fornecido nos materiais da disciplina e contém os campos Year, Host_country, Host_city, Country_Name, Country_Code, Gold, Silver e Bronze.
