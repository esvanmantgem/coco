import pandas as pd

def main():
    coco_sol = 'solution.csv'
    mc_sol = 'connect_best.txt'
    coco = pd.read_csv(coco_sol)
    mc = pd.read_csv(mc_sol)
    print("Coco:", coco['pu_val'].sum())
    print("MC:", mc['solution'].sum())

if __name__ == '__main__':
    main()
