import numpy

x_start, x_stop = 3, 5
y_start, y_stop = 1, 999999


a = (x_start <= y_stop) and (x_stop >= y_start)
print(a)
