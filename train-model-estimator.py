import tensorflow as tf
import matplotlib.pyplot as plt
import pandas as pd
import csv

def learn_estimator_model(x, y):
    def input_fn():
        features = {'x': x}
        labels = y
        return features, labels

    xfc = tf.feature_column.numeric_column('x')
    estimator = tf.estimator.LinearRegressor(feature_columns=[xfc])
    estimator.train(input_fn=input_fn, steps=150000)

    w = estimator.get_variable_value('linear/linear_model/x/weights')[0][0]
    b = estimator.get_variable_value('linear/linear_model/bias_weights')[0]

    print(estimator.latest_checkpoint())

    predictions = x * w + b
    print("Weight =", w, "bias =", b, '\n')

    write_weights_to_csv(w, b)
    # Plotting the Results
    plt.plot(x, y, 'ro', label='Original data')
    plt.plot(x, predictions, label='Fitted line')
    plt.title('Linear Regression Result')
    plt.legend()
    plt.show()

def test_graph(x,y):
    predictions = x*0.33848 - 90.2134
    plt.plot(x, y, 'ro', label='Original data')
    plt.plot(x, predictions, label='Fitted line')
    plt.title('Linear Regression Result')
    plt.legend()
    plt.show()

def write_weights_to_csv(w, b):
    with open('weights.csv', 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow((w, b))
        print("Done CSV write")

if __name__ == "__main__":
    df = pd.read_csv("ratio_data.csv", delimiter=',', header=None)
    learn_estimator_model(df[0].values, df[1].values)
    # test_graph(df[0].values, df[1].values)
