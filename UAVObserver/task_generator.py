import random

from models.task import Task


class TaskGenerator:
    def __init__(self):
        pass

    def generate_task(self, n: int, v: float, T: float, p: float) -> Task:
        # Initialize the task
        task = Task(n=n, A=None, B=None, J=None, v=v, T=T)

        # Set starting point A (xA = 0, yA = random(0, p)), using integers
        task.A = (0, random.randint(0, int(p)))

        # Set ending point B (xB = p, yB = random(0, p)), using integers
        task.B = (int(p), random.randint(0, int(p)))

        # Initialize J and tJ
        task.J = []
        tJ = []

        # Generate n unique objects with integer coordinates
        for _ in range(n):
            is_unique = False
            x, y = 0, 0
            while not is_unique:
                x = random.randint(0, int(p))
                y = random.randint(0, int(p))
                is_unique = True

                # Check if (x, y) matches A or B
                if (x, y) == task.A or (x, y) == task.B:
                    is_unique = False
                    continue

                # Check if (x, y) is unique among existing J points
                for existing_point in task.J:
                    if (x, y) == existing_point[:2]:  # Compare only (x, y), ignore t
                        is_unique = False
                        break

            # Add the unique point to J with a random inspection time
            t = random.randint(4, 12)
            task.J.append((x, y, t))
            tJ.append(t)

        return task