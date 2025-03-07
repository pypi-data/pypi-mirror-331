from dataclasses import dataclass
from abc import ABC, abstractmethod
import numpy as np
import networkx as nx

@dataclass(frozen=True)
class Typedef(ABC):
    @property
    @staticmethod
    @abstractmethod
    def type() -> type:
        pass


class QuboTypedef(Typedef):
    type = dict

class IsingTypedef(Typedef):
    type = dict

class WeightMatrix(Typedef):
    type = np.ndarray

class NxGraph(Typedef):
    type = nx.Graph
