# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df["Launch Site"].unique()

# Create a dash application
app = dash.Dash(__name__)


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Div([
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                                                [{'label': site, 'value': site} for site in launch_sites],
                                        value='ALL',   # default value
                                        placeholder="Select a launch site here",
                                        searchable=True
                                    )
                                ]),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(
                                    dcc.Graph(
                                        id='success-pie-chart',
                                        )
                                    ),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                html.Div([
                                    dcc.RangeSlider(id='payload-slider',
                                                min=0, 
                                                max=10000, 
                                                step=1000,
                                                marks={i: f'{i}' for i in range(0, 10001, 2000)},
                                                value=[min_payload, max_payload],
                                                )
                                ]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        data = filtered_df
        fig = px.pie(data, values='class', 
        names='Launch Site', 
        title='Percentage Landing Success(1)/Failure(0), All Launch Sites')
        return fig
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        df_counts = (
            site_df['class']
            .value_counts()
            .reindex([0, 1], fill_value=0)
            .rename_axis('class')
            .reset_index(name='count')
        )
        df_counts['label'] = df_counts['class'].map({0: 'Failure', 1: 'Success'})
        fig = px.pie(df_counts, values='count', names='class',
                        title=f'Percentage Landing Success(1)/Failure(0), Launch Sites ({entered_site})')
        return fig
        # return the outcomes piechart for a selected site


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('payload-slider', 'value'),
        Input('site-dropdown', 'value')
    ]
)
def success_payload_scatter_chart(payload_value, entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

    # filter by payload range (assuming payload_value is [min, max])
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= payload_value[0]) &
        (filtered_df['Payload Mass (kg)'] <= payload_value[1])
    ]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Landing Success(1)/Failure(0) vs Payload: {entered_site}'
    )
    return fig



# Run the app
if __name__ == '__main__':
    app.run()
