import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Cargar los datos (puedes cambiar esta parte si estás en Colab)
df = pd.read_csv('Viral_Social_Media_Trends.csv')

# Crear columnas auxiliares
df['Total_Engagement'] = df['Likes'] + df['Shares'] + df['Comments']

# Inicializar app Dash
app = Dash(__name__)
app.title = "Viral Social Media Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Viral Social Media Trends & Engagement Dashboard", style={'textAlign': 'center'}),

    # Filtros
    html.Div([
        html.Div([
            html.Label("Plataforma"),
            dcc.Dropdown(
                id='platform-filter',
                options=[{'label': p, 'value': p} for p in df['Platform'].unique()],
                value=df['Platform'].unique().tolist(),
                multi=True
            )
        ], style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Región"),
            dcc.Dropdown(
                id='region-filter',
                options=[{'label': r, 'value': r} for r in df['Region'].unique()],
                value=df['Region'].unique().tolist(),
                multi=True
            )
        ], style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Tipo de contenido"),
            dcc.Dropdown(
                id='content-filter',
                options=[{'label': c, 'value': c} for c in df['Content_Type'].unique()],
                value=df['Content_Type'].unique().tolist(),
                multi=True
            )
        ], style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Nivel de engagement"),
            dcc.Dropdown(
                id='engagement-filter',
                options=[{'label': e, 'value': e} for e in df['Engagement_Level'].unique()],
                value=df['Engagement_Level'].unique().tolist(),
                multi=True
            )
        ], style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    html.Hr(),

    # KPIs
    html.Div(id='kpi-cards', style={'display': 'flex', 'justifyContent': 'space-around'}),

    html.Br(),

    # Gráficos
    dcc.Graph(id='top-hashtags'),
    dcc.Graph(id='engagement-by-content'),
    dcc.Graph(id='interactions-by-platform'),
    dcc.Graph(id='engagement-map'),
    dcc.Graph(id='engagement-distribution')
])

# Callback
@app.callback(
    [
        Output('kpi-cards', 'children'),
        Output('top-hashtags', 'figure'),
        Output('engagement-by-content', 'figure'),
        Output('interactions-by-platform', 'figure'),
        Output('engagement-map', 'figure'),
        Output('engagement-distribution', 'figure')
    ],
    [
        Input('platform-filter', 'value'),
        Input('region-filter', 'value'),
        Input('content-filter', 'value'),
        Input('engagement-filter', 'value')
    ]
)
def update_dashboard(platforms, regions, contents, engagement_levels):
    dff = df[
        df['Platform'].isin(platforms) &
        df['Region'].isin(regions) &
        df['Content_Type'].isin(contents) &
        df['Engagement_Level'].isin(engagement_levels)
    ]

    # KPIs
    kpi_total_posts = len(dff)
    kpi_avg_views = int(dff['Views'].mean())
    top_hashtag = dff.groupby('Hashtag')['Total_Engagement'].sum().sort_values(ascending=False).idxmax()
    top_platform = dff['Platform'].value_counts().idxmax()

    kpis = [
        html.Div([
            html.H3("Total Posts"),
            html.P(f"{kpi_total_posts}")
        ], style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'borderRadius': '10px'}),

        html.Div([
            html.H3("Avg Views"),
            html.P(f"{kpi_avg_views:,}")
        ], style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'borderRadius': '10px'}),

        html.Div([
            html.H3("Top Hashtag"),
            html.P(top_hashtag)
        ], style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'borderRadius': '10px'}),

        html.Div([
            html.H3("Top Platform"),
            html.P(top_platform)
        ], style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'borderRadius': '10px'}),
    ]

    # Top Hashtags
    hashtag_df = dff.groupby('Hashtag')['Total_Engagement'].sum().nlargest(10).reset_index()
    fig1 = px.bar(hashtag_df, x='Total_Engagement', y='Hashtag', orientation='h',
                  title='Top 10 Hashtags by Engagement', color='Total_Engagement')

    # Engagement by Content Type
    fig2 = px.pie(dff, names='Content_Type', values='Total_Engagement',
                  title='Engagement by Content Type')

    # Interactions by Platform
    platform_df = dff.groupby('Platform')[['Likes', 'Shares', 'Comments']].sum().reset_index()
    fig3 = px.bar(platform_df, x='Platform', y=['Likes', 'Shares', 'Comments'],
                  title='Interactions by Platform', barmode='group')

    # Map
    region_df = dff.groupby('Region')['Views'].sum().reset_index()
    fig4 = px.choropleth(region_df, locations='Region', locationmode='country names',
                         color='Views', title='Views by Region',
                         color_continuous_scale='Turbo')

    # Engagement Level Distribution
    fig5 = px.histogram(dff, x='Engagement_Level', title='Engagement Level Distribution',
                        color='Engagement_Level')

    return kpis, fig1, fig2, fig3, fig4, fig5

# Ejecutar servidor
if __name__ == '__main__':
    app.run(debug=True)
