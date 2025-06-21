# Import required libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Initialize the Dash app
app = dash.Dash(__name__)

# Load the dataset
df = pd.read_csv('data/data.csv')

# Data cleaning
df['date'] = pd.to_datetime(df['date'])  # Convert date column to datetime
df = df.fillna(0)  # Fill missing values with 0 for simplicity
countries = df['location'].unique()  # Get unique countries for dropdown

# Define the layout of the app
app.layout = html.Div([
    html.H1("COVID-19 Dashboard", style={'textAlign': 'center', 'color': '#003087'}),
    
    # Dropdown for country selection
    html.Label("Select Country:"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in countries],
        value='United States',  # Default value
        style={'width': '50%', 'margin': '10px auto'}
    ),
    
    # Date range slider
    html.Label("Select Date Range:"),
    dcc.DatePickerRange(
        id='date-picker',
        min_date_allowed=df['date'].min(),
        max_date_allowed=df['date'].max(),
        initial_visible_month=df['date'].max(),
        start_date=df['date'].min(),
        end_date=df['date'].max(),
        style={'margin': '10px'}
    ),
    
    # Line chart for cases and deaths
    dcc.Graph(id='line-chart'),
    
    # Bar chart for total cases by continent
    dcc.Graph(id='bar-chart'),
    
    # Map for global cases
    dcc.Graph(id='map-chart')
])

# Define callback to update charts based on user input
@app.callback(
    [Output('line-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('map-chart', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_charts(selected_country, start_date, end_date):
    # Filter data based on user input
    filtered_df = df[(df['location'] == selected_country) & 
                     (df['date'] >= start_date) & 
                     (df['date'] <= end_date)]
    
    # Line chart for cases and deaths over time
    line_fig = px.line(
        filtered_df,
        x='date',
        y=['total_cases', 'total_deaths'],
        title=f'COVID-19 Cases and Deaths in {selected_country}',
        labels={'value': 'Count', 'date': 'Date', 'variable': 'Metric'}
    )
    
    # Bar chart for total cases by continent (using latest data)
    continent_df = df[df['date'] == df['date'].max()][['continent', 'total_cases']].groupby('continent').sum().reset_index()
    bar_fig = px.bar(
        continent_df,
        x='continent',
        y='total_cases',
        title='Total COVID-19 Cases by Continent',
        labels={'total_cases': 'Total Cases', 'continent': 'Continent'},
        color='continent'
    )
    
    # Map for global cases (latest data)
    map_df = df[df['date'] == df['date'].max()]
    map_fig = px.scatter_geo(
        map_df,
        locations='iso_code',
        size='total_cases',
        hover_name='location',
        title='Global COVID-19 Cases',
        projection='natural earth'
    )
    
    return line_fig, bar_fig, map_fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)