import math
from models.solution import Solution
from models.task import Task


class GreedyAlgorithm:
    def __init__(self, task: Task):
        self.task = task

    def SolveRoute(self) -> Solution:
        P = [self.task.A]
        S = set()
        t_total = 0
        current = self.task.A
        objects = list(self.task.J)
        distances = []
        flight_times = []

        while t_total < self.task.T:
            min_time = float('inf')
            next_obj = None

            for i, (x, y, t) in enumerate(objects):
                if (x, y) not in S and (x, y) != current:
                    d = math.sqrt((x - current[0]) ** 2 + (y - current[1]) ** 2)
                    w = d / self.task.v
                    t_to_B = math.sqrt((self.task.B[0] - x) ** 2 + (self.task.B[1] - y) ** 2) / self.task.v
                    if t_total + w + t + t_to_B <= self.task.T and w + t < min_time:
                        min_time = w + t
                        next_obj = (x, y, t, i)

            if next_obj is None:
                break

            P.append((next_obj[0], next_obj[1]))
            S.add((next_obj[0], next_obj[1]))
            d = math.sqrt((next_obj[0] - current[0]) ** 2 + (next_obj[1] - current[1]) ** 2)
            w = d / self.task.v
            distances.append(d)
            flight_times.append(w)
            t_total += w + next_obj[2]
            current = (next_obj[0], next_obj[1])
            objects.pop(next_obj[3])

        d = math.sqrt((self.task.B[0] - current[0]) ** 2 + (self.task.B[1] - current[1]) ** 2)
        t_to_B = d / self.task.v
        if t_total + t_to_B <= self.task.T:
            P.append(self.task.B)
            distances.append(d)
            flight_times.append(t_to_B)
            t_total += t_to_B
        else:
            P = []
            S = set()
            t_total = 0
            distances = []
            flight_times = []

        return Solution(P, S, t_total, distances, flight_times)
