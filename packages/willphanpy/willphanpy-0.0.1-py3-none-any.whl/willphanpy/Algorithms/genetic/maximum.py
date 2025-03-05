from Genetic import Genetic

class Maximum(Genetic):
    def __init__(self, size, length, rate, generation):
        super().__init__(size, length, rate, generation)

    def mainFunc(self, chromosome):
        x = int(chromosome, 2)
        return x**2

    def fitness(self, population):
        best_individual = max(population, key=self.mainFunc)
        return best_individual, self.mainFunc(best_individual)

maximum = Maximum(10, 5, 0.01, 50)
maximum.genetic_algorithm()