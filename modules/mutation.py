import random

def mutate(chromosome, rate=0.1):
    order = chromosome.order

    # 1. Mutate the Task Order (Swap)
    for i in range(len(order)):
        if random.random() < rate:
            j = random.randint(0, len(order)-1)
            order[i], order[j] = order[j], order[i]

    chromosome.order = order

    # 2. Mutate the Execution Modes (Randomly change strategy)
    for task_id in chromosome.modes:
        if random.random() < rate:
            # Randomly pick a new mode: 0 (Crash), 1 (Normal), or 2 (Relaxed)
            chromosome.modes[task_id] = random.choice([0, 1, 2])

    return chromosome