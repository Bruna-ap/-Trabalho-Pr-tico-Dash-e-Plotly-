"""Dashboard de Medalhas Olímpicas — trabalho prático de Visualização de Dados."""
# Usado para ler variáveis de ambiente, como a porta definida pelo Render.
import os
# Ajuda a montar os caminhos dos arquivos do projeto.
from pathlib import Path

# Pandas lê e organiza os dados da base CSV.
import pandas as pd
# Plotly Express é usado para criar os gráficos.
import plotly.express as px
# Dash monta a página e conecta os filtros às atualizações dos gráficos.
from dash import Dash, Input, Output, dcc, html

# Localiza a pasta em que este arquivo app.py está salvo.
BASE_DIR = Path(__file__).resolve().parent
# Define o caminho da base de medalhas, que fica na mesma pasta do app.py.
CSV_PATH = BASE_DIR / "Country_Medals.csv"
# Nomes das colunas usadas para as medalhas de ouro, prata e bronze.
MEDALS = ["Gold", "Silver", "Bronze"]
# Relaciona os nomes das medalhas na base aos rótulos que aparecem na tela.
MEDAL_LABELS = {"Gold": "Ouro", "Silver": "Prata", "Bronze": "Bronze"}
# Define as cores usadas para diferenciar as medalhas no gráfico de pizza.
MEDAL_COLORS = {"Ouro": "#E9B949", "Prata": "#C5D0D8", "Bronze": "#CD8A5A"}
# Agrupa as cores usadas no fundo, nos cartões, nos textos e nos gráficos.
COLORS = {
    "background": "#101820",
    "panel": "#1B2833",
    "text": "#F4F7F8",
    "muted": "#B8C5CC",
    "gold": "#E9B949",
    "grid": "#354652",
}


# Função que carrega e prepara os dados antes da montagem dos gráficos.
def load_data():
    """Load and prepare the Olympic medal dataset provided with the assignment."""
    # Verifica se o arquivo CSV está na pasta esperada; se não estiver, informa o erro.
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            "Arquivo Country_Medals.csv não encontrado. Coloque o CSV na mesma pasta de app.py."
        )

    # Lê o CSV e armazena os registros em um DataFrame do Pandas.
    data = pd.read_csv(CSV_PATH)
    # Remove espaços extras dos nomes das colunas.
    data.columns = [str(column).strip() for column in data.columns]
    # Define as colunas obrigatórias para o dashboard funcionar.
    required = ["Year", "Host_country", "Host_city", "Country_Name", *MEDALS]
    # Procura colunas obrigatórias que estejam faltando na base.
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError("Colunas ausentes na base Country_Medals.csv: " + ", ".join(missing))

    # Converte os anos para valores numéricos; valores inválidos são tratados como ausentes.
    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    # Converte as quantidades de medalhas para números e substitui valores inválidos por zero.
    for medal in MEDALS:
        data[medal] = pd.to_numeric(data[medal], errors="coerce").fillna(0)
    # Padroniza os campos de texto, removendo espaços no começo e no fim.
    for column in ["Host_country", "Host_city", "Country_Name"]:
        data[column] = data[column].astype("string").str.strip()
    # Remove linhas sem ano, país participante ou país sede.
    data = data.dropna(subset=["Year", "Country_Name", "Host_country"]).copy()
    # Mantém apenas as edições do período de 1992 a 2020, conforme o tutorial.
    data = data[data["Year"].between(1992, 2020)].copy()
    # Armazena o ano como número inteiro.
    data["Year"] = data["Year"].astype(int)
    # Match the country label used in the tutorial and in Plotly's country map.
    data["Country_Name"] = data["Country_Name"].replace(
        {"United States": "United States of America"}
    )
    # Calcula o total de medalhas de cada linha somando ouro, prata e bronze.
    data["Total_Medals"] = data[MEDALS].sum(axis=1)
    return data


# Carrega a base de dados quando a aplicação é iniciada.
df = load_data()
# Cria a aplicação Dash e define o título exibido no navegador.
app = Dash(__name__, title="Quadro de Medalhas Olímpicas")
# Disponibiliza o servidor da aplicação para o Gunicorn no Render.
server = app.server  # Render/Gunicorn entry point


# Função auxiliar para montar cartões com o mesmo estilo visual.
def panel(children, extra_style=None):
    style = {
        "backgroundColor": COLORS["panel"],
        "borderRadius": "15px",
        "padding": "16px",
        "boxShadow": "0 6px 24px rgba(0, 0, 0, .16)",
        "minWidth": "0",
    }
    # Permite acrescentar ou substituir estilos de um cartão específico.
    if extra_style:
        style.update(extra_style)
    return html.Div(children, style=style)


# Padroniza as cores, a fonte, as margens, a legenda e a altura dos gráficos.
def style_figure(fig, height=370):
    fig.update_layout(
        paper_bgcolor=COLORS["panel"],
        plot_bgcolor=COLORS["panel"],
        font={"color": COLORS["text"], "family": "Arial, sans-serif"},
        title={"x": 0.025, "xanchor": "left", "font": {"size": 17}},
        height=height,
        margin={"l": 24, "r": 24, "t": 65, "b": 35},
        legend={"orientation": "h", "y": 1.12, "x": 0, "font": {"size": 10}},
    )
    fig.update_xaxes(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"])
    fig.update_yaxes(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"])
    return fig


# Cria uma lista de países sem valores vazios e sem duplicatas para o filtro da pizza.
countries = sorted(df["Country_Name"].dropna().unique().tolist())
# Use a combined Year + host label so the selection is clear to the user.
# Monta a lista de edições olímpicas, com o ano, a cidade sede e o país sede.
editions = (
    df[["Year", "Host_country", "Host_city"]]
    .drop_duplicates()
    .sort_values("Year")
)
# Transforma cada edição em uma opção do menu suspenso.
edition_options = [
    {
        "label": f'{int(row.Year)} — {row.Host_city}, {row.Host_country}',
        "value": int(row.Year),
    }
    for row in editions.itertuples(index=False)
]

# Define a estrutura e o conteúdo visual do dashboard.
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    "VISUALIZAÇÃO DE DADOS  •  JOGOS DE VERÃO  •  1992–2020",
                    style={"color": COLORS["gold"], "fontSize": "11px", "fontWeight": "bold", "letterSpacing": "2px"},
                ),
                html.H1(
                    "Quadro de Medalhas Olímpicas",
                    style={"fontSize": "clamp(27px, 4vw, 42px)", "margin": "9px 0", "fontWeight": "750"},
                ),
                html.P(
                    "Compare o desempenho dos países e explore os resultados por edição olímpica.",
                    style={"color": COLORS["muted"], "marginTop": "0", "fontSize": "15px"},
                ),
            ],
            style={"padding": "30px 4px 14px"},
        ),
        panel(
            [
                # Texto que identifica o filtro global de medalhas.
                html.Label("Filtro global — tipo de medalha", style={"fontWeight": "bold"}),
                # Exibe as opções Todas, Ouro, Prata e Bronze para o filtro global.
                dcc.RadioItems(
                    id="medal-filter",
                    options=[
                        {"label": "Todas", "value": "Todos"},
                        {"label": "Ouro", "value": "Gold"},
                        {"label": "Prata", "value": "Silver"},
                        {"label": "Bronze", "value": "Bronze"},
                    ],
                    value="Todos",
                    inline=True,
                    labelStyle={"display": "inline-block", "margin": "12px 22px 8px 0", "cursor": "pointer"},
                    inputStyle={"marginRight": "8px", "accentColor": COLORS["gold"]},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("País para o gráfico de pizza"),
                                # Primeiro menu suspenso: permite selecionar o país do gráfico de pizza.
                                dcc.Dropdown(
                                    id="country-filter",
                                    options=[{"label": country, "value": country} for country in countries],
                                    value="Brazil" if "Brazil" in countries else countries[0],
                                    clearable=False,
                                ),
                            ],
                            style={"flex": "1 1 250px", "minWidth": "220px"},
                        ),
                        html.Div(
                            [
                                # Identifica o filtro de edição olímpica usado no gráfico de barras.
                                html.Label("Ano olímpico (cidade e país sede) — gráfico de barras"),
                                # Segundo menu suspenso: seleciona o ano e mostra a cidade e o país sede.
                                dcc.Dropdown(
                                    id="edition-filter",
                                    options=edition_options,
                                    value=2020 if 2020 in editions["Year"].values else int(editions.iloc[-1]["Year"]),
                                    clearable=False,
                                ),
                            ],
                            style={"flex": "2 1 360px", "minWidth": "250px"},
                        ),
                    ],
                    style={"display": "flex", "flexWrap": "wrap", "gap": "18px", "marginTop": "14px"},
                ),
            ],
            {"marginBottom": "18px"},
        ),
        # Reserva o espaço do mapa mundial.
        panel(dcc.Graph(id="world-map", config={"displayModeBar": False}), {"marginBottom": "18px"}),
        html.Div(
            [
                # Reserva o espaço do gráfico de área empilhada.
                panel(dcc.Graph(id="area-chart", config={"displayModeBar": False})),
                # Reserva o espaço do gráfico de barras.
                panel(dcc.Graph(id="bar-chart", config={"displayModeBar": False})),
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 410px), 1fr))", "gap": "18px"},
        ),
        panel(
            [
                html.H3("Distribuição de medalhas por país", style={"margin": "2px 0 0"}),
                html.P(
                    "O gráfico de pizza mostra ouro, prata e bronze acumulados entre 1992 e 2020 para o país selecionado.",
                    style={"color": COLORS["muted"], "marginTop": "7px"},
                ),
                # Reserva o espaço do gráfico de pizza.
                dcc.Graph(id="pie-chart", config={"displayModeBar": False}),
            ],
            {"marginTop": "18px"},
        ),
        html.Footer(
            "Fonte: Summer Olympic Medals — base fornecida no material da disciplina. Trabalho prático de Dash e Plotly.",
            style={"color": COLORS["muted"], "fontSize": "12px", "padding": "22px 4px 30px"},
        ),
    ],
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": COLORS["background"],
        "color": COLORS["text"],
        "minHeight": "100vh",
        "padding": "0 4%",
    },
)


# Liga os valores dos filtros às figuras que precisam ser atualizadas.
@app.callback(
    Output("world-map", "figure"),
    Output("area-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("pie-chart", "figure"),
    # O callback recebe o tipo de medalha escolhido pelo usuário.
    Input("medal-filter", "value"),
    # O callback recebe o país escolhido para o gráfico de pizza.
    Input("country-filter", "value"),
    # O callback recebe a edição olímpica escolhida para o gráfico de barras.
    Input("edition-filter", "value"),
)
# Função que recalcula as figuras quando um dos filtros muda.
def update_dashboard(medal_filter, selected_country, selected_year):
    """Update the three original charts from the global medal filter and the pie by country."""
    # Usa uma cópia da base para os cálculos, sem alterar o DataFrame original.
    data = df.copy()
    # Se a opção for Todas, soma as três medalhas; caso contrário, usa apenas a categoria selecionada.
    if medal_filter == "Todos":
        data["Selected_Medals"] = data[MEDALS].sum(axis=1)
        medal_title = "total de medalhas"
    else:
        data["Selected_Medals"] = data[medal_filter]
        medal_title = f"medalhas de {MEDAL_LABELS[medal_filter].lower()}"

    # 1) Choropleth map: cumulative selected medal category from 1992 to 2020.
    # Agrupa por país e soma as medalhas selecionadas para calcular os totais do mapa.
    country_totals = data.groupby("Country_Name", as_index=False)["Selected_Medals"].sum()
    # Gráfico 1: cria o mapa coroplético, usando a cor para representar o total de medalhas.
    map_fig = px.choropleth(
        country_totals,
        locations="Country_Name",
        locationmode="country names",
        color="Selected_Medals",
        hover_name="Country_Name",
        hover_data={"Selected_Medals": ":,.0f"},
        color_continuous_scale="YlOrRd",
        title=f"Mapa mundial — {medal_title} (1992–2020)",
        labels={"Selected_Medals": "Medalhas"},
    )
    style_figure(map_fig, 470)
    # Ajusta o fundo do mapa e remove a moldura e as linhas costeiras.
    map_fig.update_geos(bgcolor=COLORS["panel"], showframe=False, showcoastlines=False)

    # 2) Stacked area chart: the ten countries with the largest totals under the filter.
    # Seleciona os dez países com maior total para o gráfico de área.
    top_countries = country_totals.nlargest(10, "Selected_Medals")["Country_Name"].tolist()
    # Agrupa os dados desses países por ano e país para mostrar a evolução das medalhas.
    area_data = data[data["Country_Name"].isin(top_countries)].groupby(
        ["Year", "Country_Name"], as_index=False
    )["Selected_Medals"].sum()
    # Gráfico 2: cria o gráfico de área para comparar os dez países ao longo dos anos.
    area_fig = px.area(
        area_data,
        x="Year",
        y="Selected_Medals",
        color="Country_Name",
        title=f"Evolução das medalhas — Top 10 países ({medal_title})",
        labels={"Year": "Ano olímpico", "Selected_Medals": "Medalhas", "Country_Name": "País"},
    )
    style_figure(area_fig, 390)

    # 3) Bar chart: filter to the selected Olympic year/host edition.
    # Gráfico 3: considera apenas o ano selecionado e soma as medalhas por país.
    bar_data = data[data["Year"] == int(selected_year)].groupby(
        "Country_Name", as_index=False
    )["Selected_Medals"].sum().nlargest(10, "Selected_Medals").sort_values("Selected_Medals")
    # Busca a cidade e o país sede da edição para incluir essas informações no título.
    edition = editions[editions["Year"] == int(selected_year)].iloc[0]
    # Cria as barras horizontais para mostrar os dez maiores resultados da edição escolhida.
    bar_fig = px.bar(
        bar_data,
        x="Selected_Medals",
        y="Country_Name",
        orientation="h",
        title=f'Top 10 países — {int(selected_year)} ({edition["Host_city"]}, {edition["Host_country"]})',
        labels={"Selected_Medals": "Medalhas", "Country_Name": "País"},
        color_discrete_sequence=[COLORS["gold"] if medal_filter in ("Todos", "Gold") else {"Silver": MEDAL_COLORS["Prata"], "Bronze": MEDAL_COLORS["Bronze"]}[medal_filter]],
    )
    style_figure(bar_fig, 390)

    # 4) Pie chart: always show all three medal types for the chosen country.
    # The brief says the global medal filter applies to the three original charts.
    # Gráfico 4: soma ouro, prata e bronze do país escolhido; a pizza mostra as três categorias.
    pie_totals = df[df["Country_Name"] == selected_country][MEDALS].sum()
    # Organiza os três totais em uma tabela que será usada para montar a pizza.
    pie_data = pd.DataFrame(
        {
            "Medalha": ["Ouro", "Prata", "Bronze"],
            "Quantidade": [pie_totals["Gold"], pie_totals["Silver"], pie_totals["Bronze"]],
        }
    )
    # Cria o gráfico de pizza e define uma cor para cada tipo de medalha.
    pie_fig = px.pie(
        pie_data,
        names="Medalha",
        values="Quantidade",
        title=f"Medalhas de {selected_country} (1992–2020)",
        color="Medalha",
        color_discrete_map=MEDAL_COLORS,
        hole=0.38,
    )
    # Exibe o nome e a porcentagem nas fatias e a quantidade quando o usuário passa o mouse.
    pie_fig.update_traces(textposition="inside", textinfo="label+percent", hovertemplate="%{label}: %{value}<extra></extra>")
    style_figure(pie_fig, 360)
    # Devolve as quatro figuras para o Dash atualizar o dashboard.
    return map_fig, area_fig, bar_fig, pie_fig


# Este bloco roda quando executamos o arquivo diretamente com python app.py.
if __name__ == "__main__":
    # Usa a porta indicada pelo ambiente de hospedagem ou a porta 8050 no computador local.
    port = int(os.environ.get("PORT", "8050"))
    # Inicia o servidor da aplicação sem ativar o modo de depuração.
    app.run(host="0.0.0.0", port=port, debug=False)