import pandas as pd
import numpy as np
import plotly.express as px

from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score

# forecasting algorithms
from dashApp.forecasting_algorithms.model3_lrrf import model3_lrrf
from dashApp.forecasting_algorithms.model2_auto_arima import model2_auto_arima 
from dashApp.forecasting_algorithms.aarima_fcast import aarima_fcast  

from dashApp.models import *

data_freq = 'W'

# defining how many past periods to use to in LR and RF models to predict next Y value
T = 12

# Function for calculating scores and storing in empty dataframe called df_results
def store_scores(df, fcast_col_name, model_name, horizon, items):

    # horizon = int(np.floor(len(df.index.unique())*.2))

    # prevent global
    Ntest = horizon

    # Creating empty data frame with results of models
    df_results = pd.DataFrame({'Item':[], 'Model':[], 'MAPE':[], 'MAE':[], 'RMSE':[], 'R-Squared':[]})    

    # items = df['Item'].unique()

    for i in items:
        y1 = df[df['Item'] == i].iloc[-Ntest:]['Qty'] #to loop
        y2 = df[df['Item'] == i].iloc[-Ntest:][fcast_col_name] #to loop





        df_results_temp = pd.DataFrame({'Item':[], 'Model':[], 'MAPE':[], 'MAE':[], 'RMSE':[], 'R-Squared':[]})

        df_results_temp.loc[0,'Item'] = i #to loop
        df_results_temp.loc[0,'Model'] = model_name
        df_results_temp.loc[0,'MAPE'] = mean_absolute_percentage_error(y1,y2)
        df_results_temp.loc[0,'MAE'] = mean_absolute_error(y1,y2)
        df_results_temp.loc[0,'RMSE'] = np.sqrt(mean_squared_error(y1, y2))
        df_results_temp.loc[0,'R-Squared'] = r2_score(y1, y2)

        df_results = df_results.append(df_results_temp)

    
    return df_results

# Function for Adding future date range to original DF for future forecasting
def df_w_fcast(df, input_forecast_period,items):

    df_f1 = df.copy()
    #items = df['Item'].unique()
    for i in items:

        #create future date_range based on input forecast period
        df_future = pd.date_range(df.index[-1], periods=input_forecast_period+1, freq='W')
        df_future = df_future[1:]
        df_future = pd.DataFrame({'Date':df_future, 'Item':i}).set_index('Date') #reference column #to loop

        #add to df.index
        df_f1 = df_f1.append(df_future)

    return df_f1

# Function for forecasting with LR and RF models
# inputs - referenced df (df1 in this case), model_list (e.g. lr1_model_list ), model title (e.g. "LR")
def lr_rf_fcast_alt(df1, df1_f1, model_list, model_title, input_forecast_period, items): #inputs - referenced df (df1 in this case), model_list (e.g. lr1_model_list ), model title (e.g. "LR")


    #Forecasting future values and storing them into a list
    YYY = []

    for i in range(len(items)):

        Yfut_list = []

        df1_temp = df1[df1['Item'] == items[i]] #to loop

        # first test input; using the last T values of df
        X_fut = np.array(df1_temp['Qty'].iloc[-T:])
        last_x = X_fut

        for z in range(input_forecast_period):
              
            p = model_list[i].predict(last_x.reshape(1, -1))[0]
                        
            # update the predictions list
            Yfut_list.append(p)
            
            # make the new input
            last_x = np.roll(last_x, -1)
            last_x[-1] = p

        YYY.append(Yfut_list)

    #Bringing the list of forecasted values into the dataframe with all forecast values
    for i in range(len(items)):
        fcast_idx = (df1_f1['Item'] == items[i]) & (df1_f1.index > df1.index[-1]) #to loop
        df1_f1.loc[fcast_idx, 'Future_Forecast_{}'.format(model_title)] = YYY[i]

    return df1_f1

# Function to Run full forecast
def run_fcast_full (df, input_forecast_period, horizon, items):

    input_forecast_period = input_forecast_period
    
    dfx = df.copy()

    ## Running the model and calculating scores
    dfx, model_aarima = model2_auto_arima(dfx, horizon, items)
    
    df_results = pd.DataFrame()

    df_results = df_results.append(store_scores(dfx, 'AARIMA','ARIMA', horizon, items))
    #### 3rd Model - Machine Learning: LR & RF
    #running model 3 LR and RF
    # df1, lr1, lr2, model_rf = model3_lrrf(df)
    df1, lr1_model_list, rf_model_list = model3_lrrf(dfx, horizon, items)

    df1['Qty'] = df1['Qty'].astype(int)

    # Calculating and storing scores
    df_results = df_results.append(store_scores(df1, 'LR_multistep','LR_Multistep', horizon, items))
    # df_results = df_results.append(store_scores(df1, 'LR_multioutput','LR_Multioutput'))
    df_results = df_results.append(store_scores(df1, 'RF_multistep_test','Random Forest', horizon, items))

    df_results = df_results.sort_values(['Item', 'MAPE']).reset_index()
    df_results = df_results.loc[:,'Item':'R-Squared']
    #Storing all top results in a new dataframe
    df_results_best = pd.DataFrame()
    for i in items:
        df_results_best = df_results_best.append(df_results.loc[[df_results.loc[df_results['Item'] == i, 'MAPE'].idxmin()]])
    ###Generating new df with fcast dates and empty values

    df1_f1 = df_w_fcast(df1, input_forecast_period,items)


    #Populating df1_f1 with all the future forecast values for all models

    #running Arima function
    df1_f1 = aarima_fcast(dfx, df1_f1, input_forecast_period, items)

    #runnning LR function
    df1_f1 = lr_rf_fcast_alt(df1, df1_f1, lr1_model_list, 'LR', input_forecast_period, items )

    #running RF function
    df1_f1 = lr_rf_fcast_alt(df1, df1_f1, rf_model_list, 'RF', input_forecast_period, items)

    #populating best future forecast as a column based on results
    df1_f1 = populate_best_fcast(df1_f1, df_results_best, items)

    #returning values
    return df_results, df_results_best, df1_f1

# Function to graph all forecasts with loop
def graph_fcast_all(df1_f1):
    items = df1_f1['Item'].unique()
    #Graphing all items
    for i in items:
        df1_f1_graph = df1_f1[df1_f1['Item'] == i] #to loop
        fig = px.line(df1_f1_graph, x=df1_f1_graph.index, y=['Qty', 'Future_Forecast_ARIMA', 'Future_Forecast_LR', 'Future_Forecast_RF'])

        fig.show()

# Function to graph forecast individually
def graph_fcast_individual(df1_f1, item):

    df1_f1_graph = df1_f1[df1_f1['Item'] == item]  # to loop
    fig = px.line(df1_f1_graph, x=df1_f1_graph.index, y=[
                  'Qty', 'Future_Forecast_ARIMA', 'Future_Forecast_LR', 'Future_Forecast_RF'])

    fig.show()

# Function for selecting best result based on df_results_best
def populate_best_fcast(df1_f1, df_results_best, items):
    for i in items:

        best_idx = df1_f1['Item'] == i

        if df_results_best.loc[df_results_best['Item'] == i]['Model'].values == 'LR_Multistep':
            df1_f1.loc[best_idx, 'Future_Forecast_BEST'] = df1_f1.loc[best_idx,
                                                                      'Future_Forecast_LR']

        elif df_results_best.loc[df_results_best['Item'] == i]['Model'].values == 'ARIMA':
            df1_f1.loc[best_idx, 'Future_Forecast_BEST'] = df1_f1.loc[best_idx,
                                                                      'Future_Forecast_ARIMA']

        elif df_results_best.loc[df_results_best['Item'] == i]['Model'].values == 'Random Forest':
            df1_f1.loc[best_idx, 'Future_Forecast_BEST'] = df1_f1.loc[best_idx,
                                                                      'Future_Forecast_RF']

    return df1_f1

# function to populate all the items prior to forecast start date with np.nan so they are excluded from plotly express graph
# note - run this function before the fill last value function
def fill_na_json(df1_f1, input_forecast_period):
    ##################
    items = df1_f1['Item'].unique()
    ##################

    temp = df1_f1[df1_f1['Item'] == items[0]].iloc[-input_forecast_period:]
    pre_fcast_idx = (df1_f1.index < temp.index[0])

    df1_f1.loc[pre_fcast_idx,
               'Future_Forecast_ARIMA':'Future_Forecast_BEST'] = np.nan

    return df1_f1

# function to populate grouped df prior to forecast start date with np.nan so they are excluded from plotly express graph
# note - run this function before the fill last value function
def fill_na_df(df1_f1, input_forecast_period):

    temp = df1_f1.iloc[-input_forecast_period:]
    pre_fcast_idx = (df1_f1.index < temp.index[0])

    df1_f1.loc[pre_fcast_idx, 'Future_Forecast_BEST':] = np.nan

    pre_fcast_idx = (df1_f1.index >= temp.index[0])

    df1_f1.loc[pre_fcast_idx, 'Qty'] = np.nan

    return df1_f1

# function to populate the last actual value into forecast values so that there is not break in graph when plotting historical and forecast data
# note - run this function only after all values pre-forecast value have been replaced with np.nan so they aren't picked up by graph
def fill_last_val(df1_f1, input_forecast_period):
    for i in df1_f1['Item'].unique():
        temp1 = df1_f1[df1_f1['Item'] ==
                       i].iloc[-input_forecast_period-1:].index[0]
        last_value_idx = (df1_f1['Item'] == i) & (df1_f1.index == temp1)
        df1_f1.loc[last_value_idx, 'Future_Forecast_ARIMA':
                   'Future_Forecast_BEST'] = df1_f1.loc[last_value_idx, 'Qty'].values[0]
    return df1_f1

# function to populate the grouped DF  last actual value into forecast values so that there is not break in graph when plotting historical and forecast data
# note - run this function only after all values pre-forecast value have been replaced with np.nan so they aren't picked up by graph
def fill_last_val_grp(df1_f1, input_forecast_period):

    temp1 = df1_f1.iloc[-input_forecast_period-1:].index[0]
    last_value_idx = (df1_f1.index == temp1)
    df1_f1.loc[last_value_idx,
               'Future_Forecast_BEST':] = df1_f1.loc[last_value_idx, 'Qty'].values[0]
    return df1_f1

def store_intermediate_data(request):
    print("in databse storage........")
    session = request.session

    file_data = session.get('file', [])

    print("file data........", file_data)
    uploaded_file = request.session.get("uploaded_file")

    if len(file_data) != 0:
        custData = CustomerData.objects.filter(customer=request.user, file_name=uploaded_file).first()
        custData.putframe(file_data, request.user, uploaded_file)    
