import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def measure_real_length(start_row, end_row, w, b, real_car_length):
    distance = (real_car_length/w)*(np.log(w*end_row+b)-np.log(w*start_row+b))
    return distance


CAR_LENGTH = 350  # median real world length of a car in centimeters

df = pd.read_csv("weights.csv", delimiter=',', header=None)
w = float(df[0].values)
b = float(df[1].values)
print(w, b)
Row = np.array(list(range(260, 700)))
Ratio = CAR_LENGTH/(w*Row + b)

print(measure_real_length(300,320,w,b,CAR_LENGTH))

plt.plot(Row, Ratio, label='Fitted line')
plt.title('Actual distance variation over pixel position')
plt.ylabel('centimeters per pixel')
plt.xlabel('Row number of a frame')
plt.legend()
plt.show()


