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

import pandas as pd
import constant as c

class Conservation:

    def __init__(self, pu, features, pvf, strategy, bounds=None):
        """
        Creates and initializes a new Conservation object

        Parameters
        ----------
        pu : Pandas DataFrame
            DataFrame containing info on all planning units
        features : Pandas DataFrame
            DataFrame containing info on all features
        pvf : Pandas DataFrame
            DataFrame containing info on feature occurence per planning unit
        strategy : str
            RSP variant to run
        bounds : Pandas DataFrame
            DataFrame containing bounds info
        Returns
        -------
        None
        """

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
        """
        Sets the targets for the features

        Parameters
        ----------
            -
        Returns
        -------
        None
        """

        if c.FEAT_PROP in self.features.columns:
            self.amounts = self.pvf.groupby([c.PVF_FID]).value.sum().reset_index()
            self.prop_target = self.features.filter([c.FEAT_ID], axis=1)
            self.prop_target[c.FEAT_TARGET] = ""

    def has_target(self, target):
        return True
        #if target in self.features[c.PVF_FID].values:
        #    return True
        #return False
        #if(conservation.has_target(feature[c.PVF_FID].iloc[-1])):

    def get_target(self, k):
        """
        Gets the targets for feature k

        Parameters
        ----------
        k : str
            The identifier of the feature
        Returns
        -------
        The target for feature k
        """
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
        """
        Sets the max cost

        Parameters
        ----------
        cost : float
            The max allowed cost
        Returns
        -------
        None
        """
        self.max_cost = cost

    def set_min_cost(self, cost):
        """
        Sets the min cost

        Parameters
        ----------
        cost : float
            The min allowed cost
        Returns
        -------
        """
        self.min_cost = cost

    def set_blm_weight(self, blm):
        """
        Sets the weight for the blm

        Parameters
        ----------
            blm : float
        Returns
        -------
        None
        """
        self.blm_weight = blm
