import pandas as pd

class Conservation:

    def __init__(self, pu, species, puvspr, bounds=None):
        self.pu = pu
        self.species = species
        self.puvspr = puvspr
        self.bounds = bounds
        self.prop_target = None
        self.max_cost = None
        self.min_cost = None
        self.set_species_targets()

    def set_species_targets(self):
        if 'prop' in self.species.columns:
            self.amounts = self.puvspr.groupby(["species"]).amount.sum().reset_index()
            self.prop_target = self.species.filter(['id'], axis=1)
            self.prop_target['target'] = ""

    def get_target(self, k):
        if 'target' in self.species.columns:
            # tk = value of target in row with species id
            return self.species.loc[self.species['id'] == k, 'target'].item()
        elif 'prop' in self.species.columns:
            prop = self.species.loc[self.species['id'] == k, 'prop'].item()
            amount = self.amounts.loc[self.amounts['species'] == k, 'amount'].item()
            tk = prop * amount
            self.prop_target.loc[self.prop_target['id'] == k, 'target'] = tk
            return tk
        else: #TODO move this check, ugly here
            error = "Error: target or prop required in species.dat"
            sys.exit(error)

    def set_max_cost(self, cost):
        self.max_cost = cost

    def set_min_cost(self, cost):
        self.min_cost = cost
