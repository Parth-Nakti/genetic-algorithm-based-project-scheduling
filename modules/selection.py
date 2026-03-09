import random

def tournament_selection(population):

    a=random.choice(population)
    b=random.choice(population)

    return a if a.fitness>b.fitness else b