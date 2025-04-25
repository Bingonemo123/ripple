import time
import random
import numpy as np


def geometric_time_limit(starting_point, upper_boundary,
                         lower_boundary, m, k, rtime):
    up = 0
    down = 0
    st = time.time()
    while time.time() - st < rtime:
        current_position = starting_point
        while (current_position < upper_boundary and
               current_position >= lower_boundary):
            d = random.choice([True, False])
            if d:
                current_position = m*current_position
            else:
                current_position = k*current_position

        if current_position >= upper_boundary:
            up += 1
        else:
            down += 1

    return up, down, up/(up + down)

     
# print(brownian_time_limit(100, 200, 1, 1.3, 0.5, 100))

def asymetric_random_walk_time_limit(starting_point, upper_boundary,
                                     lower_boundary, incriment, decrement, p,
                                     rtime):
    up = 0
    down = 0
    st = time.time()
    while time.time() - st < rtime:
        current_position = starting_point
        while (current_position < upper_boundary and
               current_position > lower_boundary):
            if random.random() <= p:
                current_position += incriment
            else:
                current_position -= decrement

        if current_position >= upper_boundary:
            up += 1
        else:
            down += 1

    return up, down, up + down, up/(up + down)


def asymetric_random_walk_run_limit(starting_point, upper_boundary,
                                    lower_boundary,
                                    incriment, decrement, p, lruns):
    '''assymetric discrete one-dimentional random walk with upper and lower
      absorbing barriers'''
    up = 0
    down = 0
    runs = 0
    while runs < lruns:
        current_position = starting_point
        while (current_position < upper_boundary and
               current_position > lower_boundary):
            if random.random() <= p:
                current_position += incriment
            else:
                current_position -= decrement

        if current_position >= upper_boundary:
            up += 1
        else:
            down += 1

        runs += 1

    return up, down, up + down, up/(up + down)


def asymetric_random_walk_precision_limit(s: float, U: float, 
                                          L: float, i: float, 
                                          d: float, p: float, 
                                          precs: int):
    """
   Running random walk simulation until percentage is in specific precision.

   :param float s: starting point
   :param float U: Upper limit
   :param float L: Lowe limit
   :param float i: increament step size
   :param float d: decriment step size
   :param float p: probability of increament
   :param int: precs: precision to stop after floating point
   """
    upper_barrier_hits = 0
    lower_barrier_hits = 0
    percentage = 0
    while True:
        current_position = s
        while True:
            current_position += np.random.choice([i, -d], p=[p, 1-p])

            if current_position >= U:
                upper_barrier_hits += 1
                break
            elif current_position <= L:
                lower_barrier_hits += 1
                break
        if abs((upper_barrier_hits/(upper_barrier_hits + lower_barrier_hits)) - percentage) > 10**(-precs):
            break
        percentage = upper_barrier_hits / lower_barrier_hits if lower_barrier_hits else 0
        print(percentage)
    return percentage


def test():
    print('Telegraph')
