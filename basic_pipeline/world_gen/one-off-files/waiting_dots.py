# This code comes from the post below. It creates a waiting dot sequence in the terminal
# https://stackoverflow.com/questions/59905393/make-an-animated-waiting-dot-sequence-in-python-terminal

# itertools is a collection of tools that handle iterators in python
# TODO look into iterators in Python more.
from itertools import cycle
from time import sleep
n_points = 4
points_l = [ '.' * i + ' ' * (n_points - i) + '\r' for i in range(n_points) ]
cond = True

for points in cycle(points_l):
    print(points, end='')
    sleep(0.25)
    if not cond:
        break