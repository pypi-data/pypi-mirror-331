from typing import List, Dict

class BaseIndexer:
    """
    The common parent for all indexers.

    Contains basic parameters like language and top_k.
    """

    def __init__(self, config: dict):
        """
        Parameters
        ----------
        config : dict
            Base configuration dictionary. Expected keys (or their defaults) include:
              - language: the language code, e.g., "et" or "en"
              - top_k: number of keywords to extract (default: 5)
        """
        self.config = config
        self.language = config.get("language")
        self.top_k = config.get("top_k")

        if not self.language:
            raise ValueError("Language code is required for the indexer.")
        if not self.top_k:
            raise ValueError("Top_k (the number of keywords to find) is required for the indexer.")

    def find_keywords(self, text: str) -> List[Dict]:
        """
        Find or extract keywords from the input text.
        """
        raise NotImplementedError("Subclasses must implement this method.")