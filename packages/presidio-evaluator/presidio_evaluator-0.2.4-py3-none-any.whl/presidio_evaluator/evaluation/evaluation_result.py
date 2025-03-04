import json
from collections import Counter
from typing import List, Optional, Dict, Tuple

import pandas as pd

from presidio_evaluator.evaluation import ModelError


class EvaluationResult:
    def __init__(
        self,
        results: Counter,
        model_errors: Optional[List[ModelError]] = None,
        text: Optional[str] = None,
        pii_recall: Optional[float] = None,
        pii_precision: Optional[float] = None,
        pii_f: Optional[float] = None,
        n: Optional[int] = None,
        entity_recall_dict: Optional[Dict[str, float]] = None,
        entity_precision_dict: Optional[Dict[str, float]] = None,
        n_dict: Optional[Dict[str, int]] = None,
        tokens: Optional[List[str]] = None,
        actual_tags: Optional[List[str]] = None,
        predicted_tags: Optional[List[str]] = None
    ):
        """
        Holds the output of a comparison between ground truth and predicted
        :param results: List of objects of type Counter
        with structure {(actual, predicted) : count}
        :param model_errors: List of specific model errors for further inspection
        :param text: sample's full text (if used for one sample)
        :param pii_recall: Recall for all entities (PII or not)
        :param pii_precision: Precision for all entities (PII or not)
        :param pii_f: F measure for all entities (PII or not)
        :param n: Number of total entity tokens
        :param entity_recall_dict: Recall per entity
        :param entity_precision_dict: Precision per entity
        :param n_dict: Number of tokens per entity
        :param tokens: List of tokens
        :param actual_tags: List of actual tags
        :param predicted_tags: List of predicted tags
        """

        self.results = results
        self.model_errors = model_errors
        self.text = text

        self.pii_recall = pii_recall
        self.pii_precision = pii_precision
        self.pii_f = pii_f
        self.n = n
        self.entity_recall_dict = entity_recall_dict if entity_recall_dict else {}
        self.entity_precision_dict = (
            entity_precision_dict if entity_precision_dict else {}
        )
        self.n_dict = n_dict if n_dict else {}
        self.tokens = tokens
        self.actual_tags = actual_tags
        self.predicted_tags = predicted_tags

    def __str__(self):
        return_str = ""
        if not self.entity_precision_dict or not self.entity_recall_dict:
            return json.dumps(self.results)

        entities = self.n_dict.keys()

        row_format = "{:>20}{:>20.2%}{:>20.2%}{:>20}"
        header_format = "{:>20}" * 4
        return_str += str(
            header_format.format(
                *("Entity", "Precision", "Recall", "Number of samples")
            )
        )
        for entity in entities:
            return_str += "\n" + row_format.format(
                entity,
                self.entity_precision_dict[entity],
                self.entity_recall_dict[entity],
                self.n_dict[entity],
            )

        # add PII values
        return_str += "\n" + row_format.format(
            "PII",
            self.pii_precision,
            self.pii_recall,
            self.n,
        )

        return_str += f"\nPII F measure: {self.pii_f:.2%}"
        return return_str

    def __repr__(self):
        return f"stats={self.results}"

    def to_log(self) -> Dict:
        metrics_dict = {
            "pii_f": self.pii_f,
            "pii_recall": self.pii_recall,
            "pii_precision": self.pii_precision,
            "n": self.n,
        }
        if self.entity_precision_dict:
            metrics_dict.update(
                {
                    f"{ent}_precision": v
                    for (ent, v) in self.entity_precision_dict.items()
                }
            )
        if self.entity_recall_dict:
            metrics_dict.update(
                {f"{ent}_recall": v for (ent, v) in self.entity_recall_dict.items()}
            )
        if self.n:
            metrics_dict.update(self.n_dict)
        return metrics_dict

    def to_confusion_matrix(self) -> Tuple[List[str], List[List[int]]]:
        entities = list(self.n_dict.keys())
        if "O" in entities:
            entities = [ent for ent in entities if ent != "O"]
        entities = sorted(entities)
        entities.append("O")
        confusion_matrix = [[0] * len(entities) for _ in range(len(entities))]
        for i, actual in enumerate(entities):
            for j, predicted in enumerate(entities):
                confusion_matrix[i][j] = self.results[(actual, predicted)]

        return entities, confusion_matrix

    def to_confusion_df(self) -> pd.DataFrame:
        entities, confmatrix = self.to_confusion_matrix()

        conf_df = pd.DataFrame(confmatrix, columns=entities).set_axis(entities)

        precision_df = pd.DataFrame(self.entity_precision_dict, index=["precision"])
        recall_series = pd.Series(self.entity_recall_dict)

        # add precision numbers as the last row
        conf_df = pd.concat([conf_df, precision_df], axis=0)

        # add recall numbers as the last column
        conf_df["recall"] = recall_series
        # conf_df.set_index(["recall"], drop=False)
        return conf_df
