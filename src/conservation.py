import pandas as pd
import networkx as nx

# TODO fix this class. Not very nice like this. Works though
class Conservation:

    def __init__(self, pu, species, puvspr, bounds=None):
        self.pu = pu
        self.species = species
        self.puvspr = puvspr
        self.bounds = bounds

    def set_pu_decision_vars(self, pux):
        self.pux = pux

