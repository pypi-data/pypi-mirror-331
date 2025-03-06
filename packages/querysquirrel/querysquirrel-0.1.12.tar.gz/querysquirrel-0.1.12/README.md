<img src="https://raw.githubusercontent.com/willarmstrong1/querysquirrel_library/main/8b98b24c-d410-4238-b862-6a6f0ff5de0a.webp" alt="QuerySquirrel Logo" width="400"/>


# QuerySquirrel
QuerySquirrel is a Python library for building, training, and testing NLP models using PyTorch and the Hugging Face Transformers library. It simplifies model development by providing high-level utilities for data handling, model training, evaluation, and fine-tuning.
---

## Table of Contents
- [Features](#features)
- [Installation](#installation)
  - [Install from PyPI](#install-from-pypi)
  - [Dependencies](#dependencies)
- [Usage](#usage)
  - [Quick Start](#quick-start)
- [Contributing](#contributing)
- [License](#license)

---

## Features
- **Easy Dataset Handling**: Load and preprocess text data efficiently.
- **Model Training and Fine-tuning**: Train Transformer-based models with minimal code.
- **Evaluation Metrics**: Built-in utilities for assessing model performance.
- **Custom Model Support**: Extend existing models or integrate your own architectures.
- **Integration with PyTorch and Transformers**: Seamless use of popular NLP frameworks.

## Installation
To install QuerySquirrel on your local machine, follow these steps:

### Install from PyPI
Run the following command to install QuerySquirrel via pip:

```sh
pip install querysquirrel
```
### Dependencies
QuerySquirrel requires Python 3.7+ and the following libraries:
- PyTorch
- Transformers (Hugging Face)
- Datasets
- NumPy
- scikit-learn
- torch
- torch.nn
- torch.nn.functional
- torch.optim
- tqdm
- torch.utils.data
- sklearn.metrics
- sklearn.preprocessing
- transformers
- sentence-transformers
- math
- os
- collections
- pandas
- pyarrow
- dask.dataframe
- numpy
- Counter (from collections)
- seaborn
- matplotlib

## Usage
Once installed, you can import QuerySquirrel in your Python projects like this:

```python
from querysquirrel import myfunctions as qs
```

### Quick Start
Here's an example of how to use QuerySquirrel to train a text classification model:

```python
import querysquirrel
from querysquirrel import myfunctions as qs

# Load dataset
data = qs.load_dataset("imdb")

# Preprocess data
data = qs.tokenize(data, model_name="bert-base-uncased")

# Train model
model = qs.train(data, model_name="bert-base-uncased", epochs=3)

# Evaluate model
results = qs.evaluate(model, data["test"])
print("Evaluation Results:", results)
```

## Contributing
We welcome contributions! To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and write tests.
4. Submit a pull request.

## License
QuerySquirrel is released under the MIT License.

