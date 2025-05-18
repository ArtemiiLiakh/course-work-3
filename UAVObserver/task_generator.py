import random

from models.task import Task


class TaskGenerator:
    def __init__(self):
        pass

    def generate_task(self, n: int, v: float, T: float, p: float) -> Task:
        task = Task(n=n, A=None, B=None, J=None, v=v, T=T)

        task.A = (0, random.randint(0, int(p)))

        task.B = (int(p), random.randint(0, int(p)))

        task.J = []
        tJ = []

        for _ in range(n):
            is_unique = False
            x, y = 0, 0
            while not is_unique:
                x = random.randint(0, int(p))
                y = random.randint(0, int(p))
                is_unique = True

                if (x, y) == task.A or (x, y) == task.B:
                    is_unique = False
                    continue

                for existing_point in task.J:
                    if (x, y) == existing_point[:2]:
                        is_unique = False
                        break

            t = random.randint(4, 12)
            task.J.append((x, y, t))
            tJ.append(t)

        return task