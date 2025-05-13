import json
import time
from datetime import datetime
from tkinter import ttk, scrolledtext
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithms.algorithms_registry import AlgorithmRegistry
from algorithms.greedy_algorithm import GreedyAlgorithm
from models.solution import Solution
from models.task import Task
from task_generator import TaskGenerator


class UAVRoutePlanningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Планування маршруту БПЛА")
        self.registry = AlgorithmRegistry()
        self.registry.register("Жадібний", GreedyAlgorithm)
        self.task = None
        self.task_generator = TaskGenerator()


        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        self.task_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.task_frame, text="Робота з ІЗ")

        self.gen_params = {
            "n": tk.StringVar(value="5"),
            "v": tk.StringVar(value="6"),
            "T": tk.StringVar(value="30"),
            "p": tk.StringVar(value="30"),
        }

        ttk.Label(self.task_frame, text="Параметри генерації:").grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Label(self.task_frame, text="Кількість об'єктів (n):").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        ttk.Entry(self.task_frame, textvariable=self.gen_params["n"]).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(self.task_frame, text="Швидкість (v, м/с):").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        ttk.Entry(self.task_frame, textvariable=self.gen_params["v"]).grid(row=2, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(self.task_frame, text="Макс. час (T, с):").grid(row=3, column=0, padx=5, pady=2, sticky="e")
        ttk.Entry(self.task_frame, textvariable=self.gen_params["T"]).grid(row=3, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(self.task_frame, text="Розмір площини (p):").grid(row=4, column=0, padx=5, pady=2, sticky="e")
        ttk.Entry(self.task_frame, textvariable=self.gen_params["p"]).grid(row=4, column=1, padx=5, pady=2, sticky="w")

        self.input_label = ttk.Label(self.task_frame, text="Введіть дані задачі (JSON):")
        self.input_label.grid(row=5, column=0, columnspan=2, pady=5)
        self.input_text = scrolledtext.ScrolledText(self.task_frame, height=10, width=50)
        self.input_text.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        self.button_frame = ttk.Frame(self.task_frame)
        self.button_frame.grid(row=7, column=0, columnspan=2, pady=5)
        ttk.Button(self.button_frame, text="Генерувати", command=self.generate_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Зберегти", command=self.save_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Завантажити", command=self.load_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Редагувати", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Розв'язати та візуалізувати", command=self.solve_and_visualize).pack(
            side=tk.LEFT, padx=5)

        self.output_label = ttk.Label(self.task_frame, text="Результати:")
        self.output_label.grid(row=8, column=0, columnspan=2, pady=5)
        self.output_text = scrolledtext.ScrolledText(self.task_frame, height=10, width=50)
        self.output_text.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

        self.vis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.vis_frame, text="Візуалізація")
        self.vis_canvases = []

        self.exp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.exp_frame, text="Експерименти")

        self.exp_params_frame = ttk.Frame(self.exp_frame)
        self.exp_params_frame.pack(pady=5)
        self.exp_params = {
            "min_size": tk.StringVar(value="1"),
            "max_size": tk.StringVar(value="10"),
            "step": tk.StringVar(value="1"),
            "tasks_per_size": tk.StringVar(value="5"),
            "range_min": tk.StringVar(value="0"),
            "range_max": tk.StringVar(value="20"),
        }

        ttk.Label(self.exp_params_frame, text="Мін. розмір:").grid(row=0, column=0, padx=5)
        ttk.Entry(self.exp_params_frame, textvariable=self.exp_params["min_size"]).grid(row=0, column=1, padx=5)
        ttk.Label(self.exp_params_frame, text="Макс. розмір:").grid(row=0, column=2, padx=5)
        ttk.Entry(self.exp_params_frame, textvariable=self.exp_params["max_size"]).grid(row=0, column=3, padx=5)
        ttk.Label(self.exp_params_frame, text="Крок:").grid(row=0, column=4, padx=5)
        ttk.Entry(self.exp_params_frame, textvariable=self.exp_params["step"]).grid(row=0, column=5, padx=5)
        ttk.Label(self.exp_params_frame, text="К-сть завдань:").grid(row=1, column=0, padx=5)
        ttk.Entry(self.exp_params_frame, textvariable=self.exp_params["tasks_per_size"]).grid(row=1, column=1, padx=5)
        ttk.Label(self.exp_params_frame, text="Мін. діапазон:").grid(row=1, column=2, padx=5)
        ttk.Entry(self.exp_params_frame, textvariable=self.exp_params["range_min"]).grid(row=1, column=3, padx=5)
        ttk.Label(self.exp_params_frame, text="Макс. діапазон:").grid(row=1, column=4, padx=5)
        ttk.Entry(self.exp_params_frame, textvariable=self.exp_params["range_max"]).grid(row=1, column=5, padx=5)

        ttk.Button(self.exp_frame, text="Запустити експерименти", command=self.run_experiments).pack(pady=5)
        self.exp_output_text = scrolledtext.ScrolledText(self.exp_frame, height=15, width=50)
        self.exp_output_text.pack()

    def generate_task(self):
        try:
            n = int(self.gen_params["n"].get())
            v = float(self.gen_params["v"].get())
            T = float(self.gen_params["T"].get())
            p = float(self.gen_params["p"].get())
            if n < 0 or v <= 0 or T <= 0 or p <= 0:
                raise ValueError("Недопустимі значення параметрів: n≥0, v>0, T>0, p>0")
            self.task = self.task_generator.generate_task(n, v, T, p)
            task_data = {"n": self.task.n, "A": self.task.A, "B": self.task.B, "J": self.task.J, "v": self.task.v,
                         "T": self.task.T}
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, json.dumps(task_data, indent=2))
        except ValueError as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Помилка генерації: {str(e)}\n")

    def save_task(self):
        if self.task:
            task_data = {"n": self.task.n, "A": self.task.A, "B": self.task.B, "J": self.task.J, "v": self.task.v,
                         "T": self.task.T}
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, json.dumps(task_data, indent=2))

    def load_task(self):
        try:
            task_data = json.loads(self.input_text.get(1.0, tk.END))
            self.task = Task(task_data["n"], tuple(task_data["A"]), tuple(task_data["B"]),
                             [tuple(j) for j in task_data["J"]], task_data["v"], task_data["T"])
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Помилка завантаження: {str(e)}")

    def edit_task(self):
        try:
            task_data = json.loads(self.input_text.get(1.0, tk.END))
            self.task = Task(task_data["n"], tuple(task_data["A"]), tuple(task_data["B"]),
                             [tuple(j) for j in task_data["J"]], task_data["v"], task_data["T"])
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Дані успішно відредаговані.\n")
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Помилка редагування: {str(e)}")

    def plot_route(self, solution: Solution, algorithm_name: str, fig, ax):
        # Plot all points from the task
        all_points_x = [self.task.A[0]] + [self.task.B[0]] + [j[0] for j in self.task.J]
        all_points_y = [self.task.A[1]] + [self.task.B[1]] + [j[1] for j in self.task.J]
        ax.scatter(all_points_x, all_points_y, color='gray', label="Усі точки", alpha=0.5, s=50)

        # Plot inspected objects with green squares
        inspected_x = [x for x, y in solution.inspected]
        inspected_y = [y for x, y in solution.inspected]
        ax.scatter(inspected_x, inspected_y, color='green', label="Обстежені об'єкти", marker='s', s=100)

        # Plot A and B with stars
        ax.scatter(*self.task.A, color='red', label="A (Старт)", marker='*', s=100)
        ax.scatter(*self.task.B, color='purple', label="B (Фініш)", marker='*', s=100)

        # Plot the route line connecting only the solution points
        x_coords, y_coords = zip(*solution.route)
        ax.plot(x_coords, y_coords, '-', label=f"Маршрут ({algorithm_name})", color='blue')

        total_distance = sum(solution.distances) if solution.distances else 0
        current_time = datetime.now().strftime("%I:%M %p EEST, %A, %B %d, %Y")
        ax.set_title(
            f"Візуалізація маршруту ({algorithm_name})\nЧас: {solution.total_time:.2f} с\nЗагальна відстань: {total_distance:.2f} м\nДата: {current_time}")
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

    def solve_and_visualize(self):
        if not self.task:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Спочатку введіть або згенеруйте задачу.\n")
            return

        self.output_text.delete(1.0, tk.END)
        # Clear previous visualizations
        for canvas in self.vis_canvases:
            canvas.get_tk_widget().destroy()
        self.vis_canvases.clear()

        # Create a figure with subplots for each algorithm
        num_algorithms = len(self.registry.get_algorithms())
        fig, axes = plt.subplots(1, num_algorithms, figsize=(5 * num_algorithms, 5), squeeze=False)
        axes = axes[0]  # Get the first row of axes (1D array of Axes objects)

        for idx, (name, algorithm_class) in enumerate(self.registry.get_algorithms().items()):
            algorithm = algorithm_class(self.task)
            start_time = time.time()
            solution = algorithm.SolveRoute()
            end_time = time.time()
            self.output_text.insert(tk.END, f"Алгоритм: {name}\n")
            self.output_text.insert(tk.END, f"Маршрут: {solution.route}\n")
            self.output_text.insert(tk.END, f"Обстежені об'єкти: {solution.inspected}\n")
            self.output_text.insert(tk.END, f"Загальний час: {solution.total_time:.2f} с\n")
            self.output_text.insert(tk.END, f"Відстані між точками: {solution.distances}\n")
            self.output_text.insert(tk.END, f"Час перельотів: {solution.flight_times}\n")
            self.output_text.insert(tk.END, f"Час виконання: {(end_time - start_time) * 1000:.2f} мс\n\n")
            self.plot_route(solution, name, fig, axes[idx])

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.vis_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.vis_canvases.append(canvas)

    def generate_experiments(self):
        min_size = int(self.exp_params["min_size"].get())
        max_size = int(self.exp_params["max_size"].get())
        step = int(self.exp_params["step"].get())
        tasks_per_size = int(self.exp_params["tasks_per_size"].get())
        range_min = float(self.exp_params["range_min"].get())
        range_max = float(self.exp_params["range_max"].get())

        experiments = []
        for n in range(min_size, max_size + 1, step):
            for _ in range(tasks_per_size):
                task = self.task_generator.generate_task(
                    n=n,
                    v=6,
                    T=30,
                    p=range_max
                )
                experiments.append(task)
        return experiments

    def run_experiments(self):
        experiments = self.generate_experiments()
        self.exp_output_text.delete(1.0, tk.END)

        results = {name: [] for name in self.registry.get_algorithms().keys()}
        for task in experiments:
            for name, algorithm_class in self.registry.get_algorithms().items():
                algorithm = algorithm_class(task)
                start_time = time.time()
                solution = algorithm.SolveRoute()
                end_time = time.time()
                results[name].append({
                    "solution": solution,
                    "execution_time": (end_time - start_time) * 1000
                })

        for name, solutions in results.items():
            avg_time = sum(r["execution_time"] for r in solutions) / len(solutions)
            avg_inspected = sum(len(r["solution"].inspected) for r in solutions) / len(solutions)
            self.exp_output_text.insert(tk.END, f"Алгоритм: {name}\n")
            self.exp_output_text.insert(tk.END, f"Середній час виконання: {avg_time:.2f} мс\n")
            self.exp_output_text.insert(tk.END, f"Середня кількість обстежених об'єктів: {avg_inspected:.2f}\n")
            self.exp_output_text.insert(tk.END, "Деталі:\n")
            for i, res in enumerate(solutions):
                self.exp_output_text.insert(tk.END,
                                            f"Завдання {i + 1}: Обстежено: {len(res['solution'].inspected)}, Час: {res['solution'].total_time:.2f} с, Виконання: {res['execution_time']:.2f} мс\n")
            self.exp_output_text.insert(tk.END, "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = UAVRoutePlanningApp(root)
    root.mainloop()