#!/usr/bin/env python
from abc import ABC, abstractmethod
import numpy as np

class AbstractScore(ABC):

    def __init__(self):
        self._allRVDistributions = []
        
    @abstractmethod
    def score(self, graphPath: GraphPath) -> float:
        pass

    def setAllRVDistributions(self, allRVDistributions: np.ndarray) -> None:
        self._allRVDistributions = allRVDistributions