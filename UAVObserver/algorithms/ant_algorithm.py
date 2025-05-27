from itertools import accumulate
import math
import random
from typing import List, Optional
from models.task import Task
from models.solution import Solution
import multiprocessing

class Point:
    x: int
    y: int
    delay: int

    def __init__(self, x: int, y: int, delay: int):
        self.x = x
        self.y = y
        self.delay = delay

    def __repr__(self):
        return f'{self.x}x{self.y}'

class AlgorithmParams:
    def __init__(self,
        a: float,
        b: float,
        p: float,
        m: int,
        n: int,
        t0: float,
        max_iter: int,
        stagnation: int
    ):
        self.a = a
        self.b = b
        self.p = p
        self.m = m
        self.n = n
        self.t0 = t0
        self.max_iter = max_iter
        self.stagnation = stagnation

class Ant:
    def __init__(
        self, 
        a: float,
        b: float,
        n: int,
        T: float,
        G: List[Point],
        w: List[List[float]],
        pheromones: List[List[float]],
    ):
        self.a = a
        self.b = b
        self.n = n
        self.T = T
        self.G = G
        self.w = w
        self.pheromones = pheromones

    @staticmethod
    def staticRun(args):
        self, *args = args
        return self.run(*args)

    def run(self, n):
        A = self.G[0]
        current = A
        currentIndex = 0
        time = 0
        pathIndexes = [0]
        visited = [A]
        Sk = []
        
        while True:
            nextIndex = self._getPath(visited, time, currentIndex)
            if (nextIndex == None): break
            time += self.w[currentIndex][nextIndex] + self.G[nextIndex].delay
            current = self.G[nextIndex]
            currentIndex = nextIndex
            visited.append(current)
            pathIndexes.append(currentIndex)
            Sk.append(current)

        time += self.w[currentIndex][-1]
        pathIndexes.append(len(self.G)-1)

        for i in range(len(pathIndexes)-1):
            self.pheromones[pathIndexes[i]][pathIndexes[i+1]] += len(Sk)/n

        return pathIndexes, time

    def _getPath(
            self,
            visited: List[Point], 
            time: float,
            currentIndex: int 
        ) -> Optional[int]:
        a, b, T = self.a, self.b, self.T
        candidates = []
        for index, j in enumerate(self.G):
            total_time = time+j.delay+self.w[currentIndex][index]+self.w[index][-1]
            if j not in visited and total_time <= T and j != self.G[-1]:
                candidates.append(index)
        if (len(candidates) == 0): return None

        P = []
        probability = lambda i, currentindex: pow(self.pheromones[currentindex][i], a)*pow(1/(self.w[currentindex][i]+self.G[i].delay), b)

        for i in candidates:
            s = sum([probability(j, currentIndex) for j in candidates])
            pj = probability(i, currentIndex)/s
            P.append(pj)
        
        p = random.random()
        propabilities = accumulate(P)
        for j, pj in enumerate(propabilities):
            if pj >= p: 
                return candidates[j]

class AntAlgorithm:
    def __init__(self, task: Task, params: Optional[AlgorithmParams]=None):
        self.task = task

        if (params == None):
            params = AlgorithmParams(
                a = 1.5,
                b = 13,
                p = 0.015,
                m = 15,
                n = len(task.J)+2,
                t0 = 0.01,
                max_iter = 70,
                stagnation = 10
            )
        self.params = params
        self.G: List[Point] = [
            Point(task.A[0], task.A[1], 0),
            *map(lambda p: Point(p[0], p[1], p[2]), task.J),
            Point(task.B[0], task.B[1], 0),
        ]
        self.w = self._calculateTimeDelays()
        self.pheromones = [[params.t0]*len(self.G) for _ in range(len(self.G))]
        self.ants = [Ant(
            a=self.params.a,
            b=self.params.b,
            n=self.params.n,
            T=self.task.T,
            G=self.G,
            w=self.w,
            pheromones=self.pheromones
        ) for _ in range(self.params.m)]
    
    def SolveRoute(self) -> Solution:
        n, p, max_iter = self.params.n, self.params.p, self.params.max_iter
        bestPath: List[Point] = []
        bestS: List[Point] = []
        bestDistances: List[float] = []
        bestFlightTimes: List[float] = []
        totalTime = float('inf')
        bestPathIndexes: List[int] = []

        stagnationIter = 0

        with multiprocessing.Pool(processes=len(self.ants)) as pool:
            for _ in range(max_iter):
                if stagnationIter >= self.params.stagnation:
                    break
                
                args = list(map(lambda ant: (ant, n), self.ants))
                solutions = pool.map(Ant.staticRun, args)
                bestSolution = sorted(solutions, key=lambda solution: (len(solution[0]), solution[1]))[::-1][0]

                if (set(bestSolution[0]) == set(bestPathIndexes)):
                    stagnationIter += 1
                else:
                    stagnationIter = 0
                
                if len(bestSolution[0]) > len(bestPathIndexes) or (len(bestSolution[0]) == len(bestPathIndexes) and totalTime > bestSolution[1]):
                    bestPathIndexes = bestSolution[0]
                    totalTime = bestSolution[1]
                    bestS = set(map(lambda i: self.G[i], bestPathIndexes[1:len(bestPathIndexes)-1]))

                for i in range(len(self.pheromones)):
                    for j in range(len(self.pheromones)):
                        self.pheromones[i][j] *= (1-p)
        bestPath = list(map(lambda i: (self.G[i].x, self.G[i].y), bestPathIndexes))
        bestS = set(map(lambda i: (self.G[i].x, self.G[i].y), bestPathIndexes[1:len(bestPathIndexes)-1]))

        for i in range(len(bestPathIndexes)-1):
            current = bestPathIndexes[i]
            next = bestPathIndexes[i+1]
            bestDistances.append(self.w[current][next]*self.task.v)
            bestFlightTimes.append(self.w[current][next])

        return Solution(bestPath, bestS, totalTime, bestDistances, bestFlightTimes)

    def _calculateTimeDelays(self) -> List[List[float]]:
        v = self.task.v
        w: List[List[float]] = []
        for i in self.G:
            w.append([])
            for j in self.G:
                time = round(math.sqrt((i.x-j.x)**2 + (i.y-j.y)**2)/v, 2)
                w[-1].append(time)
        return w

    def ChangeMaxIteration(self, newValue : int):
        self.params.max_iter = newValue