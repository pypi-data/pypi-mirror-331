import importlib.resources


def load_lines_from_resource(package: str, resource: str) -> list[str]:
    """
    Load lines from a packaged resource file into a list.

    Parameters
    ----------
    package : str
        The package where the resource is located.
    resource : str
        The resource file name.

    Returns
    -------
    list[str]
        A list of strings from the resource file.
    """
    resource_path = importlib.resources.files(package).joinpath(resource)
    with resource_path.open(encoding="utf-8") as file:
        return [line.strip() for line in file]

# Stopwords for supported languages
SUPPORTED_STOPWORDS = {
    "en": load_lines_from_resource("rara_subject_indexer", "rakun_resources/english-stopwords.txt"),
    "et": load_lines_from_resource("rara_subject_indexer", "rakun_resources/estonian-stopwords-lemmas.txt"),
}

# Stopwords for supported languages used for phrase detection
SUPPORTED_STOPWORDS_PHRASER = {
    "en": load_lines_from_resource("rara_subject_indexer", "rakun_resources/english-stopwords.txt"),
    "et": load_lines_from_resource("rara_subject_indexer", "rakun_resources/estonian-stopwords.txt"),
}

# Supported Phraser model paths
SUPPORTED_PHRASER_MODEL_PATHS = {
    #"en": os.path.join(get_data_dir(), "models", "unsupervised", "model_name.model"),
    "et": {
        "package": "rara_subject_indexer",
        "resource": "data/et_phraser_train_data.txt"
    },
}

# Supported languages for using stemmer
SUPPORTED_STEMMER_LANGUAGES = {"en": "english"}
SENTENCE_SPLIT_REGEX = r"(?<!\d\.\d)(?<!\w\.\w)(?<=\.|\?|!)\s"
URL_REGEX = r"(?i)(https?://\S+|www\.\S+|doi(:|\.org/)\s*\S+)"
EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b"

# Spell check dictionary config
# Spell check will use default values term_index=0, count_index=1, separator=" unless redefined here
SPELL_CHECK_DICTIONARIES_CONFIG = {
    "et": {
        "package": "rara_subject_indexer",
        "resource": "rakun_resources/et_frequency_lemmas.txt",
        "term_index": 1,
        "count_index": 0,
        "separator": " "
    },
    "en": {
        "package": "rara_subject_indexer",
        "resource": "rakun_resources/en_full.txt",
    },
}