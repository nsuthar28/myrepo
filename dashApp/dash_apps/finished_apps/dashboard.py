
from django.conf import settings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
import plotly.express as px

import dash
from dash import Dash, dcc, html, Input, Output, dash_table, State, callback_context
from dash.dash_table.Format import Format, Group, Scheme, Trim
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash

import dash_bootstrap_components as dbc

import base64
import io
import os

from dashApp.utils import *

path = settings.BASE_DIR
# Import file -- will need to have logic around whether CSV or Excel
media_path = os.path.join(path, 'media/Food_Distributor_Data_3items.csv')

# df = pd.read_csv(
#     media_path,
#     index_col='Date', parse_dates=True)

# df['Item'] = df['Item'].astype(str)

# # Identifying all Items to forecast
# items = df['Item'].unique()

# Identifying column names
# columns = list(df.columns)

# Creating empty data frame with results of models
df_results = pd.DataFrame(
    {'Item': [], 'Model': [], 'MAPE': [], 'MAE': [], 'RMSE': [], 'R-Squared': []})


# df_results, df_results_best, df1_f1 = run_fcast_full(df, input_forecast_period)


# TESTING CODE FOR DASHBOARD

app = DjangoDash('dashboard', external_stylesheets=[dbc.themes.CERULEAN])
# app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])


# server = app.server  # for deployment

# https://dash.plot.ly/dash-core-components/dropdown
# We need to construct a dictionary of dropdown values for the years





# styling
rcorners1 = {
    #   'border-radius': '25px',
    'background': 'white',
    'padding-top': '1rem',
    'padding-left': '1rem',
    'height': '8rem',
    'color': '#00A7E1',
    'margin-bottom': '1rem'

}


tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px'

}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#00A7E1',
    'color': 'white',
    'fontWeight': 'bold',
    'padding': '6px'
}


# table data

PAGE_SIZE = 10

#


app.layout = html.Div([

    dbc.Row(
        html.Div([
            html.H4('Forecast Dashboard', style={
                    'padding': '1rem 1rem', 'background': 'white', 'margin-bottom': '1rem'})
        ])
    ),

    dbc.Row(

        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),

            # dcc.Store(id='prelim-store', data=[], storage_type='memory')
        ])

    ),

    dbc.Row([
        dbc.Col(
            html.Div([
                dbc.Row([
                    dcc.Graph(id='fcast_graph_main')
                ]),
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.P('Select Item', style={
                                   'paddingTop': '1rem'}),
                            dcc.Dropdown(
                                id='product_dropdown',
                                options=[],
                                multi=True
                            )
                        ]),

                        width=4

                    ),
                    dbc.Col(
                        html.Div([
                            html.P(''),


                        ]),

                        width=4


                    ),
                    dbc.Col(
                        html.Div([
                            html.P('Set Forecast Horizon',
                                   style={'paddingTop': '1rem'}),
                            html.Div(
                                [dcc.Input(id='input_fcast_period', type='number', placeholder='Input nper')]),
                            html.Button('Forecast', id='button_fcast', n_clicks=0, style={
                                        'margin-top': '1rem'}, className='btn btn-outline-primary')
                        ]),
                        width=4

                    )

                ])

            ], className='p-3 mb-2 bg-white text-dark'),

            width=8


        ),

        dbc.Col(
            html.Div([
                html.H5('Performance Metrics'),
                html.Div(id='fit_output'),
                dcc.Loading(
                    id='loading_table_1',
                    type='circle',
                    fullscreen=True,
                    children=html.Div([

                        dcc.Store(id='intermediate-value'),

                        html.Div(id='container_table_dfresults')



                    ])
                ),







            ], className='p-3 mb-2 bg-white text-dark'),

            width=4


        ),


    ]),

    dbc.Row([
        dbc.Col(
            html.Div([
                html.Div(id='table_fcast_detail_container')
            ], className='p-3 mb-2 bg-white text-dark')
        )


    ]),


    # Empty row for testing stuff
    dbc.Row([
        html.Div(id='test1'),
        dcc.Store(id='test_store', storage_type='session')
    ])



])


# TEMPORARY TEST CALL BACKS
# @app.callback(Output('test_store', 'data'),
#               Input('prelim-store', 'data'),
#               prevent_initial_call=True)

# def test_store(data):
#     df = pd.read_json(data, orient='split')

#     return df.to_json(date_format='iso', orient='split')

# @app.callback(Output('test1', 'children'),
#               Input('test_store', 'data'),
#               prevent_initial_call=True)

# def test_test(data):

#     df = pd.read_json(data, orient='split')

#     return html.Div([


#         dash_table.DataTable(
#             df.to_dict('records'),
#             [{'name': i, 'id': i} for i in df.columns]
#         ),

#         html.Hr(),  # horizontal line


#     ])
##### END TEST ##############


###### CALL BACKS #####

## Callback for main graph before forecast is ran
@app.callback(Output('fcast_graph_main', 'figure'),
            [Input('intermediate-value', 'data'),
            Input('button_fcast', 'n_clicks'),
            Input('product_dropdown', 'value'),
            Input('upload-data', 'contents')],
            State('input_fcast_period', 'value'),
            State('upload-data', 'filename'),
            State('upload-data', 'last_modified'),
            prevent_initial_call=True)

def update_figure(stored_data, button_click, product_dropdown, file_content, value, filename, file_last_modified, **kwargs):    
    changed_id = [p['prop_id'] for p in kwargs['callback_context'].triggered][0]

    content_type, content_string = file_content[0].split(',')
    decoded = base64.b64decode(content_string)
    local_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')),index_col='Date', parse_dates=True)
    
    if 'button_fcast' in changed_id:
        df1 = pd.read_json(stored_data[0], orient='split')
        df1['Item'] = df1['Item'].astype(str)

        df1 = df1.reset_index(drop=False, inplace=False)
        
        df1 = df1.rename(columns={'index':'Date'})
        if product_dropdown:
            df1 = df1[df1['Item'].isin(product_dropdown)]
        
        filtered_df = df1.groupby(['Date'], as_index=False)[['Qty', 'Future_Forecast_BEST', 'Future_Forecast_ARIMA','Future_Forecast_LR', 'Future_Forecast_RF' ]].sum()

        #cleaning up forecast numbers for graphing -- turning zeros into np.nan and removing gap in graph numbers
        filtered_df = fill_na_df(filtered_df, value)
        filtered_df = fill_last_val_grp(filtered_df, value)

        fig = px.line(filtered_df, x='Date', y=['Qty', 'Future_Forecast_BEST', 'Future_Forecast_ARIMA','Future_Forecast_LR', 'Future_Forecast_RF' ], title='Sales Data', template='plotly_white', markers=True)

        fig['data'][0]['line']['color']='#2683b9'
        fig['data'][0]['line']['width']=2

        fig.update_layout(
                transition_duration=500,
                font_family = "system-ui",
                title={'text':'Sales Data', 'font':{'size':20, 'color':'#2fa4e7'}}
            
            )

        return fig   

    elif not button_click:
        df1 = local_df.copy().reset_index()
        df1['Item'] = df1['Item'].astype(str)

        if product_dropdown:
            df1 = df1[df1['Item'].isin(product_dropdown)]
        
        filtered_df = df1.groupby(['Date'], as_index=False)['Qty'].sum()

        fig = px.line(filtered_df, x='Date', y='Qty', title='Sales Data', template='plotly_white', markers=True)

        fig['data'][0]['line']['color']='#2683b9'
        fig['data'][0]['line']['width']=2

        fig.update_layout(
                transition_duration=500,
                font_family = "system-ui",
                title={'text':'Sales Data', 'font':{'size':20, 'color':'#2fa4e7'}}
            
            )

        return fig

## Callback for set product-dropdown values
@app.callback(Output('product_dropdown', 'options'),
              Input('upload-data', 'contents'),
              prevent_initial_call=True)

def set_dropdown(file_content):
    if file_content == None:
        return dash.no_update

    content_type, content_string = file_content[0].split(',')
    decoded = base64.b64decode(content_string)
    local_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')),index_col='Date', parse_dates=True)
    
    product_options = []
    for po in local_df['Item'].unique():
        product_options.append({'label': str(po), 'value': str(po)})
    
    return product_options

## Callback for using dcc.Store to store the forecast analysis - main function and results outputs
@app.callback(
    Output('intermediate-value', 'data'),
    Input('button_fcast', 'n_clicks'),
    State('input_fcast_period', 'value'),
    State('upload-data', 'contents'),
    prevent_initial_call=True)
    
def clean_data(button_click, value,file_content, **kwargs): # TO BE UPDATED! Need to update the value to feed in user input value for Forecast Period
    
    changed_id = [p['prop_id'] for p in kwargs['callback_context'].triggered][0]
    content_type, content_string = file_content[0].split(',')
    
    decoded = base64.b64decode(content_string)
    local_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')),index_col='Date', parse_dates=True)

    horizon = int(np.floor(len(local_df.index.unique())*.2))
    
    items = local_df['Item'].unique()

    if 'button_fcast' in changed_id:
        
        df_results, df_results_best, df1_f1 = run_fcast_full(local_df, value, horizon, items)

        # a few filter steps that compute the data
        # as it's needed in the future callbacks
        df_1 = df1_f1
        df_2 = df_results
        df_3 = df_results_best
        return [ df_1.to_json(date_format='iso', orient='split'), df_2.to_json(date_format='iso', orient='split'), df_3.to_json(date_format='iso', orient='split')]


## Callback for results table
@app.callback(
    Output('fit_output', 'children'),
    Input('button_fcast', 'n_clicks'),
    State('input_fcast_period', 'value'),
    prevent_initial_call=True
    )

def update_table1( btn1, value):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'button_fcast' in changed_id:

        return 'Below are key forecast metrics by model'
    else:
        return 'Please initiate forecast to see performance metrics'




## Callback for results table
@app.callback(
    Output('container_table_dfresults', 'children'),
    Input('intermediate-value', 'data'),
    prevent_initial_call=True
    )

def update_table1( stored_data):
    if [stored_data] == [None]:
        return dash.no_update

    else:
        df = pd.read_json(stored_data[1], orient='split')

        df['Item'] = df['Item'].astype(str)
        df['Model'] = df['Model'].astype(str)

        return dash_table.DataTable(

            id='table_df_results',
            
            columns= [
                dict(id='Item', name='Item'),
                dict(id='Model', name='Model'),
                dict(id='MAPE', name='MAPE', type='numeric', format=Format(precision=4, scheme=Scheme.fixed, trim=Trim.yes)),
                dict(id='MAE', name='MAE', type='numeric', format=Format(precision=4, scheme=Scheme.fixed, trim=Trim.yes)),
                dict(id='RMSE', name='RMSE', type='numeric', format=Format(precision=4, scheme=Scheme.fixed, trim=Trim.yes)),
                dict(id='R-Squared', name='R-Squared', type='numeric', format=Format(precision=4, scheme=Scheme.fixed, trim=Trim.yes)),            
            ],
            data=df.to_dict('records'),
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            # page_action="native",
            # page_current= 0,
            # page_size= 10,
            style_table={'height':'400px', 'overflowX': 'auto'},
            style_cell={
                'height':'auto',
                'minWidth': '6rem', 'width': '6rem', 'maxWidth': '6rem',
                'whiteSpace': 'normal'
            },
            fixed_rows={'headers':True},
            fixed_columns={'headers': True, 'data': 1}
        )    




## Callback for table forecast detail
@app.callback(
    Output('table_fcast_detail_container', 'children'),
    [Input('intermediate-value', 'data'),
    Input('product_dropdown', 'value')],
    prevent_initial_call=True
)

def table_fcast_detail(stored_data, product_dropdown):       
    if None in [stored_data, product_dropdown]:
        return dash.no_update
    else:
        df = pd.read_json(stored_data[0], orient='split')
        df = df[['Item', 'Qty', 'Future_Forecast_BEST', 'Future_Forecast_ARIMA', 'Future_Forecast_LR', 'Future_Forecast_RF' ]]
        df['Item'] = df['Item'].astype(str)
        
        
        df = df.reset_index()
        df = df.rename(columns={'index':'Date'})

        for i in df.columns:
            if "Future_" in str(i):
                df = df.rename(columns={'{}'.format(i):'{}'.format(i[7:])})

        # df['Date'] = pd.DatetimeIndex(df['Date']).strftime("%Y-%m-%d")
        df['Date'] = df['Date'].dt.date

        #sorting by date then item
        df = df.sort_values(['Date', 'Item'])

        #including dropdown filter rule
        if product_dropdown:
            df = df[df['Item'].isin(product_dropdown)]    

        #populating temporary column list of dictionaries for column naming and formating 
        col_temp = [
            dict(id='Date', name='Date'),
            dict(id='Item', name='Item'),
        ]

        #looping addition of all other columns as numeric and formated with comma
        for clmn in df.columns[2:]:
            col_temp.append(dict(id=clmn, name=clmn, type='numeric', format=Format(precision=0, scheme=Scheme.fixed, trim=Trim.yes).group(True)))
        
        return [
            html.H5('Detail'),
            dash_table.DataTable(    

                id='datatable-interactivity',
                
                columns= col_temp,
                data=df.to_dict('records'),
                editable=True,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                # page_action="native",
                # page_current= 0,
                # page_size= 10,
                style_table={'height':'400px'},
                style_cell={
                    'height':'auto',
                    'maxWidth':'4rem'
                },
                fixed_rows={'headers':True},
                export_format='csv'

            )                
        ]
    