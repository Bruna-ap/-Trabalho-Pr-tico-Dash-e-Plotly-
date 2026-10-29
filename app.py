"""Dashboard de Medalhas Olímpicas — trabalho prático de Visualização de Dados."""
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "Country_Medals.csv"
MEDALS = ["Gold", "Silver", "Bronze"]
MEDAL_LABELS = {"Gold": "Ouro", "Silver": "Prata", "Bronze": "Bronze"}
MEDAL_COLORS = {"Ouro": "#E9B949", "Prata": "#C5D0D8", "Bronze": "#CD8A5A"}
COLORS = {
    "background": "#101820",
    "panel": "#1B2833",
    "text": "#F4F7F8",
    "muted": "#B8C5CC",
    "gold": "#E9B949",
    "grid": "#354652",
}


def load_data():
    """Load and prepare the Olympic medal dataset provided with the assignment."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            "Arquivo Country_Medals.csv não encontrado. Coloque o CSV na mesma pasta de app.py."
        )

    data = pd.read_csv(CSV_PATH)
    data.columns = [str(column).strip() for column in data.columns]
    required = ["Year", "Host_country", "Host_city", "Country_Name", *MEDALS]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError("Colunas ausentes na base Country_Medals.csv: " + ", ".join(missing))

    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    for medal in MEDALS:
        data[medal] = pd.to_numeric(data[medal], errors="coerce").fillna(0)
    for column in ["Host_country", "Host_city", "Country_Name"]:
        data[column] = data[column].astype("string").str.strip()
    data = data.dropna(subset=["Year", "Country_Name", "Host_country"]).copy()
    data = data[data["Year"].between(1992, 2020)].copy()
    data["Year"] = data["Year"].astype(int)
    # Match the country label used in the tutorial and in Plotly's country map.
    data["Country_Name"] = data["Country_Name"].replace(
        {"United States": "United States of America"}
    )
    data["Total_Medals"] = data[MEDALS].sum(axis=1)
    return data


df = load_data()
app = Dash(__name__, title="Quadro de Medalhas Olímpicas")
server = app.server  # Render/Gunicorn entry point


def panel(children, extra_style=None):
    style = {
        "backgroundColor": COLORS["panel"],
        "borderRadius": "15px",
        "padding": "16px",
        "boxShadow": "0 6px 24px rgba(0, 0, 0, .16)",
        "minWidth": "0",
    }
    if extra_style:
        style.update(extra_style)
    return html.Div(children, style=style)


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


countries = sorted(df["Country_Name"].dropna().unique().tolist())
# Use a combined Year + host label so the selection is clear to the user.
editions = (
    df[["Year", "Host_country", "Host_city"]]
    .drop_duplicates()
    .sort_values("Year")
)
edition_options = [
    {
        "label": f'{int(row.Year)} — {row.Host_city}, {row.Host_country}',
        "value": int(row.Year),
    }
    for row in editions.itertuples(index=False)
]

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
                html.Label("Filtro global — tipo de medalha", style={"fontWeight": "bold"}),
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
                                html.Label("Ano olímpico (cidade e país sede) — gráfico de barras"),
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
        panel(dcc.Graph(id="world-map", config={"displayModeBar": False}), {"marginBottom": "18px"}),
        html.Div(
            [
                panel(dcc.Graph(id="area-chart", config={"displayModeBar": False})),
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


@app.callback(
    Output("world-map", "figure"),
    Output("area-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("pie-chart", "figure"),
    Input("medal-filter", "value"),
    Input("country-filter", "value"),
    Input("edition-filter", "value"),
)
def update_dashboard(medal_filter, selected_country, selected_year):
    """Update the three original charts from the global medal filter and the pie by country."""
    data = df.copy()
    if medal_filter == "Todos":
        data["Selected_Medals"] = data[MEDALS].sum(axis=1)
        medal_title = "total de medalhas"
    else:
        data["Selected_Medals"] = data[medal_filter]
        medal_title = f"medalhas de {MEDAL_LABELS[medal_filter].lower()}"

    # 1) Choropleth map: cumulative selected medal category from 1992 to 2020.
    country_totals = data.groupby("Country_Name", as_index=False)["Selected_Medals"].sum()
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
    map_fig.update_geos(bgcolor=COLORS["panel"], showframe=False, showcoastlines=False)

    # 2) Stacked area chart: the ten countries with the largest totals under the filter.
    top_countries = country_totals.nlargest(10, "Selected_Medals")["Country_Name"].tolist()
    area_data = data[data["Country_Name"].isin(top_countries)].groupby(
        ["Year", "Country_Name"], as_index=False
    )["Selected_Medals"].sum()
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
    bar_data = data[data["Year"] == int(selected_year)].groupby(
        "Country_Name", as_index=False
    )["Selected_Medals"].sum().nlargest(10, "Selected_Medals").sort_values("Selected_Medals")
    edition = editions[editions["Year"] == int(selected_year)].iloc[0]
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
    pie_totals = df[df["Country_Name"] == selected_country][MEDALS].sum()
    pie_data = pd.DataFrame(
        {
            "Medalha": ["Ouro", "Prata", "Bronze"],
            "Quantidade": [pie_totals["Gold"], pie_totals["Silver"], pie_totals["Bronze"]],
        }
    )
    pie_fig = px.pie(
        pie_data,
        names="Medalha",
        values="Quantidade",
        title=f"Medalhas de {selected_country} (1992–2020)",
        color="Medalha",
        color_discrete_map=MEDAL_COLORS,
        hole=0.38,
    )
    pie_fig.update_traces(textposition="inside", textinfo="label+percent", hovertemplate="%{label}: %{value}<extra></extra>")
    style_figure(pie_fig, 360)
    return map_fig, area_fig, bar_fig, pie_fig


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8050"))
    app.run(host="0.0.0.0", port=port, debug=False)
