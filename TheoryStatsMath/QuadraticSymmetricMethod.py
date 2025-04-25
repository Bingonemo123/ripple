upper_increment = lower_increment = 1 # includes that this is one
p = 0.6
q = 1 - p
upper_absorption_point = 3
lower_absorption_point = 0
starting_point = 1


r_1 = (1  +  ( 1 - 4 * p * q) ** 0.5 )/ 2 * p
r_2 = (1  -  ( 1 - 4 * p * q) ** 0.5 )/ 2 * p

### using r_1 

C_2 = 1/( (r_1 ** upper_absorption_point) - (r_1 ** lower_absorption_point))
C_1 = ( r_1 ** lower_absorption_point )/((r_1 ** lower_absorption_point) - (r_1 ** upper_absorption_point))
prob = C_2 * (r_1 ** (starting_point)) + C_1

print("solution for r_1:", r_1)
print("solution for C2 and C1:", C_2, C_1)
print("prob:", prob)

### using r_2

C_2 = 1/( (r_2 ** upper_absorption_point) - (r_2 ** lower_absorption_point))
C_1 = ( r_2 ** lower_absorption_point )/((r_2 ** lower_absorption_point) - (r_2 ** upper_absorption_point))
prob = C_2 * (r_2 ** (starting_point)) + C_1

print("solution for r_1:", r_2)
print("solution for C2 and C1:", C_2, C_1)
print("prob:", prob)

