from typing import List, Dict

from rara_subject_indexer.indexers.base_indexer import BaseIndexer
from rara_subject_indexer.unsupervised.keyword_extractor import KeywordExtractor


class RakunIndexer(BaseIndexer):
    """
    An unsupervised indexer that uses the Rakun (keyword extraction) logic.

    The configuration should include:
      - language: the language code.
      - top_k: how many keywords to extract (optional; default is 5).

    No model_path is required because the extractor is already part of the library.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.extractor = KeywordExtractor()
        self.entity_type = "Teemamärksõnad"

    def find_keywords(self, text: str) -> List[Dict]:
        """
        Predict keywords using the unsupervised Rakun-based extractor.

        Parameters
        ----------
        text : str
            Input text.

        Returns
        -------
        List[Dict]
            A list of dictionaries, each with keys "keyword", "entity_type", and "score".
        """
        keywords = self.extractor.predict(text, lang_code=self.language, top_n=self.top_k, **self.config)
        return [{"keyword": kw, "entity_type": self.entity_type, "score": score} for kw, score in keywords]