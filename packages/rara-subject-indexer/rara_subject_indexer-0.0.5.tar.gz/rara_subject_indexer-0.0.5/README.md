# Subject Indexers

This repository provides two pipelines:

1) for processing text and label files in order to train and evaluate an Omikuji model. 
It includes text lemmatization, TF-IDF feature extraction, 
label binarization. The system is designed for extreme multilabel classification.
2) for processing text and extracting topic keywords using unsupervised methods.
Optionally multiword keyword detection can be enabled by using a pretrained PhraserModel.
Spelling mistakes can be automatically corrected by enabling SpellCorrector.


## ⚙️ Installation Guide


<details><summary>Click to expand</summary>

### Preparing the Environment

1. **Set Up Your Python Environment**  
   Ensure you have Python **3.10** or above installed.

2. **Install Required Dependencies**  
   Install the required dependencies using:
    ```bash
    pip install -r requirements.txt
    ```
   
### Installation via PyPI

1. **Install the Package**  
   You can install the package using:
    ```bash
    pip install rara-subject-indexer
    ```

</details>

## 📝 Testing

<details><summary>Click to expand</summary>

Run the test suite:
```bash
python -m pytest -v tests
```

</details>

## 📚 Documentation

<details><summary>Click to expand</summary>

### Main Classes

The `rara-subject-indexer` library organizes subject indexing into a few key classes. At its core are the abstract `BaseIndexer` and two concrete indexers: `OmikujiIndexer` for supervised keyword extraction and `RakunIndexer` for unsupervised keyword extraction. 
The `OmikujiIndexer` class uses pre-trained Omikuji models, which can be downloaded with the `Downloader` utility class.

---

#### 🔍 Downloader Class

##### Overview

The `Downloader` class downloads pretrained models and other relevant data from Google Drive. It accepts a shareable URL or file ID and automatically extracts zip archives after downloading.

##### Key Function

<details><summary>Click to expand</summary>

 `download()`

- **Purpose:** Downloads the file from Google Drive and extracts it if it is a zip archive.
- **Usage:** Call this method on an instance of the `Downloader` class to perform the download and extraction.

</details>

##### Example Usage

<details><summary>Click to expand</summary>

[Click to copy GDrive URLs of Omikuji models here.](https://drive.google.com/drive/folders/1yKgedNCe9fNAQXvjhiJEo7JI-Yk0ImSD)

```python
from rara_subject_indexer.utils.downloader import Downloader

drive_url = "https://drive.google.com/file/d/EXAMPLE_FILE_ID/view?usp=drive_link"
downloader = Downloader(drive_url, output_dir="/path/to/save/downloads")
downloader.download()
```

</details>

---

#### 🔍 BaseIndexer Class

##### Overview

`BaseIndexer` serves as the common parent for all indexers. It defines basic configuration parameters (such as language and the number of keywords to extract) and provides the interface for keyword extraction. Subclasses must implement the `find_keywords()` method.

##### Parameters

<details><summary>Click to expand</summary>

| Name    | Type | Optional | Default | Description                                                                 |
|---------|------|----------|---------|-----------------------------------------------------------------------------|
| config  | dict | False    | None    | Base configuration dictionary with keys like `language` (e.g., `"et"` or `"en"`) and `top_k` (number of keywords to extract). |

</details>

##### Key Functions

<details><summary>Click to expand</summary>

1. `find_keywords(text: str) -> List[Dict]`

   Abstract method for finding or extracting keywords from the input text.  
   **Returns:** List of dictionaries representing keyword results (e.g., each with keys `"keyword"`, `"entity_type"`, and `"score"`).

</details>

---

#### 🔍 OmikujiIndexer Class

##### Overview

`OmikujiIndexer` is a supervised indexer that leverages an Omikuji model for keyword prediction. During initialization, it loads a pre-trained model (via a specified model path) and validates that the model’s language matches the indexer configuration.

##### Config Parameters

<details><summary>Click to expand</summary>

| Name       | Type | Optional | Default | Description                                                                 |
|------------|------|----------|---------|-----------------------------------------------------------------------------|
| language   | str  | False    | None    | Language of the input text (e.g., `"et"` or `"en"`).                       |
| top_k      | int  | False    | None    | Number of keywords to extract.                                             |
| model_path | str  | False    | None    | Path to the Omikuji model file.                                            |

</details>

##### Key Functions

<details><summary>Click to expand</summary>

1. `find_keywords(text: str) -> List[Dict]`

   Uses the loaded Omikuji model to predict keywords for the provided text.  
   **Returns:** A list of dictionaries containing `"keyword"`, `"entity_type"`, and `"score"`.

</details>

##### Usage Example

<details><summary>Click to expand</summary>

```python
from rara_subject_indexer.indexers.omikuji_indexer import OmikujiIndexer

config = {
    "language": "en",
    "top_k": 5,
    "model_path": "/path/to/omikuji_model"  # Use Downloader to download a model
}

indexer = OmikujiIndexer(config)
keywords = indexer.find_keywords("Sample input text for keyword extraction.")
print(keywords)
```

</details>

---

#### 🔍 RakunIndexer Class

##### Overview

`RakunIndexer` provides unsupervised keyword extraction using Rakun’s internal extraction logic. It does not require a separate model file since the extractor is part of the library. The default entity type for keywords is set to `"Teemamärksõnad"`.

##### Config Parameters

<details><summary>Click to expand</summary>

| Name             | Type | Optional | Default | Description                                                                 |
|------------------|------|----------|---------|-----------------------------------------------------------------------------|
| language         | str  | False    | None    | Language of the input text (e.g., `"et"` or `"en"`).                       |
| top_k            | int  | False    | None    | Number of keywords to extract.                                             |
| merge_threshold  | float| True     | 0.0     | Threshold for merging similar keywords.                                    |
| use_phraser      | bool | True     | False   | Whether to use a Phraser model for multi-word keyword detection.           |
| correct_spelling | bool | True     | False   | Whether to correct spelling mistakes in the input text.                    |
| preserve_case    | bool | True     | True    | Whether to preserve the case of extracted keywords.                        |
| max_uppercase    | int  | True     | 2       | Maximum number of uppercase characters in a keyword.                       |
| min_word_frequency | int | True    | 3       | Minimum word frequency for keyword extraction.                             |

</details>

##### Key Functions

<details><summary>Click to expand</summary>

1. `find_keywords(text: str) -> List[Dict]`

   Uses Rakun-based unsupervised extraction to predict keywords from the input text.  
   **Returns:** A list of dictionaries where each dictionary contains `"keyword"`, `"entity_type"`, and `"score"`.

</details>

##### Usage Example

<details><summary>Click to expand</summary>

```python
from rara_subject_indexer.indexers.rakun_indexer import RakunIndexer

config = {
   "language": "et",
   "top_k": 5,
   "merge_threshold": 0.0,      # Optional
   "use_phraser": False,        # Optional
   "correct_spelling": False,   # Optional
   "preserve_case": True,       # Optional
   "max_uppercase": 2,          # Optional
   "min_word_frequency": 3      # Optional
}

indexer = RakunIndexer(config)
keywords = indexer.find_keywords("Sample input text for keyword extraction.")
print(keywords)
```

</details>

---
 

### Training Supervised and Unsupervised Models

If necessary, you can train the supervised and unsupervised models from scratch using the provided pipelines. 
The training process involves reading text and label files, preprocessing the text, and training the models 
using the extracted features.

<details><summary>Click to expand</summary>

#### Training an Omikuji Model for Supervised Keyword Extraction

<details><summary>Click to expand</summary>

A sample code snippet to train and predict using the Omikuji model is provided below:

```python
from rara_subject_indexer.supervised.omikuji_model import OmikujiModel

model = OmikujiModel()

model.train(
    text_file="texts.txt",  # File with one document per line
    label_file="labels.txt",  # File with semicolon-separated labels for each document
    language="et",  # Language of the text, in ISO 639-1 format
    entity_type="Teemamärksõnad",  # Entity type for the keywords
    lemmatization_required=True, # (Optional) Whether to lemmatize the text - only set False if text_file is already lemmatized
    max_features=20000,  # (Optional) Maximum number of features for TF-IDF extraction
    keep_train_file=False,  # (Optional) Whether to retain intermediate training files
    eval_split=0.1  # (Optional) Proportion of the dataset used for evaluation
)

predictions = model.predict(
    text="Kui Arno isaga koolimajja jõudis",  # Text to classify
    top_k=3  # Number of top predictions to return
)  # Output: [('koolimajad', 0.262), ('isad', 0.134), ('õpilased', 0.062)]
```

#### 📂 Data Format

The files provided to the train function should be in the following format:
- A **text file** (`.txt`) where each line is a document.
    ```
    Document one content.
    Document two content.
    ```
- A **label file** (`.txt`) where each line contains semicolon-separated labels corresponding to the text file.
    ```
    label1;label2
    label3;label4
    ```

#### 🛠 Components Overview

| Component | Description |
|-----------|-------------|
| `DataLoader` | Handles reading and preprocessing parallel text-label files. |
| `TfidfFeatureExtractor` | Extracts TF-IDF features from preprocessed text files. |
| `LabelBinarizer` | Encodes labels into a sparse binary matrix. |
| `TextPreprocessor` | Handles text preprocessing, including lemmatization. |
| `OmikujiModel` | Handles model training using Omikuji, a scalable extreme classification library. |
| `OmikujiHelpers` | Helper functions for Omikuji model training and evaluation. |

</details>

---

#### Training Phraser for Unsupervised Keyword Extraction

<details><summary>Click to expand</summary>

A sample code snippet to train and predict using the Phraser model is provided below:

```python
from rara_subject_indexer.unsupervised.phraser_model import PhraserModel

model = PhraserModel()

model.train(
    train_data_path=".../train.txt",  # File with one document per line, text should be lemmatised.
    lang_code="et",  # Language of the text, in ISO 639-1 format
    min_count=5,  # (Optional) Minimum word frequency for phrase formation.
    threshold=10.0  # (Optional) Score threshold for forming phrases.
)

predictions = model.predict(
    text="'vabariik aastapäev sööma kiluvõileib'",  # Lemmatised text for phrase detection
)  # Output: ['vabariik_aastapäev', 'sööma', kiluvõileib']
```

#### 📂 Data Format

The file provided to the PhraserModel train function should be in the following format:

- A **text file** (`.txt`) where each line is a document.
    ```
    Document one content.
    Document two content.
    ```

#### 🛠 Components Overview

| Component          | Description                                                                                                                                                                                                           |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `KeywordExtractor` | Extracts topic keywords from the text using unsupervised methods. Optionally multi-word keywords can be found using a pretrained PhraserModel. Spelling mistakes can be automatically corrected using SpellCorrector. |
| `PhraserModel`     | Handles Gensim Phraser model training and evaluation.                                                                                                                                                                 |
| `SpellCorrector`   | Handles spelling correction logic using SymSpell.                                                                                                                                                                     |                                                         |

</details>
</details>
</details>