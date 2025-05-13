class AlgorithmRegistry:
    def __init__(self):
        self.algorithms = {}

    def register(self, name: str, algorithm):
        self.algorithms[name] = algorithm

    def get_algorithms(self):
        return self.algorithms