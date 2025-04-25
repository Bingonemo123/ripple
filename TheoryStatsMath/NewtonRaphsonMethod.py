upper_increment = 1.3
lower_increment = 2
p = 0.62
q = 1 - p
upper_absorption_point = 10
lower_absorption_point = 0
starting_point = 5

def equation(x):
    return p *( x ** (upper_increment) ) + q * ( x ** ( -lower_increment )) - 1

def equation_derivative(x):
    return p * upper_increment * (x ** ( upper_increment - 1)) + q * ( -lower_increment ) * x ** ( -lower_increment - 1)

def newton_raphson(guess, epsilon=1e-50, max_iterations=100):
    x = guess
    iteration = 0

    while abs(equation(x)) > epsilon and iteration < max_iterations:
        x = x - equation(x) / equation_derivative(x)
        iteration += 1

    return x

# Initial guess for x
initial_guess = 0.5

# Solve the equation
solution = newton_raphson(initial_guess)

print("Approximate solution for x:", solution)

print(equation(solution))

C_2 = 1/( (solution ** upper_absorption_point) - (solution ** lower_absorption_point))
C_1 = ( solution ** lower_absorption_point )/((solution ** lower_absorption_point) - (solution ** upper_absorption_point))

prob = C_2 * (solution ** (starting_point)) + C_1

print(prob)


