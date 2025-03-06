"""Defines the ArithmeticMeanCombiner."""

import numpy as np
from hiclass.probability_combiner.ProbabilityCombiner import ProbabilityCombiner
from typing import List


class ArithmeticMeanCombiner(ProbabilityCombiner):
    """Combine probabilities of multiple levels by taking their arithmetic mean."""

    def combine(self, proba: List[np.ndarray]):
        """Combine probabilities of each level with probabilities of previous levels.

        Calculate the arithmetic mean of node probabilities and the probabilities of its predecessors.
        """
        res = [proba[0]]
        sums = [proba[0]]
        for level in range(1, self.classifier.max_levels_):
            level_probs = np.zeros_like(proba[level])
            level_sum = np.zeros_like(proba[level])
            # find all predecessors of a node
            predecessors = self._find_predecessors(level)

            for node in predecessors.keys():
                index = self.classifier.class_to_index_mapping_[level][node]
                # find indices of all predecessors
                predecessor_indices = [
                    self.classifier.class_to_index_mapping_[level - 1][predecessor]
                    for predecessor in predecessors[node]
                ]
                # combine probabilities of all predecessors
                predecessors_combined_prob = np.sum(
                    [
                        sums[level - 1][:, pre_index]
                        for pre_index in predecessor_indices
                    ],
                    axis=0,
                )
                level_sum[:, index] += (
                    proba[level][:, index] + predecessors_combined_prob
                )
                level_probs[:, index] = level_sum[:, index] / (level + 1)

            res.append(level_probs)
            sums.append(level_sum)
        return self._normalize(res) if self.normalize else res
