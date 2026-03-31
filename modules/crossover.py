import random
from modules.chromosome import Chromosome

def crossover(parent1, parent2):
    size = len(parent1.order)
    point = random.randint(1, size-1)

    # 1. Crossover the Task Order
    first = parent1.order[:point]
    second = [t for t in parent2.order if t not in first]
    child_order = first + second
    
    # 2. Crossover the Execution Modes
    child_modes = {}
    for t in child_order:
        tid = t["id"]
        # 50% chance to inherit mode from Parent 1, 50% from Parent 2
        if random.random() < 0.5:
            child_modes[tid] = parent1.modes[tid]
        else:
            child_modes[tid] = parent2.modes[tid]

    # Create the new child with both order and modes
    child = Chromosome(parent1.tasks, order=child_order, modes=child_modes)
    return child