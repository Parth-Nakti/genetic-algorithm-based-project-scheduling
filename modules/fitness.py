import math

def check_dependency_violations(chromosome):
    """Checks if tasks are scheduled in an order that violates their dependencies."""
    violations = 0
    # Create a map of task_id to its position in the current chromosome order
    pos = {task["id"]: i for i, task in enumerate(chromosome.order)}
    
    for i, task in enumerate(chromosome.order):
        for dep_id in task["dependencies"]:
            # If a dependency is scheduled AFTER the current task, it's a violation
            if pos.get(dep_id, 999) > i:
                violations += 1
    return violations

def calculate_metrics(chromosome):
    """Calculates duration, cost, and risk based on task modes and order."""
    finish_times = {}
    total_base_cost = 0
    total_risk = 0

    for task in chromosome.order:
        # 1. Get Mode (0=Crash, 1=Normal, 2=Relaxed)
        mode = chromosome.modes.get(task["id"], 1)
        
        # 2. Apply Mode Multipliers
        if mode == 0: # Crash: 50% Time, 200% Cost
            dur_mult, cost_mult = 0.5, 2.0  
        elif mode == 2: # Relaxed: 130% Time, 80% Cost
            dur_mult, cost_mult = 1.3, 0.8
        else: # Normal
            dur_mult, cost_mult = 1.0, 1.0
            
        actual_duration = task["duration"] * dur_mult
        actual_cost = task["cost"] * cost_mult

        # 3. Handle Start Times & Dependencies (The Brick Wall)
        dep_finish_times = [finish_times[d] for d in task["dependencies"] if d in finish_times]
        
        # If any dependencies are missing from finish_times, it's out of order
        if len(dep_finish_times) < len(task["dependencies"]):
            start = 999 
        else:
            start = max(dep_finish_times) if dep_finish_times else 0
            
        finish = start + actual_duration
        finish_times[task["id"]] = finish
        total_base_cost += actual_cost
        total_risk += task["risk"]

    chromosome.duration = max(finish_times.values()) if finish_times else 0
    chromosome.cost = total_base_cost
    chromosome.risk = total_risk

def fitness_function(chromosome, deadline=30, budget=40000, overhead=400): 
    """Main objective function for the GA."""
    calculate_metrics(chromosome)
    
    # 1. Calculate Grand Total (Base + Dynamic Overhead)
    # The 'overhead' parameter is now passed from the UI
    grand_total_cost = chromosome.cost + (chromosome.duration * overhead)
    
    # 2. Hard Penalties (Dependency violations must be zero)
    dep_violations = check_dependency_violations(chromosome)
    dep_penalty = dep_violations * 100000 
    
    # 3. Soft Penalties (Constraint violations)
    time_penalty = 0
    if chromosome.duration > deadline:
        time_penalty = (chromosome.duration - deadline) * 10000
        
    budget_penalty = 0
    if grand_total_cost > budget:
        budget_penalty = (grand_total_cost - budget) * 5000

    # 4. Optimization Score (The goal is to minimize this)
    # Lower duration and lower cost = higher fitness
    score = (chromosome.duration * 5) + (grand_total_cost / 100)
    
    # 5. Fitness Formula
    chromosome.fitness = 1 / (1 + score + dep_penalty + time_penalty + budget_penalty)
    return chromosome.fitness