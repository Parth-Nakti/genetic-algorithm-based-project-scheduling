import random

class Chromosome:

    def __init__(self, tasks):
        self.tasks = tasks
        self.order = random.sample(tasks, len(tasks))
        self.fitness = None