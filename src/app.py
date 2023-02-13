import pandas as pd
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import plotly.express as px

import os

"""PREPARE DATA"""


file_path = os.path.join(os.path.dirname(__file__), 'games.csv')
df = pd.read_csv(file_path)
clear_df = df[(df.User_Score != 'tbd') & (df.Year_of_Release >= 2000)].dropna()
clear_df['User_Score'] = clear_df['User_Score'].astype(float)

"""DROPDOWNS AND SLIDER"""

year_selector = dcc.RangeSlider(
    id='year_selector',
    step=1,
    value=[df['Year_of_Release'].min(), df['Year_of_Release'].max()],
    marks={
        2000: '2000',
        2007: '2007',
        2016: '2016'
    }
)
genre_selector = dcc.Dropdown(
    id="genre_dropdown",
    options=[{"label": genre, "value": genre} for genre in clear_df["Genre"].unique()],
    multi=True,
    value=list(clear_df["Genre"].unique())
)
rating_selector = dcc.Dropdown(
    id="rating_dropdown",
    options=[{"label": Rating, "value": Rating} for Rating in clear_df["Rating"].unique()],
    multi=True,
    value=list(clear_df["Rating"].unique())
)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

"""LAYOUT"""

app.layout = html.Div([
    dbc.Row(html.H1('Game Industry History'), style={'margin-bottom': '20px', 'text-align': 'center'}),
    dbc.Row(html.Div([
        html.P('This dashboard provides insights into the history of the gaming industry. '
               'The dashboard is based on the "games.csv" data table, which contains information'
               'about video games such as their names, platforms, year of release, genre, critic '
               'score, user score, and rating. The dashboard allows users to filter the data based '
               'on genre and rating using multiple selection filters. The filtered data is then '
               'used to plot two interactive graphs: 1. A stacked area plot that shows the number'
               ' of game releases by year and platform. 2. A scatter plot that displays the '
               'relationship between critic scores and user scores, grouped by genre. '
               'The plot uses different colors to distinguish between genres. A third filter'
               ' allows users to set a range of years to further refine the data displayed in '
               'the graphs. Additionally, an interactive text box displays the number of games '
               'selected based on the filters applied.',
               style={'margin-bottom': '20px'})
    ], style={'text-align': 'center'})),
    dbc.Row([dbc.Col([
        html.Div('Genre selector', style={'margin-bottom': '10px'}),
        html.Div(genre_selector, style={'margin-bottom': '20px'})
    ], style={'margin-right': '20px'}),
        dbc.Col([
            html.Div('Rating selector', style={'margin-bottom': '10px'}),
            html.Div(rating_selector, style={'margin-bottom': '20px'})
        ], style={'margin-left': '20px'})], style={'margin-bottom': '20px'}),
    dbc.Row([dbc.Col([
        html.Div('Selected games:', style={'margin-bottom': '10px'}),
        html.Div(id='selected_games', style={'font-weight': 'bold', 'margin-bottom': '20px'})
    ], style={'margin-right': '20px'}),
        dbc.Col()]),
    dbc.Row([
        dbc.Col([
            html.Div('Stacked Area Plot of Video Game Releases by Year and Platform', style={'margin-bottom': '10px'}),
            dcc.Graph(id='stacked_area', style={'margin-bottom': '20px'})
        ], style={'margin-right': '20px'}, width=5),
        dbc.Col([
            html.Div('Genre-Based Scatter Plot of User and Critic Ratings', style={'margin-bottom': '10px'}),
            dcc.Graph(id='critic_user_scatter', style={'margin-bottom': '20px'})
        ], style={'margin-left': '20px'}, width=5)
    ], style={'margin-bottom': '20px'}),
    dbc.Row([dbc.Col([
        html.Div('Year Range Selector', style={'text-align': 'center', 'padding-top': '20px'}),
        html.Div(year_selector)
    ], width=3),
        dbc.Col()]),
], style={'padding': '20px'})

""""CALLBACKS"""


# Define the callback to update stacked area plot
@app.callback(
    Output(component_id='stacked_area', component_property='figure'),
    [Input(component_id='year_selector', component_property='value'),
     Input(component_id='genre_dropdown', component_property='value'),
     Input(component_id='rating_dropdown', component_property='value')]
)
def update_scatter_chart(years, selected_genres, selected_rating):
    chart_data = clear_df[(clear_df['Year_of_Release'] > years[0]) &
                          (clear_df['Year_of_Release'] < years[1]) &
                          (clear_df['Genre'].isin(selected_genres)) &
                          (clear_df['Rating'].isin(selected_rating))]
    games_grouped = chart_data.groupby(['Year_of_Release', 'Platform']).size().reset_index(name='Count')
    stacked_area = px.area(games_grouped, x='Year_of_Release', y='Count', color='Platform',
                           pattern_shape="Platform"
                           )
    return stacked_area


# Define the callback to update scatter plotter
@app.callback(
    Output(component_id='critic_user_scatter', component_property='figure'),
    [Input(component_id='year_selector', component_property='value'),
     Input(component_id='genre_dropdown', component_property='value'),
     Input(component_id='rating_dropdown', component_property='value')]
)
def update_scatter_chart(years, selected_genres, selected_rating):
    chart_data = clear_df[(clear_df['Year_of_Release'] > years[0]) &
                          (clear_df['Year_of_Release'] < years[1]) &
                          (clear_df['Genre'].isin(selected_genres)) &
                          (clear_df['Rating'].isin(selected_rating))]
    fig = px.scatter(chart_data, x='User_Score', y='Critic_Score', color="Genre")
    return fig


# Define the callback to update the selected games text
@app.callback(
    Output(component_id='selected_games', component_property='children'),
    [Input(component_id='year_selector', component_property='value'),
     Input(component_id='genre_dropdown', component_property='value'),
     Input(component_id='rating_dropdown', component_property='value')]
)
def update_text(years, selected_genres, selected_rating):
    current_games = clear_df[(clear_df['Year_of_Release'] > years[0]) &
                             (clear_df['Year_of_Release'] < years[1]) &
                             (clear_df['Genre'].isin(selected_genres)) &
                             (clear_df['Rating'].isin(selected_rating))]
    games = len(current_games.index)
    return games


if __name__ == '__main__':
    app.run_server(debug=True)
