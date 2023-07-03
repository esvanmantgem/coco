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

#import gurobipy as gp
import pandas as pd
import cocoio as cio
import cocoparser as cparser
import timer as ctimer
#import connectivity as conn
#import conservation as cons
#import solution as sol
#import constant as c
import rsp.rsp as rsp
import pareto.pareto as pareto
import sys
#from gurobipy import GRB



def main():
    # setup timers
    timer = ctimer.Timer()
    timer.start_setup()

    # parse args
    args = cparser.parse_args()

    # read files
    print("files read...")
    if args.cmd == 'PF':
        #if args.input:
        #    print("Currently not implemented, only for test purposes")
        #    (path, features, pu, pvf) = cio.read_csv_files(args.input)
        #    pareto.run_pf_test(args, path, features, pu, pvf, timer)
        #elif args.config:
        if args.config:
            (features, maps, config) = cio.read_config_file(args.config)
            path = args.output
            pareto.run_pf(args, path, features, maps, config, timer)
        else:
            error = "Config json file missing"
            sys.exit(error)
    else:
        (path, features, pu, pvf) = cio.read_csv_files(args.input)
        rsp.run_rsp(args, path, features, pu, pvf, timer)

if __name__ == '__main__':
    main()
