import numpy as np
import pmdarima as pm

# setting ARIMA m value
m_arima_set = 12

# AUTO ARIMA ALL IN ONE FUNCTION
def model2_auto_arima(df, horizon, items):
    Ntest = horizon

    # Full Code with loop

    for i in items:

        train = df[df['Item'] == i].iloc[:-Ntest]  # to loop
        test = df[df['Item'] == i].iloc[-Ntest:]  # to loop

        model_aarima = pm.auto_arima(train['Qty'],
                                     trace=True,  # shows which models tested out
                                     suppress_warnings=True, seasonal=True, m=m_arima_set)  # --- Needs to link to user input; Need to figure out how to tune this

        # test prediction
        test_pred, confint = model_aarima.predict(
            n_periods=Ntest, return_conf_int=True)

        train = df[df['Item'] == i].iloc[:-Ntest]  # to loop
        test = df[df['Item'] == i].iloc[-Ntest:]  # to loop

        train_idx = (df['Item'] == i) & (
            df.index <= train.index[-1])  # to loop
        test_idx = (df['Item'] == i) & (df.index > train.index[-1])  # to loop

        df.loc[test_idx, 'AARIMA'] = test_pred

    return df, model_aarima

    # # Calculating and storing scores
    # df_results = df_results.append(store_scores(df, 'Forecast','ARIMA'))

    # return df_results
