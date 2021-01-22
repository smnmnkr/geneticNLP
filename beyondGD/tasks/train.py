from beyondGD.neural import descent, evolve, swarm, amoeba

from beyondGD.utils import time_track, dict_max
from beyondGD.tasks.utils import (
    setup,
    init_population,
    population_from_model,
    evaluate,
)

# --- map tasks to string args
tasks: dict = {
    "descent": descent,
    "evolve": evolve,
    "swarm": swarm,
    "amoeba": amoeba,
}

#
#
#  -------- do_train -----------
#
@time_track
def do_train(args: dict) -> None:

    # --- setup experiment
    model, data, utils = setup(args)

    # create empty population, return type holder
    population: dict = {}
    last_return_type: str = None

    # log that training is orchestra
    if len(utils.get("train_config").get("tasks")) > 1:
        print("\n[--- ORCHESTRA ---]")

    # --- start training
    for task in utils.get("train_config").get("tasks"):

        # --- init population, if is first task and not gradient descent
        if task.get("type") != ("descent") and not population:
            population = init_population(
                utils.get("model_class"),
                utils.get("model_config"),
                task.get("population_size"),
            )

        # --- create population from last task model
        if (
            last_return_type == "model"
            and task.get("type") != "descent"
        ):
            population = population_from_model(
                utils.get("model_class"),
                model,
                task.get("population_size"),
            )

        # --- start task
        print(f"\n[--- {task.get('type').upper()} ---]")

        # handle task, which take and return population
        if task.get("type") in ("evolve", "amoeba"):
            population = tasks.get(task.get("type"))(
                population,
                data.get("train"),
                data.get("dev"),
                **task.get("parameters"),
            )

            last_return_type = "population"

        # handle task, which take and return model
        elif task.get("type") in ("descent", "swarm"):

            # if last task has returned a population, extract the best model
            if last_return_type == "population":
                best, _ = dict_max(population)

            # else use the model as best
            else:
                best = model

            # train gradient descent
            model = tasks.get(task.get("type"))(
                best,
                data.get("train"),
                data.get("dev"),
                **task.get("parameters"),
            )

            last_return_type = "model"

    # --- get best model from population
    if last_return_type == "population":
        best, _ = dict_max(population)

    # --- last model equals best model
    else:
        best = model

    # --- run metric
    evaluate(
        best,
        utils.get("encoding"),
        data.get("test"),
    )