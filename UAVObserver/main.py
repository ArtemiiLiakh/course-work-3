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
        self.task_generator = TaskGenerator()
        self.plots_drawer = PlotsDrawer()


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
        ttk.Button(self.button_frame, text="Завантажити з файлу", command=self.load_task_from_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Зберегти у файл", command=self.save_task_to_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Редагувати", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Розв'язати та візуалізувати", command=self.solve_and_visualize).pack(side=tk.LEFT, padx=5)

        self.output_label = ttk.Label(self.task_frame, text="Результати:")
        self.output_label.grid(row=8, column=0, columnspan=2, pady=5)
        self.output_text = scrolledtext.ScrolledText(self.task_frame, height=10, width=50)
        self.output_text.grid(row=9, column=0, columnspan=2, padx=5, pady=5)


        self.vis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.vis_frame, text="Візуалізація")


        self.exp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.exp_frame, text="Експерименти")

        self.exp_notebook = ttk.Notebook(self.exp_frame)
        self.exp_notebook.pack(pady=10, expand=True)

        # 3.4.1: Вплив параметра завершення алгоритму мурашиних колоній
        self.exp_341_frame = ttk.Frame(self.exp_notebook)
        self.exp_notebook.add(self.exp_341_frame, text="3.4.1")

        self.exp_341_params = {
            "max_iters": tk.StringVar(value="50,100,150,200"),
            "n": tk.StringVar(value="10"),
            "T": tk.StringVar(value="30"),
            "tasks_per_iter": tk.StringVar(value="20"),
            "v": tk.StringVar(value="6"),
            "range_max": tk.StringVar(value="20"),
        }
        ttk.Label(self.exp_341_frame, text="Значення max_iter (через кому):").grid(row=0, column=0, padx=5,
                                                                                   columnspan=2)
        ttk.Entry(self.exp_341_frame, textvariable=self.exp_341_params["max_iters"]).grid(row=0, column=2, padx=5,
                                                                                          columnspan=2)
        ttk.Label(self.exp_341_frame, text="Кількість об’єктів (n):").grid(row=1, column=0, padx=5)
        ttk.Entry(self.exp_341_frame, textvariable=self.exp_341_params["n"]).grid(row=1, column=1, padx=5)
        ttk.Label(self.exp_341_frame, text="Макс. час (T, с):").grid(row=1, column=2, padx=5)
        ttk.Entry(self.exp_341_frame, textvariable=self.exp_341_params["T"]).grid(row=1, column=3, padx=5)
        ttk.Label(self.exp_341_frame, text="К-сть завдань для усереднення:").grid(row=2, column=0, padx=5)
        ttk.Entry(self.exp_341_frame, textvariable=self.exp_341_params["tasks_per_iter"]).grid(row=2, column=1, padx=5)
        ttk.Label(self.exp_341_frame, text="Розмір поля:").grid(row=2, column=2, padx=5)
        ttk.Entry(self.exp_341_frame, textvariable=self.exp_341_params["range_max"]).grid(row=2, column=3, padx=5)
        ttk.Button(self.exp_341_frame, text="Запустити", command=self.run_exp_341).grid(row=3, column=0, columnspan=4,
                                                                                        pady=5)
        self.exp_341_output = scrolledtext.ScrolledText(self.exp_341_frame, height=10, width=50)
        self.exp_341_output.grid(row=4, column=0, columnspan=4, pady=5)

        # 3.4.2: Вплив параметрів задачі
        self.exp_342_frame = ttk.Frame(self.exp_notebook)
        self.exp_notebook.add(self.exp_342_frame, text="3.4.2")

        self.exp_342_params = {
            "T_values": tk.StringVar(value="30,45,60"),
            "n": tk.StringVar(value="10"),
            "tasks_per_T": tk.StringVar(value="20"),
            "v": tk.StringVar(value="6"),
            "range_max": tk.StringVar(value="20"),
        }
        ttk.Label(self.exp_342_frame, text="Значення T (через кому):").grid(row=0, column=0, padx=5, columnspan=2)
        ttk.Entry(self.exp_342_frame, textvariable=self.exp_342_params["T_values"]).grid(row=0, column=2, padx=5,
                                                                                         columnspan=2)
        ttk.Label(self.exp_342_frame, text="Кількість об’єктів (n):").grid(row=1, column=0, padx=5)
        ttk.Entry(self.exp_342_frame, textvariable=self.exp_342_params["n"]).grid(row=1, column=1, padx=5)
        ttk.Label(self.exp_342_frame, text="К-сть завдань для усереднення:").grid(row=2, column=0, padx=5)
        ttk.Entry(self.exp_342_frame, textvariable=self.exp_342_params["tasks_per_T"]).grid(row=2, column=1, padx=5)
        ttk.Label(self.exp_342_frame, text="Розмір поля:").grid(row=2, column=2, padx=5)
        ttk.Entry(self.exp_342_frame, textvariable=self.exp_342_params["range_max"]).grid(row=2, column=3, padx=5)
        ttk.Button(self.exp_342_frame, text="Запустити", command=self.run_exp_342).grid(row=3, column=0, columnspan=4,
                                                                                        pady=5)
        self.exp_342_output = scrolledtext.ScrolledText(self.exp_342_frame, height=10, width=50)
        self.exp_342_output.grid(row=4, column=0, columnspan=4, pady=5)

        # 3.4.3: Вплив розмірності задачі
        self.exp_343_frame = ttk.Frame(self.exp_notebook)
        self.exp_notebook.add(self.exp_343_frame, text="3.4.3")

        self.exp_343_params = {
            "min_size": tk.StringVar(value="5"),
            "max_size": tk.StringVar(value="20"),
            "step": tk.StringVar(value="5"),
            "tasks_per_n": tk.StringVar(value="20"),
            "T": tk.StringVar(value="30"),
            "v": tk.StringVar(value="6"),
            "range_max": tk.StringVar(value="20"),
        }
        ttk.Label(self.exp_343_frame, text="Мін. кількість об’єктів:").grid(row=0, column=0, padx=5)
        ttk.Entry(self.exp_343_frame, textvariable=self.exp_343_params["min_size"]).grid(row=0, column=1, padx=5)
        ttk.Label(self.exp_343_frame, text="Макс. кількість об’єктів:").grid(row=0, column=2, padx=5)
        ttk.Entry(self.exp_343_frame, textvariable=self.exp_343_params["max_size"]).grid(row=0, column=3, padx=5)
        ttk.Label(self.exp_343_frame, text="Крок:").grid(row=1, column=0, padx=5)
        ttk.Entry(self.exp_343_frame, textvariable=self.exp_343_params["step"]).grid(row=1, column=1, padx=5)
        ttk.Label(self.exp_343_frame, text="К-сть завдань для усереднення:").grid(row=1, column=2, padx=5)
        ttk.Entry(self.exp_343_frame, textvariable=self.exp_343_params["tasks_per_n"]).grid(row=1, column=3, padx=5)
        ttk.Label(self.exp_343_frame, text="Макс. час (T, с):").grid(row=2, column=0, padx=5)
        ttk.Entry(self.exp_343_frame, textvariable=self.exp_343_params["T"]).grid(row=2, column=1, padx=5)
        ttk.Label(self.exp_343_frame, text="Розмір поля:").grid(row=2, column=2, padx=5)
        ttk.Entry(self.exp_343_frame, textvariable=self.exp_343_params["range_max"]).grid(row=2, column=3, padx=5)
        ttk.Button(self.exp_343_frame, text="Запустити", command=self.run_exp_343).grid(row=3, column=0, columnspan=4,
                                                                                        pady=5)
        self.exp_343_output = scrolledtext.ScrolledText(self.exp_343_frame, height=10, width=50)
        self.exp_343_output.grid(row=4, column=0, columnspan=4, pady=5)

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

        self.plots_drawer.draw(solutions, self.task, algorithm_names, self.vis_frame)

    def generate_exp_341_tasks(self):
        n = int(self.exp_341_params["n"].get())
        T = float(self.exp_341_params["T"].get())
        tasks_per_iter = int(self.exp_341_params["tasks_per_iter"].get())
        range_max = float(self.exp_341_params["range_max"].get())
        v = float(self.exp_341_params["v"].get())
        max_iters = [int(x.strip()) for x in self.exp_341_params["max_iters"].get().split(",")]

        experiments = []
        for _ in range(tasks_per_iter):
            task = self.task_generator.generate_task(n, v, T, range_max)
            experiments.append((task, max_iters))
        return experiments

    def generate_exp_342_tasks(self):
        n = int(self.exp_342_params["n"].get())
        tasks_per_T = int(self.exp_342_params["tasks_per_T"].get())
        range_max = float(self.exp_342_params["range_max"].get())
        v = float(self.exp_342_params["v"].get())
        T_values = [float(x.strip()) for x in self.exp_342_params["T_values"].get().split(",")]

        experiments = []
        for T in T_values:
            for _ in range(tasks_per_T):
                task = self.task_generator.generate_task(n, v, T, range_max)
                experiments.append(task)
        return experiments

    def generate_exp_343_tasks(self):
        min_size = int(self.exp_343_params["min_size"].get())
        max_size = int(self.exp_343_params["max_size"].get())
        step = int(self.exp_343_params["step"].get())
        tasks_per_n = int(self.exp_343_params["tasks_per_n"].get())
        T = float(self.exp_343_params["T"].get())
        range_max = float(self.exp_343_params["range_max"].get())
        v = float(self.exp_343_params["v"].get())

        experiments = []
        for n in range(min_size, max_size + 1, step):
            for _ in range(tasks_per_n):
                task = self.task_generator.generate_task(n, v, T, range_max)
                experiments.append(task)
        return experiments

    def run_exp_341(self):
        experiments = self.generate_exp_341_tasks()
        self.exp_341_output.delete(1.0, tk.END)

        results = {int(x.strip()): {"inspected": 0.0, "time": 0.0} for x in
                   self.exp_341_params["max_iters"].get().split(",")}
        tasks_per_iter = int(self.exp_341_params["tasks_per_iter"].get())

        for task, max_iters in experiments:
            for max_iter in max_iters:
                algorithm = self.registry.get_algorithms()["Мурашиний"](task)
                start_time = time.time()
                algorithm.ChangeMaxIteration(max_iter)
                solution = algorithm.SolveRoute()
                end_time = time.time()
                exec_time = (end_time - start_time) * 1000
                results[max_iter]["inspected"] += len(solution.inspected) / tasks_per_iter
                results[max_iter]["time"] += exec_time / tasks_per_iter

        self.exp_341_output.insert(tk.END, "3.4.1: Вплив параметра завершення алгоритму мурашиних колоній\n")
        for max_iter, data in results.items():
            self.exp_341_output.insert(tk.END,
                                       f"max_iter={max_iter}: Середня кількість об’єктів={data['inspected']:.2f}, Середній час={data['time']:.2f} мс\n")

    def run_exp_342(self):
        experiments = self.generate_exp_342_tasks()
        self.exp_342_output.delete(1.0, tk.END)

        results = {float(x.strip()): {"greedy_inspected": 0.0, "aco_inspected": 0.0} for x in
                   self.exp_342_params["T_values"].get().split(",")}
        tasks_per_T = int(self.exp_342_params["tasks_per_T"].get())

        for task in experiments:
            T = task.T
            greedy = self.registry.get_algorithms()["Жадібний"](task)
            aco = self.registry.get_algorithms()["Мурашиний"](task)
            start_time = time.time()
            greedy_solution = greedy.SolveRoute()
            end_time = time.time()
            results[T]["greedy_inspected"] += len(greedy_solution.inspected) / tasks_per_T
            start_time = time.time()
            aco_solution = aco.SolveRoute()
            end_time = time.time()
            results[T]["aco_inspected"] += len(aco_solution.inspected) / tasks_per_T

        self.exp_342_output.insert(tk.END, "3.4.2: Вплив параметрів задачі (T)\n")
        for T, data in results.items():
            self.exp_342_output.insert(tk.END,
                                       f"T={T}: Жадібний={data['greedy_inspected']:.2f}, Мурашиний={data['aco_inspected']:.2f}\n")

    def run_exp_343(self):
        experiments = self.generate_exp_343_tasks()
        self.exp_343_output.delete(1.0, tk.END)

        results = {n: {"greedy_inspected": 0.0, "aco_inspected": 0.0, "greedy_time": 0.0, "aco_time": 0.0}
                   for n in
                   range(int(self.exp_343_params["min_size"].get()), int(self.exp_343_params["max_size"].get()) + 1,
                         int(self.exp_343_params["step"].get()))}
        tasks_per_n = int(self.exp_343_params["tasks_per_n"].get())

        for task in experiments:
            n = task.n
            greedy = self.registry.get_algorithms()["Жадібний"](task)
            aco = self.registry.get_algorithms()["Мурашиний"](task)
            start_time = time.time()
            greedy_solution = greedy.SolveRoute()
            end_time = time.time()
            exec_time = (end_time - start_time) * 1000
            results[n]["greedy_inspected"] += len(greedy_solution.inspected) / tasks_per_n
            results[n]["greedy_time"] += exec_time / tasks_per_n
            start_time = time.time()
            aco_solution = aco.SolveRoute()
            end_time = time.time()
            exec_time = (end_time - start_time) * 1000
            results[n]["aco_inspected"] += len(aco_solution.inspected) / tasks_per_n
            results[n]["aco_time"] += exec_time / tasks_per_n

        self.exp_343_output.insert(tk.END, "3.4.3: Вплив розмірності задачі (n)\n")
        for n, data in results.items():
            self.exp_343_output.insert(tk.END,
                                       f"n={n}: Жадібний (об’єктів={data['greedy_inspected']:.2f}, час={data['greedy_time']:.2f} мс), "
                                       f"Мурашиний (об’єктів={data['aco_inspected']:.2f}, час={data['aco_time']:.2f} мс)\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = UAVRoutePlanningApp(root)
    root.mainloop()