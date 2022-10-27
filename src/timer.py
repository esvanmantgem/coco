import time

class Timer:
    def __init__(self):
        self.start_sol_ns = None
        self.stop_sol_ns = None
        self.start_set_ns = None
        self.stop_set_ns = None
        self.start_sol = None
        self.stop_sol = None
        self.start_set = None
        self.stop_set = None

    def start_setup(self):
        self.start_set_ns = time.time_ns()
        self.start_set = time.time()

    def stop_setup(self):
        self.stop_set_ns = time.time_ns()
        self.stop_set = time.time()

    def start_solver(self):
        self.start_sol_ns = time.time_ns()
        self.start_sol = time.time()

    def stop_solver(self):
        self.stop_sol_ns = time.time_ns()
        self.stop_sol = time.time()

    def setup_time(self):
        return self.stop_set - self.start_set

    def solver_time(self):
        return self.stop_sol - self.start_sol

    def stop(self):
        self.stop_solver()
        self.stop_setup()
