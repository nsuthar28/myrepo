import numpy as np
import pandas as pd

from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_percentage_error, mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression

from sklearn.ensemble import RandomForestRegressor

# defining how many past periods to use to in LR and RF models to predict next Y value
T = 12

# Defining function for Model 3 LR and RF
def model3_lrrf(df, horizon, items):
    # FULL LOOP TEST 1 - LR & RF

    df1 = pd.DataFrame(columns=['Item', 'Qty', 'LR_1step_train', 'LR_1step_test', 'LR_multistep', 'LR_multioutput',
                       'RF_1step_train',  'RF_1step_test', 'RF_multistep_test'])  # empty dataframe to append to in loop

    horizon = int(np.floor(len(df.index.unique())*.2))

    Ntest = horizon
    # creating emply lists to store models by item
    lr1_model_list = []
    rf_model_list = []

    for i in items:
        df_temp = df[df['Item'] == i]  # to loop

        train = df_temp.iloc[:-Ntest]
        test = df_temp.iloc[-Ntest:]
        # Make supervised dataset
        # use T past values to predict the next value

        series = df_temp['Qty'].to_numpy()

        # T = T #to adjust based on input - Weekly
        X = []
        Y = []
        for t in range(len(series) - T):
            x = series[t:t+T]
            X.append(x)
            y = series[t+T]
            Y.append(y)

        X = np.array(X).reshape(-1, T)
        Y = np.array(Y)
        N = len(X)
        print("X.shape", X.shape, "Y.shape", Y.shape)
        Xtrain, Ytrain = X[:-Ntest], Y[:-Ntest]
        Xtest, Ytest = X[-Ntest:], Y[-Ntest:]
        lr1 = LinearRegression()
        lr1.fit(Xtrain, Ytrain)
        lr1.score(Xtrain, Ytrain)
        lr1.score(Xtest, Ytest)

        lr1_model_list.append(lr1)  # storing lr1 models into list
        # Boolean index
        train_idx = df_temp.index <= train.index[-1]
        test_idx = ~train_idx

        train_idx[:T] = False  # first T values are not predictable
        # 1-step forecast
        df_temp.loc[train_idx, 'LR_1step_train'] = lr1.predict(Xtrain)
        df_temp.loc[test_idx, 'LR_1step_test'] = lr1.predict(Xtest)
        # plot 1-step forecast
        # df_temp[['Qty', 'LR_1step_train', 'LR_1step_test']].plot(figsize=(15, 5));
        # multi-step forecast
        multistep_predictions = []

        # first test input
        last_x = Xtest[0]

        while len(multistep_predictions) < Ntest:
            p = lr1.predict(last_x.reshape(1, -1))[0]

            # update the predictions list
            multistep_predictions.append(p)

            # make the new input
            last_x = np.roll(last_x, -1)
            last_x[-1] = p
        # save multi-step forecast to dataframe
        df_temp.loc[test_idx, 'LR_multistep'] = multistep_predictions
        # plot 1-step and multi-step forecast
        # df_temp[['Qty', 'LR_multistep', 'LR_1step_test']].plot(figsize=(15, 5));
        # make multi-output supervised dataset
        Tx = T
        Ty = Ntest
        X = []
        Y = []
        for t in range(len(series) - Tx - Ty + 1):
            x = series[t:t+Tx]
            X.append(x)
            y = series[t+Tx:t+Tx+Ty]
            Y.append(y)
        X = np.array(X).reshape(-1, Tx)
        Y = np.array(Y).reshape(-1, Ty)
        N = len(X)
        print("X.shape", X.shape, "Y.shape", Y.shape)
        Xtrain_m, Ytrain_m = X[:-1], Y[:-1]
        Xtest_m, Ytest_m = X[-1:], Y[-1:]
        lr2 = LinearRegression()
        lr2.fit(Xtrain_m, Ytrain_m)
        lr2.score(Xtrain_m, Ytrain_m)
        r2_score(lr2.predict(Xtest_m).flatten(), Ytest_m.flatten())
        # save multi-output forecast to dataframe
        df_temp.loc[test_idx, 'LR_multioutput'] = lr2.predict(
            Xtest_m).flatten()
        # plot all forecasts
        # cols = ['Qty', 'LR_multistep', 'LR_1step_test', 'LR_multioutput']
        # df_temp[cols].plot(figsize=(15, 5));
        # MAPE
        mape1 = mean_absolute_percentage_error(Ytest, multistep_predictions)
        print("multi-step MAPE:", mape1)
        mape2 = mean_absolute_percentage_error(
            Ytest, df_temp.loc[test_idx, 'LR_multioutput'])
        print("multi-output MAPE:", mape2)

        # random forest
        model_rf = RandomForestRegressor()  # can change different models
        name = 'RF'  # can change the name

        model_rf.fit(Xtrain, Ytrain)
        print("One-step forecast:", name)
        # print("Train R^2:", model_rf.score(Xtrain, Ytrain))
        # print("Test R^2 (1-step):", model_rf.score(Xtest, Ytest))

        rf_model_list.append(model_rf)
        # store 1-step forecast
        df_temp.loc[train_idx,
                    f'{name}_1step_train'] = model_rf.predict(Xtrain)
        df_temp.loc[test_idx, f'{name}_1step_test'] = model_rf.predict(Xtest)

        # generate multi-step forecast
        multistep_predictions = []

        # first test input
        last_x = Xtest[0]

        while len(multistep_predictions) < Ntest:
            p = model_rf.predict(last_x.reshape(1, -1))[0]

            # update the predictions list
            multistep_predictions.append(p)

            # make the new input
            last_x = np.roll(last_x, -1)
            last_x[-1] = p

        # store multi-step forecast
        df_temp.loc[test_idx, f'{name}_multistep_test'] = multistep_predictions

        # MAPE of multi-step forecast
        mape = mean_absolute_percentage_error(Ytest, multistep_predictions)
        print("Test MAPE (multi-step):", mape)

        # plot 1-step and multi-step forecast
        # cols = [
        # 'Qty',
        # f'{name}_1step_train',
        # f'{name}_1step_test',
        # f'{name}_multistep_test'
        # ]
        # df_temp[cols].plot(figsize=(15, 5));
        df1 = df1.append(df_temp)

    df1 = df1.sort_index()
    # return df1, lr1, lr2, model_rf
    return df1, lr1_model_list, rf_model_list
