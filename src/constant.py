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

###
# ARGS CONSTANTS
###

# RSP variants
RSP_CF = 'RSP-CF'
RSP_CC = 'RSP-CC'
RSP_CON = 'RSP-Con'
RSP = 'RSP'
RSP_BLM = 'RSP-BLM'

# metrics
EC = 'ec'
BC = 'bc'
INDEG = 'indegree'
OUTDEG = 'outdegree'

###
# INPUT CONSTANTS
###

# I/O files
FEAT_F = 'feature.csv'
PU_F = 'pu.csv'
PVF_F = 'pvf.csv'
BOUNDS_F = 'bound.dat'

# Column names
# pu.csv
PU_ID = 'pu'
PU_COST = 'cost'
PU_XLOC = 'xloc'
PU_YLOC = 'yloc'

# feature.csv
FEAT_ID = 'feature'
FEAT_PROP = 'prop'
FEAT_TARGET = 'target'
FEAT_NAME = 'name'

# pvf.csv
PVF_FID = 'feature'
PVF_PID = 'pu'
PVF_VAL = 'value'

# feature edgelist, edgelist, con_matrix
HEL_FID = 'feature'
HEL_PID1 = 'pu1'
HEL_PID2 = 'pu2'
HEL_VAL = 'value'

# pu attribute list
ATTR_FID = 'feature'
ATTR_PID = 'pu'
ATTR_VAL = 'value'

# bounds.dat
BD_PID1 = 'id1'
BD_PID2 = 'id2'
BD_VAL = 'value'
BD_BOUND = 'boundary'

###
# CODE CONSTANTS
###

# pux
PUX_PID = 'pu'
PUX_X = 'x'

# metric values
MET_PID = 'pu'
MET_PID1 = 'pu1'
MET_PID2 = 'pu2'
MET_VAL = 'value'

# graph attribue names
NODE_VAL = 'value'
EDGE_VAL = 'value'

# metric value name
MEAN = 'mean'
MEDIAN = 'median'
MIN = 'min'
MAX = 'max'

###
# OUTPUT CONSTANTS
###

# output file names
METRICS = 'metrics.csv'
TARGETS = 'targets.csv'
SOLUTION = 'solution.csv'
RUNSTATS = 'runstats.csv'
SOL_AREA = 'solution_area.pdf'

# args_stats
ARGS_NAME = 'name'
ARGS_VAL = 'value'

# run_stats
RUNSTAT_NAME = 'name'
RUNSTAT_VAL = 'value'
SOLVER_TIME = 'solver_time'
TOTAL_TIME = 'total_time'
OBJ_VAL = 'obj_value'
GAP_OPT = 'gap_to_opt'
TOTAL_COST = 'total_cost'

# features stats
FEATURES = 'features'
TOTAL_F = 'total'
TARGET_F = 'target'
REACHED_F = 'reached'

# metrics stats
DATA_M = 'con_data'
METRIC_M = 'metric'
TOTAL_M = 'total'
MIN_M = 'min'
MAX_M = 'max'
MIN_THRES = 'min_threshold'
MAX_THRES = 'max_threshold'
TARGET_M = 'target'
TOTAL_METRIC_M = 'total_metric'
AVG_PER_PU = 'avg_per_pu'

