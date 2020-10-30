from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import IterableDataset

from geneticNLP.data import batch_loader

from geneticNLP.neural.ga.swarm import optimize
from geneticNLP.neural.ga.utils import (
    evaluate_parallel,
    process_parallel,
)

#
#
#  -------- swarm -----------
#
def swarm(
    model: nn.Module,
    train_set: IterableDataset,
    dev_set: IterableDataset,
    noise_std: float = 0.1,
    learning_rate: float = 0.001,
    population_size: int = 80,
    selection_rate: float = 10,
    crossover_rate: float = 0.5,
    epoch_num: int = 200,
    report_rate: int = 10,
    batch_size: int = 32,
):
    # disable gradients
    torch.set_grad_enabled(False)

    # load dev set as batched loader
    dev_loader = batch_loader(
        dev_set,
        batch_size=batch_size,
    )

    # generate queen, swarm
    queen: nn.Module = model
    population: dict = {queen: queen.evaluate(dev_loader)}

    # --
    for epoch in range(1, epoch_num + 1):
        time_begin = datetime.now()

        # load train set as batched loader
        train_loader = batch_loader(
            train_set,
            batch_size=batch_size,
        )

        for batch in train_loader:

            # --- process generation
            population = process_parallel(
                population,
                batch,
                population_size=population_size,
                selection_rate=selection_rate,
                crossover_rate=crossover_rate,
            )

            # --- update queen model
            optimize(
                queen,
                population,
                noise_std,
                learning_rate,
            )

        # --- report
        if epoch % report_rate == 0:

            # --- evaluate all models on train set
            evaluate_parallel(population, train_loader)

            print(
                "[--- @{:02}: \t avg(train)={:2.4f} \t queen(train)={:2.4f} \t queen(dev)={:2.4f} \t time(epoch)={} ---]".format(
                    epoch,
                    sum(population.values()) / len(population),
                    queen.evaluate(train_loader),
                    queen.evaluate(dev_loader),
                    datetime.now() - time_begin,
                )
            )
