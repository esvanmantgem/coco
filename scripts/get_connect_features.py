import pandas as pd

def main():
    puvspr = 'puvspr_connect.dat'
    ps = pd.read_csv(puvspr)
    print(ps)
    #print("MC:", mc['solution'].sum())
    #print(ps.groupby(["species"])).
    #pu_per_sp = [y for x, y in ps.groupby('species')]

    df = ps.loc[ps['species'] == 21]
    print(ps.loc[ps['species'] == 21])
    #print(pu_per_sp)

    df.to_csv('puvnew.csv', index=False)
        #amounts = conservation.puvspr.groupby(["species"]).amount.sum().reset_index()

if __name__ == '__main__':
    main()
