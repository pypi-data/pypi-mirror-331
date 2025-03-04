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


## 📚 Documentation

<details><summary>Click to expand</summary>

Documentation can be found [here](DOCUMENTATION.md).

</details>

## 📝 Testing

<details><summary>Click to expand</summary>

Run the test suite:
```bash
python -m pytest -v tests
```

</details>

