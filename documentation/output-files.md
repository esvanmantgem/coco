# Coco output files

Coco produces different output files. Coco will store these files in the folder passed as the argument for `--output`. Here, we describe each file and it's contents.

## Run statistics
In the file `runstats.csv` Coco provides an overview of all parameter settings for the run and the most important results. First it shows some interesting values of the current run. This includes `solver_time` and `total_time`, i.e., the time it took the ILP solver to find a solution and the total runtime of Coco resp. It shows the objective value found by the solver (`obj_val`), the meaning of which depends on the RPS variant used. Next, `gap_to_opt` indicates the gap of the found solution to the optimal solution. And finally, the total cost (`total_cost`) indicates the total cost of all planning units that are in the solution, with the cost for each planning unit according to the input file `pu.csv`. After these values, all parameters that could be set in Coco are shown and their exact values for this run. This makes it easy to check which command was entered for each specific Coco run.

## Solution area
Coco produces two files that represent the solution area found. First, it produces `solution.pdf`, a visual representation of the solution area. Blue dots indicate planning units that are not selected and yellow dots planning units that are selected.

For further processing, Coco also creates a file `solution.csv` which contains the id of each planning unit, the xlocation and ylocation as provided in the `pu.csv`. Additionally, each planning unit has a value `x` where `x = [0,1]`. If `x=0` it means the planning unit is not selected, if `x=1` it means the planning unit is selected.

## Targets
The file `targets.csv` contains information on the occurence of each feature in the solution area. It constains the id of each feature as specified in the `feature.csv`, the total occurence of each feature that should be reached (`total`) according the either the `target` or `prop` in the `feature.csv` and the occurence reached for each feature in the solution area (`reached`).

## Metrics
In case an RPS variant including connectivity was executed, Coco also creates a file called `metrics.csv`. The first column `con_data` indicates the id of the dataset. This is the id as provided in the connecitivity dataset, e.g., the connectivity matrix or (feature) edgelist. Note that this can be (but does not have to be) a feature from the `feature.csv`. If that is the case, the same id should be used. The next column `metric` indicates the metric the values in the row refer to. The total
metric value over the entire planning area is reported (`total`), and for all planning units the minimum (`min`) and maximum (`max`) values. Further, in case thresholds were set as parameters, these values are shown (`min_threshold`, `max_threshold`), otherwise, these values are set to `0`. In case a target was set for the connectivity metrics (RSP-CF), this is shown in the `target` column, otherwise these values are set to `0`. Finally, `total_metric` indicates the total value of the metric for
that feature in the solution area and `avg_per_pu` shows the average metric per planning unit for that feature in the solution area.
