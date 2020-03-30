import pickle
import pandas
import datetime


_ESTIMATOR_PATH = 'upstream_estimator.pickle'
_estimator = pickle.load(open(_ESTIMATOR_PATH, 'rb'))

_STOP_PERCENT = 1.007     # stop when price upper then buy_price * STOP_PERCENT
_STOP_TIME = 7 * 5 * 60   # stop if we reached STOP_TIME



def predict(price_history):
    price_history = list(price_history)[-2001:]
    df = pandas.DataFrame({'open': price_history})
    df = _process_df(df)
    predicted = _estimator.predict_proba(df.iloc[-1:])
    predicted_final = _predict_from_proba(predicted)
    utc_now = datetime.datetime.utcnow()
    return {
        'class_proba': predicted,
        'buy': predicted_final,
        'buy_price': price_history[-1],
        'stop_price': _STOP_PERCENT * price_history[-1],
        'stop_utc_time': utc_now + datetime.timedelta(seconds=_STOP_TIME),
        'utc_time': utc_now,
    }


def _process_df(df):

    price_column = 'open'
    normalize_columns = ['mean_10m', 'mean_15m', 'mean_20m', 'mean_40m', 'mean_80m', 'mean_160m']

    def mean(column, window):
        column = list(column)
        result = []
        for i in range(min(window, len(column))):
            result.append(column[i])
        for i in range(0, len(column) - window):
            result.append(sum(column[i:i+window])/window)
        return result

    df['mean_10m'] = mean(df['open'], 2)
    df['mean_15m'] = mean(df['open'], 8)
    df['mean_20m'] = mean(df['open'], 32)
    df['mean_40m'] = mean(df['open'], 120)
    df['mean_80m'] = mean(df['open'], 480)
    df['mean_160m'] = mean(df['open'], 2000)

    def normalize_column(price_column, normalize_column):
        result_column = []
        for p, n in zip(price_column, normalize_column):
            result_column.append((n / p - 1) * 100)
        return result_column

    for nc in normalize_columns:
        df[nc] = normalize_column(df[price_column], df[nc])

    return df[normalize_columns]


def _predict_from_proba(predicted, up_prob=0.64,straight_prob=0, downprob=0.17):
    predict_final = []
    print(predicted)
    for p in predicted:
        predict_final.append(p[3] > up_prob and p[0] < downprob and p[1]+p[2]>straight_prob)
    return predict_final
