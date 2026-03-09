from modules.population import create_population
from modules.fitness import fitness_function
from modules.selection import tournament_selection
from modules.crossover import crossover
from modules.mutation import mutate

def run_ga(tasks, population_size=30, generations=50, deadline=15):
    # Added 'deadline' to the arguments above ^
    
    population = create_population(tasks, population_size)

    for gen in range(generations):
        # 1. Calculate fitness (Passing the deadline to the fitness function)
        for p in population:
            fitness_function(p, deadline)

        # 2. Elitism: Sort by fitness (highest first)
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Carry over the top 2 best solutions
        new_population = [population[0], population[1]]

        # 3. Fill the rest of the population
        while len(new_population) < population_size:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)

            child = crossover(parent1, parent2)
            child = mutate(child)

            # Evaluate the child with the deadline
            fitness_function(child, deadline)

            new_population.append(child)

        population = new_population
        best = population[0]
        
        # Status check for the print statement
        status = "ON TRACK" if best.duration <= deadline else "OVERDUE"
        
        print(f"Gen {gen} | Duration: {best.duration}d | {status} | Fitness: {best.fitness:.6f}")

    return population[0]