"""
Module implementing a Genetic Algorithm for optimization.
This module provides the `GeneticAlgorithm` class, which implements a genetic algorithm for solving optimization problems. The genetic algorithm evolves a population of binary-encoded individuals over multiple generations using selection, crossover, and mutation operators to optimize a given fitness function.
Classes
GeneticAlgorithm
    Class that implements the genetic algorithm for optimization.
Notes
-----
The genetic algorithm is a population-based search algorithm inspired by the principles of natural selection and genetics. It is particularly useful for solving complex optimization problems where the search space is large and traditional gradient-based methods are not applicable.
The `GeneticAlgorithm` class in this module allows customization of various parameters such as population size, number of generations, crossover probability, mutation probability, and selection strategy. It also supports user-defined fitness functions to evaluate the fitness of individuals in the population.
"""

import numpy as np
import random


class GeneticAlgorithm:
    """
    Implements a Genetic Algorithm for optimization.

    Parameters
    ----------
    populationSize : int
        Number of individuals in the population.
    numBitsPerIndividual : int
        Number of bits representing each individual.
    numGenerations : int
        Number of generations to execute.
    crossoverProbability : float
        Probability of crossover between individuals.
    mutationProbability : float
        Probability of mutation for each bit in the individuals.
    numParents : int
        Number of parents selected in each generation.
    fitnessFunction : callable
        Function to compute the fitness of an individual.
    tolerance : float
        Tolerance value to stop the algorithm if reached.
    numCompetitors : int, optional
        Number of competitors in the tournament selection (default is 2).

    Attributes
    ----------
    population : ndarray
        Matrix representing the current population.
    populationFitness : ndarray
        Fitness values computed for the population's individuals.
    parents : ndarray
        Matrix of selected parents in each generation.
    bikes : list
        List of `bike` objects containing the physical properties of vehicles.
    elites : ndarray
        Elite individuals stored across generations.
    maxValues : list
        Maximum fitness values per generation.
    averageValues : list
        Average fitness values per generation.
    minValues : list
        Minimum fitness values per generation.
    """

    def __init__(
        self,
        populationSize,
        numBitsPerIndividual,
        numGenerations,
        crossoverProbability,
        mutationProbability,
        numParents,
        fitnessFunction,
        tolerance,
        numCompetitors=2,
    ):

        np.random.seed(42)
        random.seed(42)

        self.numBitsPerIndividual = numBitsPerIndividual
        self.numParents = numParents
        self.populationSize = populationSize
        self.crossoverProbability = crossoverProbability
        self.mutationProbability = mutationProbability
        self.numGenerations = numGenerations
        self.numCompetitors = numCompetitors

        self.population = np.random.randint(
            0, 2, (self.populationSize, self.numBitsPerIndividual)
        )
        self.populationFitness = np.zeros(self.populationSize)
        self.parents = np.zeros((self.numParents, self.numBitsPerIndividual))
        self.bikes = []

        self.fitnessFunction = fitnessFunction

        self.elites = np.zeros((self.numGenerations, self.numBitsPerIndividual))
        self.maxValues = []
        self.averageValues = []
        self.minValues = []

        self.tolerance = tolerance

    def bike2array(self, i, bike):
        """
        Converts the properties of a `bike` object into a binary representation.

        Parameters
        ----------
        i : int
            Index of the individual in the population.
        bike : object
            `Bike` object with physical properties to convert.
        """
        chrom = []
        scale = 10
        nbit = self.numBitsPerIndividual

        chrom.append(np.binary_repr(int(self.bikes[i].wheel_1_x * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].wheel_1_y * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].wheel_1_radius * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].wheel_1_mass * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].wheel_1_torque * scale), nbit))

        chrom.append(np.binary_repr(int(self.bikes[i].wheel_2_x * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].wheel_2_y * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].wheel_2_radius * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].wheel_2_mass * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].wheel_2_torque * scale), nbit))

        chrom.append(np.binary_repr(int(self.bikes[i].body_1_x * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].body_1_y * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].body_1_mass * scale), nbit))

        chrom.append(np.binary_repr(int(self.bikes[i].body_2_x * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].body_2_y * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].body_2_mass * scale), nbit))

        chrom.append(np.binary_repr(int(self.bikes[i].k_spring_w1_w2 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].k_spring_w1_b1 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].k_spring_w1_b2 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].k_spring_w2_b1 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].k_spring_w2_b2 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].k_spring_b1_b2 * scale), nbit))

        chrom.append(np.binary_repr(int(self.bikes[i].loss_spring_w1_w2 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].loss_spring_w1_b1 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].loss_spring_w1_b2 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].loss_spring_w2_b1 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].loss_spring_w2_b2 * scale), nbit))
        chrom.append(np.binary_repr(int(self.bikes[i].loss_spring_b1_b2 * scale), nbit))

        self.population[i] = chrom

    def binarytobike(self, chrom):
        """
        Converts a binary chromosome into a scaled decimal representation.

        Parameters
        ----------
        chrom : ndarray
            Binary chromosome to convert.

        Returns
        -------
        list
            Decimal values of the `bike` physical properties.
        """
        scale = 10
        deci = []
        for binary in chrom:
            decimal = int(str(binary), 2)
            deci.append(decimal / scale)
        return deci

    def fit(self):
        """
        Runs the Genetic Algorithm, including selection, crossover, and mutation,
        until the number of generations is reached or the tolerance is met.
        """

        print("Initial population:")
        print(self.population)

        self.calculateFitness()
        print("Initial fitness:")
        print(self.populationFitness)

        for i in range(self.numGenerations):
            print(f"\nGeneration {i + 1}:")

            self.elites[i] = self.population[np.argmax(self.populationFitness)].copy()
            print("Elites:")
            print(self.elites[i])

            self.selection()
            print("Selected Parents:")
            print(self.parents)

            self.crossover()
            print("Population after crossing:")
            print(self.population)

            self.mutation()
            print("Population after mutation:")
            print(self.population)
            # Update fitness
            self.population[np.argmin(self.populationFitness)] = self.elites[i].copy()

            self.calculateStatistics()
            self.calculateFitness()
            print("Generation Fitness:")
            print(self.populationFitness)

            if self.tolerance < self.maxValues[-1]:
                print("Last iteration", i)
                self.elites[i] = self.population[np.argmax(self.populationFitness)]
                break

    def calculateFitness(self):
        for i in range(self.populationSize):
            self.populationFitness[i] = self.fitnessFunction(self, self.population[i])

    def selection(self):
        """
        Selects parents using a tournament selection mechanism.
        """
        for i in range(self.numParents):
            competitorIndices = np.random.randint(
                0, len(self.populationFitness), (self.numCompetitors, 1)
            )
            winnerIndex = np.argmax(self.populationFitness[competitorIndices])
            self.parents[i] = self.population[competitorIndices[winnerIndex]].copy()

    def crossover(self):
        """
        Performs crossover between the selected parents to generate offspring.
        """
        for i in range(self.populationSize // 2):
            parent1 = self.parents[random.randint(0, len(self.parents)) - 1].copy()
            parent2 = self.parents[random.randint(0, len(self.parents)) - 1].copy()

            if random.random() < self.crossoverProbability:
                offspring = self._cross(parent1, parent2)
            else:
                offspring = (parent1, parent2)

            self.population[2 * i] = offspring[0]
            self.population[2 * i + 1] = offspring[1]

    def _cross(self, parent1, parent2):
        """
        Performs a single-point crossover between two parents.

        Parameters
        ----------
        parent1 : ndarray
            The first parent.
        parent2 : ndarray
            The second parent.

        Returns
        -------
        tuple of ndarray
            Two offspring resulting from the crossover.
        """
        crossoverPoint = random.randint(0, self.numBitsPerIndividual)
        offspring1 = np.concatenate(
            (parent1[:crossoverPoint], parent2[crossoverPoint:]), axis=None
        )
        offspring2 = np.concatenate(
            (parent2[:crossoverPoint], parent1[crossoverPoint:]), axis=None
        )
        return (offspring1, offspring2)

    def mutation(self):
        """
        Applies random mutations to the population's individuals based on the defined mutation probability.
        """
        for i in range(self.populationSize):
            for j in range(self.numBitsPerIndividual):
                if random.random() < self.mutationProbability:
                    self.population[i][j] = (
                        self.population[i][j] ^ 1
                    )  # XOR operator: 1^1 = 0, 0^1 = 1

    def getElites(self):
        """
        Retrieves the stored elite individuals.

        Returns
        -------
        ndarray
            Array of elite individuals.
        """
        return self.elites

    def calculateStatistics(self):
        """
        Computes statistics of the population, including maximum, minimum,
        and average fitness values.
        """
        self.maxValues.append(max(self.populationFitness))
        print(self.maxValues[-1])
        self.averageValues.append(np.average(self.populationFitness))
        self.minValues.append(min(self.populationFitness))

    def getStatistics(self):
        """
        Returns the population statistics.

        Returns
        -------
        tuple of list
            Maximum, average, and minimum fitness values per generation.
        """
        return self.maxValues, self.averageValues, self.minValues
