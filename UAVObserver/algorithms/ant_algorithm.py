from itertools import accumulate
import math
import random
from typing import List, Optional
from models.task import Task
from models.solution import Solution

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

class AntAlgorithm:
    def __init__(self, task: Task, params: Optional[AlgorithmParams]=None):
        self.task = task

        if (params == None):
            params = AlgorithmParams(
                a = 0.05,
                b = 2.5,
                p = 0.01,
                m = 10,
                n = len(task.J)+2,
                t0 = 0.01,
                max_iter = 100,
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
    
    def SolveRoute(self) -> Solution:
        m, n, p, max_iter = self.params.m, self.params.n, self.params.p, self.params.max_iter
        A = self.G[0]
        B = self.G[-1]
        bestPath: List[Point] = [A]
        bestS: List[Point] = []
        bestDistances: List[float] = []
        bestFlightTimes: List[float] = []
        totalTime = float('inf')
        
        stagnationIter = 0

        for _ in range(max_iter):
            if stagnationIter >= self.params.stagnation:
                break
            
            for k in range(m):
                current = A
                currentIndex = 0
                time = 0
                path = [A]
                pathIndexes = [0]
                visited = [A]
                Sk = []
                distances = []
                flightTimes = []
                while True:
                    nextIndex = self._getCandidate(visited, time, currentIndex)
                    if (nextIndex == None): break
                    time += self.w[currentIndex][nextIndex] + self.G[nextIndex].delay
                    distances.append(self.w[currentIndex][nextIndex]*self.task.v)
                    flightTimes.append(self.w[currentIndex][nextIndex])
                    current = self.G[nextIndex]
                    currentIndex = nextIndex
                    visited.append(current)
                    path.append(current)
                    pathIndexes.append(currentIndex)
                    Sk.append(current)

                time += self.w[currentIndex][-1]
                distances.append(self.w[currentIndex][-1]*self.task.v)
                flightTimes.append(self.w[currentIndex][-1])
                pathIndexes.append(len(self.G)-1)
                path.append(B)

                if (bestS == Sk):
                    stagnationIter += 1
                else:
                    stagnationIter = 0

                if (len(Sk) > len(bestS) or (len(Sk) == len(bestS) and time < totalTime)):
                    bestS = Sk
                    bestPath = path
                    totalTime = time
                    bestDistances = distances
                    bestFlightTimes = flightTimes

                for i in range(len(pathIndexes)-1):
                    self.pheromones[pathIndexes[i]][pathIndexes[i+1]] += len(Sk)/n
                
            for i in range(len(self.pheromones)):
                for j in range(len(self.pheromones)):
                    self.pheromones[i][j] *= (1-p)
        
        bestPath = list(map(lambda p: (p.x, p.y), bestPath))
        bestS = set(map(lambda p: (p.x, p.y), bestS))

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

    def _getCandidate(
            self,
            visited: List[Point], 
            time: float,
            currentIndex: int 
        ) -> Optional[int]:
        a, b, T = self.params.a, self.params.b, self.task.T
        candidates = []
        for index, j in enumerate(self.G):
            total_time = time+j.delay+self.w[currentIndex][index]+self.w[index][-1]
            if j not in visited and total_time <= T and j != self.G[-1]:
                candidates.append(index)
        if (len(candidates) == 0): return None

        P = []
        probability = lambda i, nextindex: (self.pheromones[nextindex][i]**a)*(1/(self.w[nextindex][i]+self.G[i].delay))**b

        for i in candidates:
            s = sum([probability(j, currentIndex) for j in candidates])
            pj = probability(i, currentIndex)/s
            P.append(pj)
        
        p = random.random()
        propabilities = accumulate(P)
        for j, pj in enumerate(propabilities):
            if pj >= p: 
                return candidates[j]

    def ChangeMaxIteration(self, newValue : int):
        self.params.max_iter = newValue