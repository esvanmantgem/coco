# Copyright (c) 2022, Eline van Mantgem
#
# This file is part of Coco.
#
# Coco is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Coco is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Coco. If not, see <http://www.gnu.org/licenses/>.

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
