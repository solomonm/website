### Data
import pandas as pd
import datetime
import urllib

### Graphing
import plotly.graph_objects as go
import plotly.express as px
from textwrap import wrap
### Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from navbar import Navbar
from footer import Footer
from assets.mappings import states, colors

from projections.utils import cols, df_us, add_cases, df_projections


def build_continent_map(map_date,val='Active', continent = 'World'):
    global df_projections

    df_continent = df_projections
    if continent !='World':
        df_continent = df_projections.loc[df_projections.Continent == continent] #Filter by continent

    if isinstance(map_date, str):
        map_date = datetime.datetime.strptime(map_date, '%Y-%m-%d').date()

    df_map = df_continent.loc[df_continent['Day'] == map_date]
    df_map = df_map.loc[df_map['Province'] == 'None'] #exclude province data
    df_map = df_map.loc[df_map['Country'] != 'None'] #exclude global world data
    df_map = df_map.applymap(str)

    fig = go.Figure()

    if (val is not None) and (val in cols):

        df_map.loc[:,'text'] = df_map['Country'] + '<br>' + \
                    'Total Detected ' + df_map['Total Detected'] + '<br>' + \
                    'Active ' + df_map['Active'] + '<br>' + \
                    'Active Hospitalized ' + df_map['Active Hospitalized'] + '<br>' + \
                    'Cumulative Hospitalized ' + df_map['Cumulative Hospitalized'] + '<br>' + \
                    'Total Detected Deaths ' + df_map['Total Detected Deaths']


        fig = go.Figure(data=go.Choropleth(
                locations=df_map['Country'],
                z=df_map[val].astype(float),
                locationmode="country names",
                autocolorscale=False,
                colorscale='inferno_r',
                text=df_map['text'], # hover text
                marker_line_color='black', # line markers between states
                colorbar_title='<br>'.join(wrap(''.join(['{}'.format(add_cases(val))]), width=10))
            ))

    fig.update_layout(
            margin=dict(l=10, r=10, t=50, b=50),
            title_text=add_cases('{} Predicted {} {}'.format(map_date.strftime('%b %d,%Y'), continent, val)),
            geo = dict(
                scope= continent.lower(),
                projection=go.layout.geo.Projection(type = 'natural earth'),
                showlakes=True, # lakes
                lakecolor='rgb(255, 255, 255)',
                countrycolor='lightgray',
                landcolor='whitesmoke',
                showland=True,
                showframe = False,
                showcoastlines = True,
                showcountries=True,
                visible = False,
            ),
            modebar={
                'orientation': 'v',
                'bgcolor': 'rgba(0,0,0,0)',
                'color': 'lightgray',
                'activecolor': 'gray'
            }
        )

    graph = dcc.Graph(
        id='continent-projection-map',
        figure=fig,
    )

    return graph

def build_us_map(map_date,val='Active'):

    global df_us

    if isinstance(map_date, str):
        map_date = datetime.datetime.strptime(map_date, '%Y-%m-%d').date()

    df_map = df_us.loc[df_us['Day']==map_date]
    df_map = df_map.loc[df_us['Province']!='US']
    df_map = df_map.applymap(str)

    df_map.loc[:,'code'] = df_map.Province.apply(lambda x: states[x])

    fig = go.Figure()

    if (val is not None) and (val in cols):

        df_map.loc[:,'text'] = df_map['Province'] + '<br>' + \
                    'Total Detected ' + df_map['Total Detected'] + '<br>' + \
                    'Active ' + df_map['Active'] + '<br>' + \
                    'Active Hospitalized ' + df_map['Active Hospitalized'] + '<br>' + \
                    'Cumulative Hospitalized ' + df_map['Cumulative Hospitalized'] + '<br>' + \
                    'Total Detected Deaths ' + df_map['Total Detected Deaths']

        fig = go.Figure(data=go.Choropleth(
                locations=df_map['code'],
                z=df_map[val].astype(float),
                locationmode='USA-states',
                colorscale='inferno_r',
                autocolorscale=False,
                text=df_map['text'], # hover text
                marker_line_color='white' , # line markers between states
                colorbar_title='<br>'.join(wrap(''.join(['{}'.format(add_cases(val))]), width=10))
            ))

    fig.update_layout(
            margin=dict(l=10, r=10, t=50, b=50),
            title_text=add_cases('{} Predicted US {}'.format(map_date.strftime('%b %d,%Y'), val)),
            geo = dict(
                scope='usa',
                projection=go.layout.geo.Projection(type = 'albers usa'),
                showlakes=True, # lakes
                lakecolor='rgb(255, 255, 255)'
            ),
            modebar={
                'orientation': 'v',
                'bgcolor': 'rgba(0,0,0,0)',
                'color': 'lightgray',
                'activecolor': 'gray'
            }
        )

    graph = dcc.Graph(
        id='us-projection-map',
        figure=fig
    )
    return graph

def find_smallest_scope(state, country, continent):
    location = state
    if state in 'None':
        if country is 'None':
            location = continent
        else:
            location = country
    return location

def build_state_projection(state, country, continent, vals):
    global df_projections
    location = find_smallest_scope(state, country, continent)

    df_projections_sub = df_projections.loc[ (df_projections.Province == state) & (df_projections.Country == country)]
    if continent not in ['US', 'World']:
        df_projections_sub = df_projections_sub.loc[(df_projections_sub.Continent == continent)]
    if continent == 'US':
        df_projections_sub = df_projections.loc[(df_projections.Country == 'US') & (df_projections.Province == state)]
    if continent == 'World':
        if country =='None':
            df_projections_sub = df_projections.loc[(df_projections.Continent == 'None')] #include only global world data
    fig = go.Figure()

    if (vals is not None) and (set(vals).issubset(set(cols))):
        for val in vals:
            i = cols[val]
            fig.add_trace(go.Scatter(
                name=val,
                showlegend=True,
                x=df_projections_sub['Day'],
                y=df_projections_sub[val].values,
                mode="lines+markers",
                marker=dict(color=colors[i]),
                line=dict(color=colors[i])
            ))

    title = '<br>'.join(wrap('<b> Projections for {} </b>'.format(location), width=26))
    fig.update_layout(
                height=550,
                title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                title_font_size=25,
                xaxis={'title': "Date",'linecolor': 'lightgrey'},
                yaxis={'title': "Count",'linecolor': 'lightgrey'},
                legend_title='<b> Values Predicted </b>',
                margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                hovermode='closest',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend={
                        "orientation": "h",
                        "xanchor": "center",
                        "y": -0.2,
                        "x": 0.5
                        },
                modebar={
                    'orientation': 'v',
                    'bgcolor': 'rgba(0,0,0,0)',
                    'color': 'lightgray',
                    'activecolor': 'gray'
                }
            )

    graph = dcc.Graph(
        id='projection-graph',
        figure=fig
    )
    return graph

def get_stat(d, val, scope):
    global df_projections
    df_projections_sub = df_projections

    if isinstance(d, str):
        d = datetime.datetime.strptime(d, '%Y-%m-%d').date()

    if scope == 'US':
        df_projections_sub = df_projections.loc[(df_projections.Country == scope) & (df_projections.Province == 'None')]
    elif scope =='World':
        df_projections_sub = df_projections.loc[df_projections.Continent == 'None']
    else:
        df_projections_sub = df_projections.loc[(df_projections.Continent == scope) & (df_projections.Country == 'None')]

    df_projections_sub = df_projections_sub.loc[df_projections_sub['Day']==d].reset_index()

    card_content = [
        dbc.CardHeader(
            f'{df_projections_sub.iloc[0][val]:,}',
            style={"textAlign":"center","fontSize":30,"fontWeight": "bold","color":'#1E74F0'}
        ),
        dbc.CardBody(
            [
                html.H5(add_cases(val),id='us-stats-cards'),
            ]
        ),
    ]
    return card_content