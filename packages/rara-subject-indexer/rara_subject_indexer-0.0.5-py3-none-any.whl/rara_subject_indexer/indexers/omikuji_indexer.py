import logging
import os
from typing import List, Dict

from rara_subject_indexer.indexers.base_indexer import BaseIndexer
from rara_subject_indexer.supervised.omikuji_model import OmikujiModel

logger = logging.getLogger(__name__)


class OmikujiIndexer(BaseIndexer):
    """
    A supervised indexer that wraps an Omikuji model.

    The configuration should include:
      - model_path: local path to the downloaded Omikuji model artifacts.
      - top_k: how many keywords to extract (optional; default is 5).

    The language is retrieved from the model's configuration during load.
    """

    def __init__(self, config: dict):
        """
        Initialize the Omikuji indexer by loading the model.
        """
        super().__init__(config)

        model_path = config.get("model_path")
        if not model_path or not os.path.exists(model_path):
            raise ValueError("Invalid or missing 'model_path' for Omikuji model.")
        logger.info(f"Loading Omikuji model from {model_path}")

        self.model = OmikujiModel(model_artifacts_path=model_path)
        if self.language != self.model.preprocessor.language:
            raise ValueError(
                f"Model language '{self.model.preprocessor.language}' does not match indexer language '{self.language}'"
            )

        self.entity_type = self.model.entity_type

    def find_keywords(self, text: str) -> List[Dict]:
        """
        Predict keywords using the loaded Omikuji model.

        Parameters
        ----------
        text : str
            Input text.

        Returns
        -------
        List[Dict]
            A list of dictionaries, each with keys "keyword", "entity_type", and "score".
        """
        predictions = self.model.predict(text, top_k=self.top_k)
        results = []
        for label, score in predictions:
            results.append({
                "keyword": label,
                "entity_type": self.entity_type,
                "score": score
            })
        return results