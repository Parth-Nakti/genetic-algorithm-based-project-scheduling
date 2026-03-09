import random

def mutate(chromosome,rate=0.1):

    order=chromosome.order

    for i in range(len(order)):

        if random.random()<rate:

            j=random.randint(0,len(order)-1)

            order[i],order[j]=order[j],order[i]

    chromosome.order=order

    return chromosome