import pandas as pd
import numpy as np
import dash
from dash import dcc, html
import plotly.express as px
import pycountry

#Get dataset from wiki
data = {
    'Year': [
        1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 
        1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018
    ],
    'Winner': [
        'Uruguay', 'Italy', 'Italy', 'Uruguay', 'West Germany', 'Brazil', 'Brazil', 'England', 'Brazil', 'West Germany',
        'Argentina', 'Italy', 'Argentina', 'West Germany', 'Brazil', 'France', 'Brazil', 'Italy', 'Spain', 'Germany', 'France'
    ],
    'Runner-Up': [
        'Argentina', 'Czechoslovakia', 'Hungary', 'Brazil', 'Hungary', 'Sweden', 'Czechoslovakia', 'West Germany', 'Italy', 'Netherlands',
        'Netherlands', 'West Germany', 'West Germany', 'Argentina', 'Italy', 'Brazil', 'Germany', 'France', 'Netherlands', 'Argentina', 'Croatia'
    ]
}

#Set dataframe
df = pd.DataFrame(data)

#Get all countries in the world
all_countries = {country.name for country in pycountry.countries}

#Count number of wins per country, replace West Germany with Germany and England with United Kingdom
win_counts = df['Winner'].replace({'West Germany': 'Germany'}).value_counts().reset_index()
win_counts = df['Winner'].replace({'England': 'United Kingdom'}).value_counts().reset_index()
win_counts.columns = ['Country', 'Wins']

#Ensure all countries are included in win_counts with zero wins if necessary
full_win_counts = pd.DataFrame({'Country': list(all_countries)})
full_win_counts = full_win_counts.merge(win_counts, on='Country', how='left').fillna(0)
full_win_counts['Wins'] = full_win_counts['Wins'].astype(int)

#Create Choropleth with custom colors
fig = px.choropleth(
    full_win_counts,
    locations='Country',
    locationmode='country names',
    color='Wins',
    color_continuous_scale=[(0, 'lightgrey'), (0.1, 'yellow'), (0.5, 'orange'), (1, 'red')],
    title='FIFA World Cup Wins by Country'
)

#Create Dash app layout
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard"),
    dcc.Graph(figure=fig),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': c, 'value': c} for c in sorted(all_countries)],
        placeholder="Select a country",
        style={'backgroundColor': 'white'}
    ),
    html.Div(id='win-output', style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px'}),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': y, 'value': y} for y in df['Year']],
        placeholder="Select a year",
        style={'backgroundColor': 'white'}
    ),
    html.Div(id='match-output', style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px'})
])

#Callbacks for user interaction
@app.callback(
    dash.Output('win-output', 'children'),
    [dash.Input('country-dropdown', 'value')]
)
def display_wins(country):
    if country:
        wins = full_win_counts[full_win_counts['Country'] == country]['Wins'].values
        return f"{country} has won {wins[0]} times."
    return ""

@app.callback(
    dash.Output('match-output', 'children'),
    [dash.Input('year-dropdown', 'value')]
)
def display_match(year):
    if year:
        match = df[df['Year'] == year]
        if not match.empty:
            return f"Winner: {match['Winner'].values[0]}, Runner-Up: {match['Runner-Up'].values[0]}"
    return ""

#Run App
if __name__ == '__main__':
    app.run(debug=True)
