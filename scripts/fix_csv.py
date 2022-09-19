import pandas as pd

def main():
    file = 'hexFlow.csv'
    new_file = 'hexFlow_fix.csv'
    df = pd.read_csv(file)
    if df.columns.str.contains('^Unnamed:').any():
        df = pd.read_csv(file, index_col=[0])
    df.columns = df.columns.astype(int)
    df = df.reset_index(drop=True)

    df.columns = range(df.shape[1])
    df.to_csv(new_file, index=False)
    print(df)

if __name__ == '__main__':
    main()
