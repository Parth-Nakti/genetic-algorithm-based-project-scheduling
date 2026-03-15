def check_dependency_violations(chromosome):
    violations = 0
    pos = {task["id"]: i for i, task in enumerate(chromosome.order)}
    for i, task in enumerate(chromosome.order):
        for dep_id in task["dependencies"]:
            if pos.get(dep_id, 0) > i:
                violations += 1
    return violations

def calculate_metrics(chromosome):
    finish_times = {}
    total_cost = 0
    total_risk = 0

    for task in chromosome.order:
        start = max([finish_times.get(d, 0) for d in task["dependencies"]] or [0])
        finish = start + task["duration"]
        finish_times[task["id"]] = finish
        total_cost += task["cost"]
        total_risk += task["risk"]

    chromosome.duration = max(finish_times.values()) if finish_times else 0
    chromosome.cost = total_cost
    chromosome.risk = total_risk

def fitness_function(chromosome, deadline=15): 
    calculate_metrics(chromosome)
    
    time_weight, cost_weight, risk_weight = 0.5, 0.3, 0.2
    
    score = (time_weight * chromosome.duration +
             cost_weight * (chromosome.cost / 1000) + 
             risk_weight * chromosome.risk)

    dep_violations = check_dependency_violations(chromosome)
    dep_penalty = dep_violations * 10000 

    deadline_penalty = 0
    if chromosome.duration > deadline:
        deadline_penalty = (chromosome.duration - deadline) * 5000

    chromosome.fitness = 1 / (1 + score + dep_penalty + deadline_penalty)
    return chromosome.fitness