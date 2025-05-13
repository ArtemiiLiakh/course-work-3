import asyncio
from sys import platform

from algorithms.greedy_algorithm import GreedyAlgorithm
from models.task import Task


def main():

    task = Task(
        n=6,
        A=(0, 8),
        B=(16, 8),
        J=[(2, 3, 7), (5, 14, 4), (9, 7, 9), (12, 12, 8), (14, 5, 10), (15, 10, 12)],
        v=6,
        T=30
    )

    algorithm = GreedyAlgorithm(task)
    solution = algorithm.SolveRoute()

    print("Маршрут:", solution.route)
    print("Обстежені об'єкти:", solution.inspected)
    print("Загальний час:", solution.total_time)


if __name__ == "__main__":
    main()