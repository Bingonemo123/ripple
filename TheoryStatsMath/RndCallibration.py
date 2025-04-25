import random
import time


st = time.time()
up = 0
down = 0
while time.time() - st < 10:
    if random.random() <= 0.62:
        up += 1
    else:
        down += 1

print(up, down, up/(up + down))
