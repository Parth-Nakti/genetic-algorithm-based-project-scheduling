import random
from modules.chromosome import Chromosome

def crossover(parent1,parent2):

    size=len(parent1.order)

    point=random.randint(1,size-1)

    child_tasks=parent1.tasks
    child=Chromosome(child_tasks)

    first=parent1.order[:point]

    second=[t for t in parent2.order if t not in first]

    child.order=first+second

    return child