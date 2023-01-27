import pandas as pd
import constant as c

class Conservation:

    def __init__(self, pu, features, pvf, strategy, bounds=None):
        self.pu = pu
        self.features = features
        self.pvf = pvf
        self.bounds = bounds
        self.strategy = strategy
        self.blm_weight = 1
        self.prop_target = None
        self.max_cost = None
        self.min_cost = None
        self.set_features_targets()

    def set_features_targets(self):
        if c.FEAT_PROP in self.features.columns:
            # TODO rewrite in case name of 'value' column changes
            self.amounts = self.pvf.groupby([c.PVF_FID]).value.sum().reset_index()
            self.prop_target = self.features.filter([c.FEAT_ID], axis=1)
            self.prop_target[c.FEAT_TARGET] = ""

    def get_target(self, k):
        if c.FEAT_TARGET in self.features.columns:
            # tk = value of target in row with features id
            return self.features.loc[self.features[c.FEAT_ID] == k, c.FEAT_TARGET].item()
        elif c.FEAT_PROP in self.features.columns:
            prop = self.features.loc[self.features[c.FEAT_ID] == k, c.FEAT_PROP].item()
            # TODO rewrite in case name of 'value' column changes
            amount = self.amounts.loc[self.amounts[c.PVF_FID] == k, c.PVF_VAL].item()
            tk = prop * amount
            self.prop_target.loc[self.prop_target[c.FEAT_ID] == k, c.FEAT_TARGET] = tk
            return tk
        else: #TODO move this check, ugly here
            error = "Error: target or prop required in features.csv"
            sys.exit(error)

    def set_max_cost(self, cost):
        self.max_cost = cost

    def set_min_cost(self, cost):
        self.min_cost = cost

    def set_blm_weight(self, blm):
        self.blm_weight = blm
