import json
import time
from tkinter import ttk, scrolledtext, filedialog
import tkinter as tk
from algorithms.algorithms_registry import AlgorithmRegistry
from algorithms.greedy_algorithm import GreedyAlgorithm
from algorithms.ant_algorithm import AntAlgorithm
from models.task import Task
from task_generator import TaskGenerator
from plots_drawer import PlotsDrawer

class UAVRoutePlanningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Планування маршруту БПЛА")
        self.registry = AlgorithmRegistry()
        self.registry.register("Жадібний", GreedyAlgorithm)
        self.registry.register("Мурашиний", AntAlgorithm)
        self.task = None
        self.task_generator = TaskGenerator()  # Initialize the task generator
        self.plots_drawer = PlotsDrawer()  # Initialize the plots drawer

        # GUI Layout
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        # Task Input Tab
        self.task_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.task_frame, text="Робота з ІЗ")

        # Parameters for task generation
        self.gen_params = {
            "n": tk.StringVar(value="5"),  # Default number of objects
            "v": tk.StringVar(value="6"),  # Default UAV speed (m/s)
            "T": tk.StringVar(value="30"),  # Default max flight time (s)
            "p": tk.StringVar(value="30"),  # Default plane size
        }

        # Use grid for consistent layout
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
        ttk.Button(self.button_frame, text="Завантажити з файлу", command=self.load_task_from_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Зберегти у файл", command=self.save_task_to_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Редагувати", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Розв'язати та візуалізувати", command=self.solve_and_visualize).pack(side=tk.LEFT, padx=5)

        self.output_label = ttk.Label(self.task_frame, text="Результати:")
        self.output_label.grid(row=8, column=0, columnspan=2, pady=5)
        self.output_text = scrolledtext.ScrolledText(self.task_frame, height=10, width=50)
        self.output_text.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

        # Visualization Tab
        self.vis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.vis_frame, text="Візуалізація")

        # Experiments Tab
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
        ttk.Label(self.exp_params_frame, text="Розмір поля:").grid(row=1, column=4, padx=5)
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
            task_data = {"n": self.task.n, "A": self.task.A, "B": self.task.B, "J": self.task.J, "v": self.task.v, "T": self.task.T}
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, json.dumps(task_data, indent=2))
        except ValueError as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Помилка генерації: {str(e)}\n")

    def save_task(self):
        if self.task:
            task_data = {"n": self.task.n, "A": self.task.A, "B": self.task.B, "J": self.task.J, "v": self.task.v, "T": self.task.T}
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, json.dumps(task_data, indent=2))

    def load_task_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    task_data = json.load(file)
                    self.task = Task(task_data["n"], tuple(task_data["A"]), tuple(task_data["B"]), [tuple(j) for j in task_data["J"]], task_data["v"], task_data["T"])
                    self.input_text.delete(1.0, tk.END)
                    self.input_text.insert(tk.END, json.dumps(task_data, indent=2))
                    self.output_text.delete(1.0, tk.END)
                    self.output_text.insert(tk.END, f"Задача успішно завантажена з {file_path}\n")
            except Exception as e:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, f"Помилка завантаження з файлу: {str(e)}\n")

    def save_task_to_file(self):
        if self.task:
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file_path:
                try:
                    task_data = {"n": self.task.n, "A": self.task.A, "B": self.task.B, "J": self.task.J, "v": self.task.v, "T": self.task.T}
                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(task_data, file, indent=2)
                    self.output_text.delete(1.0, tk.END)
                    self.output_text.insert(tk.END, f"Задача успішно збережено у {file_path}\n")
                except Exception as e:
                    self.output_text.delete(1.0, tk.END)
                    self.output_text.insert(tk.END, f"Помилка збереження у файл: {str(e)}\n")

    def load_task(self):
        try:
            task_data = json.loads(self.input_text.get(1.0, tk.END))
            self.task = Task(task_data["n"], tuple(task_data["A"]), tuple(task_data["B"]), [tuple(j) for j in task_data["J"]], task_data["v"], task_data["T"])
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Помилка завантаження: {str(e)}")

    def edit_task(self):
        try:
            task_data = json.loads(self.input_text.get(1.0, tk.END))
            self.task = Task(task_data["n"], tuple(task_data["A"]), tuple(task_data["B"]), [tuple(j) for j in task_data["J"]], task_data["v"], task_data["T"])
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Дані успішно відредаговані.\n")
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Помилка редагування: {str(e)}")

    def solve_and_visualize(self):
        if not self.task:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Спочатку введіть або згенеруйте задачу.\n")
            return

        self.output_text.delete(1.0, tk.END)
        solutions = []
        algorithm_names = []
        # Solve for each algorithm and collect solutions
        for name, algorithm_class in self.registry.get_algorithms().items():
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
            solutions.append(solution)
            algorithm_names.append(name)

        # Draw all solutions in a single call
        self.plots_drawer.draw(solutions, self.task, algorithm_names, self.vis_frame)

    def generate_experiments(self):
        min_size = int(self.exp_params["min_size"].get())
        max_size = int(self.exp_params["max_size"].get())
        step = int(self.exp_params["step"].get())
        tasks_per_size = int(self.exp_params["tasks_per_size"].get())
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
                self.exp_output_text.insert(tk.END, f"Завдання {i+1}: Обстежено: {len(res['solution'].inspected)}, Час: {res['solution'].total_time:.2f} с, Виконання: {res['execution_time']:.2f} мс\n")
            self.exp_output_text.insert(tk.END, "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = UAVRoutePlanningApp(root)
    root.mainloop()