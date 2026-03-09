from modules.chromosome import Chromosome

def create_population(tasks,size):

    population=[]

    for _ in range(size):
        population.append(Chromosome(tasks))

    return population