from collections import Counter
from pathlib import Path
from typing import List

import numpy as np
from scipy.spatial.distance import jensenshannon

class Map:
    """Constructs a map object from a 2D representation, i.e. a list of strings."""
    def __init__(self, map: List[str]):
        self.map = map
    def flatten(self):
        return "".join(self.map)

def hamming_distance(map1: Map, map2: Map) -> int:
    """Returns the Hamming distance between two maps. Lower values indicate more similar maps."""
    return sum([1 for i, j in zip(map1.flatten(), map2.flatten()) if i != j])

def js_divergence(map1: Map, map2: Map) -> float:
    """Returns the Jensen-Shannon divergence between two maps. Lower values indicate more similar maps."""
    def map_to_hist(map: Map):
        return Counter(map.flatten())

    hist1 = map_to_hist(map1)
    hist2 = map_to_hist(map2)
    keys = set(hist1.keys()) | set(hist2.keys())
    hist1 = np.array([hist1[key] for key in keys])
    hist2 = np.array([hist2[key] for key in keys])
    return jensenshannon(hist1, hist2)

if __name__ == "__main__":
    map1 = Map(Path("basic_pipeline/evaluation/maps/sample1.txt").read_text().splitlines())
    map2 = Map(Path("basic_pipeline/evaluation/maps/sample2.txt").read_text().splitlines())
    print(hamming_distance(map1, map2))
    print(js_divergence(map1, map2))