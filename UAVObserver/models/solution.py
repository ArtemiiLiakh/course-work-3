from typing import Set, Tuple, List


class Solution:
    def __init__(self, route: List[Tuple[float, float]], inspected: Set[Tuple[float, float]], total_time: float, distances: List[float], flight_times: List[float]):
        self.route = route
        self.inspected = inspected
        self.total_time = total_time
        self.distances = distances
        self.flight_times = flight_times