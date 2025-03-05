from Genetic import Genetic

class Knapsack(Genetic):
    def __init__(self, size, length, rate, generation, value, weight, limit):
        super().__init__(size, length, rate, generation)
        self.__value = value
        self.__weight = weight
        self.__limit = limit

    def mainFunc(self, chromosome):
        value = 0
        for i in range(len(chromosome)):
            value += int(chromosome[i]) * self.__value[i]
        return value

    def calculateWeight(self, chromosome):
        weight = 0
        for i in range(len(chromosome)):
            weight += int(chromosome[i]) * self.__weight[i]
        return weight

    def fitness(self, population):
        best_individual = max(population, key = self.mainFunc)
        value = self.mainFunc(best_individual)
        weight = self.calculateWeight(best_individual)
        
        item = []
        for i in range(len(best_individual)):
            if(int(best_individual[i])):
                item.append(i)

        if(weight <= self.__limit):
            return best_individual, ["Item: " + str(item), "Value: " + str(value), "Weight: " + str(weight)]

        return False, False
        

knapsack = Knapsack(10, 6, 0.5, 100, [
    8, 10, 20, 40, 12, 15
], [
    5, 10, 15, 20, 25, 30
], 45)
knapsack.genetic_algorithm()