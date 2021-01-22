import random, multiprocessing
import torch.multiprocessing as mp

from beyondGD.neural.ga import mutate, cross, elitism

from beyondGD.utils.types import IterableDataset

from beyondGD.utils import inverse_logistic


# prevent MAC OSX multiprocessing bug
# src: https://github.com/pytest-dev/pytest-flask/issues/104
multiprocessing.set_start_method("fork")


#
#
#  -------- evaluate_parallel -----------
#  !!! mutable object population !!!
#
def evaluate_parallel(
    population: dict,
    data_loader: IterableDataset,
):

    #
    #  -------- worker_eval -----------
    def worker_eval(entity):
        population[entity] = entity.evaluate(data_loader)

    #
    # --- begin method:

    processes: list = []

    for entity, _ in population.items():

        p = mp.Process(target=worker_eval, args=(entity,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    return None


#
#
#  -------- evaluate_linear -----------
#  !!! mutable object population !!!
#
def evaluate_linear(
    population: dict,
    data_loader: IterableDataset,
):

    for entity, _ in population.items():
        population[entity] = entity.evaluate(data_loader)

    return None


#
#
#  -------- process_linear -----------
#  !!! mutable object population !!!
def process_linear(
    population: dict,
    batch: list,
    selection_rate: int,
    mutation_rate: float,
    crossover_rate: int,
):

    # create empty new generation
    new_population: dict = {}

    # --- select by elite
    selection: dict = elitism(population, selection_rate)

    # --- fill new population with mutated, crossed entities
    for _ in range(len(population)):

        # get random players from selection
        rnd_entity, score = random.choice(
            list(selection.items())
        )

        # (optionally) cross random players
        if (
            crossover_rate > random.uniform(0, 1)
            and len(selection) > 1
        ):

            rnd_recessive, _ = random.choice(
                list(selection.items())
            )

            rnd_entity = cross(rnd_entity, rnd_recessive)

        # mutate random selected
        mut_entity, _ = mutate(rnd_entity, mutation_rate)

        # calculate score
        new_population[mut_entity] = mut_entity.accuracy(batch)

    return new_population