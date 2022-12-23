import pmdarima as pm

# setting ARIMA m value
m_arima_set = 12

# Function for forecasting with Auto Arima
def aarima_fcast(df, df1_f1, input_forecast_period, items):
    # Forecasting Future N periods with Auto Arima
    # Looping through all items

    for i in items:

        # train = df[df['Item'] == i].iloc[:-Ntest] #to loop
        train = df[df['Item'] == i]  # to loop
        # test = df[df['Item'] == i].iloc[-Ntest:] #to loop

        model_aarima = pm.auto_arima(train['Qty'],
                                     trace=True,  # shows which models tested out
                                     suppress_warnings=True, seasonal=True, m=m_arima_set)  # --- Needs to link to user input; Need to figure out how to tune this

        # test prediction
        test_pred, confint = model_aarima.predict(
            n_periods=input_forecast_period, return_conf_int=True)  # User inputer - Forecast n periods
        print(df.index[-1])
        print("------------------------")
        print(df1_f1.index)
        try:
            fcast_idx = (df1_f1['Item'] == i) & (
                df1_f1.index > df.index[-1])  # to loop
            df1_f1.loc[fcast_idx, 'Future_Forecast_ARIMA'] = test_pred
        except Exception as E:
            print(E)
    return df1_f1
