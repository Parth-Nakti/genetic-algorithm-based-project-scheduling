import random

class Chromosome:
    def __init__(self, tasks, order=None, modes=None):
        self.tasks = tasks
        
        # 1. Initialize Order
        if order is None:
            self.order = tasks.copy()
            random.shuffle(self.order)
        else:
            self.order = order
            
        # 2. Initialize Execution Modes (0=Crash, 1=Normal, 2=Relaxed)
        if modes is None:
            self.modes = {task["id"]: random.choice([0, 1, 2]) for task in self.order}
        else:
            self.modes = modes
            
        self.duration = 0
        self.cost = 0
        self.risk = 0
        self.fitness = 0