import random

class Genetic:
    def __init__(self, size, length, rate, generation):
        self.__populationSize = size
        self.__chromosomeLength = length
        self.__mutationRate = rate
        self.__generation = generation
    def mainFunc(self, chromosome):
        pass
    def fitness(self, population):
        pass

    # create population
    def __generate_population(self):
        return [''.join(random.choice('01') for _ in range(self.__chromosomeLength)) for _ in range(self.__populationSize)]
    
    # __selection
    def __selection(self, population):
        size = len(population)
        selected = random.choices(
            population, 
            weights=[self.mainFunc(ind) for ind in population], 
            k=size
        )
        return selected
    # __Crossover
    def __crossover(self, parent1, parent2):
        point = random.randint(1, self.__chromosomeLength - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    # Mutation
    def __mutate(self, chromosome):
        mutated = ''.join(
            bit if random.random() > self.__mutationRate else str(1 - int(bit))
            for bit in chromosome
        )
        return mutated

    # Genetic Algorithm
    def genetic_algorithm(self):
        population = self.__generate_population()
        best_individual_final = None
        fitness_final = None

        for generation in range(self.__generation):
            # __Selection
            population = self.__selection(population)
            
            # __Crossover
            new_population = []
            for i in range(0, self.__populationSize, 2):
                parent1, parent2 = population[i], population[i+1]
                child1, child2 = self.__crossover(parent1, parent2)
                new_population.append(self.__mutate(child1))
                new_population.append(self.__mutate(child2))
            
            population = new_population
            
            # Check best individual
            best_individual, fitness = self.fitness(population)
            if(best_individual):
                best_individual_final = best_individual
                fitness_final = fitness
            
            print(f"Generation {generation + 1}: Best = {best_individual_final}, Fitness = {fitness_final}")

        # Final solution
        best_individual, fitness = self.fitness(population)
        if(best_individual):
            best_individual_final = best_individual
            fitness_final = fitness

        print(f"Best solution: {best_individual_final}, result = {fitness_final}")
            

