import random
random.seed(42) # This forces the "random" numbers to be the same every time you run it
from modules.population import create_population
from modules.fitness import fitness_function
from modules.selection import tournament_selection
from modules.crossover import crossover
from modules.mutation import mutate

def run_ga(tasks, population_size=50, generations=500, deadline=30, budget=25000, overhead=400):
    """
    Runs the Multi-Modal Genetic Algorithm with Time-Cost Trade-off.
    """
    # 1. Initialize the population
    population = create_population(tasks, population_size)

    for gen in range(generations):
        # 2. Evaluate fitness for everyone (Passes deadline, budget, and dynamic overhead)
        for p in population:
            fitness_function(p, deadline=deadline, budget=budget, overhead=overhead)

        # 3. Sort by fitness (Highest fitness first)
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        # 4. Elitism: Keep the top 2 best performers unchanged
        new_population = [population[0], population[1]]

        # 5. Breeding loop
        while len(new_population) < population_size:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)

            # Crossover (Inherits order and modes)
            child = crossover(parent1, parent2)
            
            # Mutation (Randomly swaps order OR flips task modes)
            child = mutate(child, rate=0.2) 

            # Calculate fitness for the new child with dynamic overhead
            fitness_function(child, deadline=deadline, budget=budget, overhead=overhead)

            new_population.append(child)

        population = new_population
        best = population[0]
        
        # Status logging for your terminal
        # Total cost check now uses the dynamic overhead variable
        current_total_cost = best.cost + (best.duration * overhead)
        status = "✅ CONSTRAINTS MET" if (best.duration <= deadline and 
                                         current_total_cost <= budget) else "❌ INFEASIBLE"
        
        if gen % 10 == 0: # Print every 10 generations to keep terminal clean
            print(f"Gen {gen} | Duration: {best.duration:.1f}d | Status: {status}")

    return population[0]