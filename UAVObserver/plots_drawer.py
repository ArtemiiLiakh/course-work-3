from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models.solution import Solution
from models.task import Task


class PlotsDrawer:
    def __init__(self):
        self.vis_canvases = []

    def plot_route(self, solution: Solution, task: Task, algorithm_name: str, fig, ax):
        # Plot all points from the task
        all_points_x = [task.A[0]] + [task.B[0]] + [j[0] for j in task.J]
        all_points_y = [task.A[1]] + [task.B[1]] + [j[1] for j in task.J]
        ax.scatter(all_points_x, all_points_y, color='gray', label="Усі точки", alpha=0.5, s=50)

        # Plot inspected objects with green squares
        inspected_x = [x for x, y in solution.inspected]
        inspected_y = [y for x, y in solution.inspected]
        ax.scatter(inspected_x, inspected_y, color='green', label="Обстежені об'єкти", marker='s', s=100)

        # Plot A and B with stars
        ax.scatter(*task.A, color='red', label="A (Старт)", marker='*', s=100)
        ax.scatter(*task.B, color='purple', label="B (Фініш)", marker='*', s=100)

        # Plot the route line connecting only the solution points
        x_coords, y_coords = zip(*solution.route)
        ax.plot(x_coords, y_coords, '-', label=f"Маршрут ({algorithm_name})", color='blue')

        total_distance = sum(solution.distances) if solution.distances else 0
        current_time = datetime.now().strftime("%I:%M %p EEST, %A, %B %d, %Y")
        ax.set_title(f"Візуалізація маршруту ({algorithm_name})\nЧас: {solution.total_time:.2f} с\nЗагальна відстань: {total_distance:.2f} м\nДата: {current_time}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True)
        ax.legend()

        # Annotate each leg with distance and flight time
        for i in range(len(solution.route) - 1):
            x1, y1 = solution.route[i]
            x2, y2 = solution.route[i + 1]
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            distance = solution.distances[i]
            flight_time = solution.flight_times[i]
            ax.annotate(f"D: {distance:.2f}m\nT: {flight_time:.2f}s",
                        xy=(mid_x, mid_y),
                        xytext=(5, 5),
                        textcoords="offset points",
                        fontsize=8,
                        bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.5))

    def clear_canvases(self):
        for canvas in self.vis_canvases:
            canvas.get_tk_widget().destroy()
        self.vis_canvases.clear()

    def draw(self, solution: Solution, task: Task, algorithm_name: str, frame):
        self.clear_canvases()
        num_algorithms = 1  # Single plot per draw call
        fig, axes = plt.subplots(1, num_algorithms, figsize=(5 * num_algorithms, 5), squeeze=False)
        axes = axes[0]
        self.plot_route(solution, task, algorithm_name, fig, axes[0])
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.vis_canvases.append(canvas)