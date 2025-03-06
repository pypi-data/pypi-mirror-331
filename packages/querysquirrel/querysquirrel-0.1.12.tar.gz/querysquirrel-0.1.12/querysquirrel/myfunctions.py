import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import tqdm
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import f1_score, accuracy_score
from sklearn.preprocessing import LabelEncoder
from transformers import DistilBertModel, DistilBertTokenizer
from transformers import BertTokenizer, BertModel
from sentence_transformers import SentenceTransformer
import math
import os
import collections
import pandas as pd
import pyarrow
import dask.dataframe as dd
import numpy as np
from collections import Counter
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


class FullyConnected(nn.Module):
    """
    A simple Fully Connected Neural Network with one hidden layer.

    Args:
        input_size (int): Number of input features.
        hidden_size (int): Number of neurons in the hidden layer.
        num_layers (int): Number of output classes.

    Methods:
        forward(x): Forward pass of the network.
    """

    def __init__(self, input_size, hidden_size, num_layers):
        super(FullyConnected, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(p=0.1)
        self.maxpool = nn.MaxPool1d(kernel_size=2, stride=2)
        pooled_output_size = hidden_size // 2
        self.fc2 = nn.Linear(pooled_output_size, num_layers)

    def forward(self, x):
        """
        Performs forward pass through the network.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor after passing through the network.
        """
        x = torch.flatten(x, 1).float()
        x = F.relu(self.fc1(x))
        x = x.unsqueeze(1)
        x = self.maxpool(x)
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class MLPsoftmax(nn.Module):
    """
    A Multi-Layer Perceptron (MLP) classifier with softmax activation.

    Args:
        input_size (int): Number of input features.
        hidden_size (int): Number of neurons in the hidden layer.
        num_layers (int): Number of output classes.

    Methods:
        forward(x): Forward pass of the network.
    """

    def __init__(self, input_size, hidden_size, num_layers):
        super(MLPsoftmax, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(p=0.1)
        self.maxpool = nn.MaxPool1d(kernel_size=2, stride=2)
        pooled_output_size = hidden_size // 2
        self.fc2 = nn.Linear(pooled_output_size, num_layers)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        """
        Performs forward pass through the network.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor with softmax probabilities.
        """
        x = torch.flatten(x, 1).float()
        x = F.relu(self.fc1(x))
        x = x.unsqueeze(1)
        x = self.maxpool(x)
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.softmax(x)
        return x


class ESCIDataset(Dataset):
    """
    A PyTorch dataset class for embedding-based classification.

    Args:
        embeddings (pd.DataFrame): Dataframe containing embeddings.
        labels (pd.Series or list): Labels corresponding to embeddings.

    Methods:
        __len__(): Returns dataset length.
        __getitem__(idx): Returns embedding-label pair at a given index.
    """

    def __init__(self, embeddings, labels):
        self.embeddings = embeddings.values
        print(f'Shape of embeddings: {self.embeddings.shape}')
        self.labels = labels

    def __len__(self):
        """Returns the total number of samples."""
        return len(self.labels)

    def __getitem__(self, idx):
        """Returns a sample (embedding and label) from the dataset."""
        return self.embeddings[idx], self.labels[idx]


def generate_embeddings(texts, model, tokenizer, device):
    """
    Generates embeddings for a batch of input texts.

    Args:
        texts (list of str): List of input texts.
        model (transformers.PreTrainedModel): Transformer model for embedding.
        tokenizer (transformers.PreTrainedTokenizer): Tokenizer for model.
        device (str): Device to run inference (e.g., 'cuda' or 'cpu').

    Returns:
        np.ndarray: Array of text embeddings.
    """
    batch_size = 128
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        inputs = tokenizer(batch.tolist(), return_tensors='pt', padding=True, truncation=True, max_length=512)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)

        batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        embeddings.append(batch_embeddings)

    return np.vstack(embeddings)


def train_model(model, train_loader, criterion, optimizer, device, num_epochs=4):
    """
    Trains a neural network model.

    Args:
        model (torch.nn.Module): The model to be trained.
        train_loader (DataLoader): DataLoader for training data.
        criterion (torch.nn.Module): Loss function.
        optimizer (torch.optim.Optimizer): Optimization algorithm.
        device (str): Device to run training (e.g., 'cuda' or 'cpu').
        num_epochs (int, optional): Number of training epochs. Defaults to 4.

    Returns:
        None
    """
    model.train()
    for epoch in range(num_epochs):
        epoch_loss = 0
        for batch_idx, (embeddings, labels) in enumerate(train_loader):
            embeddings, labels = embeddings.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(embeddings.float())
            labels = labels.long()
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss / len(train_loader):.4f}")


def evaluate_model(test_loader, model, device):
    """
    Evaluates a trained model on test data.

    Args:
        test_loader (DataLoader): DataLoader for test data.
        model (torch.nn.Module): The trained model.
        device (str): Device to run evaluation (e.g., 'cuda' or 'cpu').

    Returns:
        float: F1 score (micro-average).
    """
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device).float()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    return f1_score(all_labels, all_preds, average='micro')


def compute_metrics(eval_pred):
    """
    Computes evaluation metrics including accuracy, F1-score, and perplexity.

    Args:
        eval_pred (transformers.EvalPrediction): Model predictions and labels.

    Returns:
        dict: Dictionary with accuracy, F1 score, and perplexity.
    """
    logits, labels = eval_pred.predictions, eval_pred.label_ids
    predictions = np.argmax(logits, axis=-1)
    loss = eval_pred.metrics["eval_loss"]

    accuracy = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average="weighted")
    perplexity = math.exp(loss)

    return {
        "perplexity": perplexity,
        "accuracy": accuracy,
        "f1": f1
    }

 def get_unique_replacements(text, top_tokens, tokenizer):
    """
    Filters out duplicate word replacements in the final output.

    Args:
        text (str): The original text with a masked token.
        top_tokens (list): List of top token predictions from the model.
        tokenizer (transformers.PreTrainedTokenizer): Tokenizer used for decoding.

    Returns:
        list: List of unique replacement variations of the input text.
    """
    seen_replacements = set()
    results = []

    for token in top_tokens:
        decoded_token = tokenizer.decode([token]).strip()
        if decoded_token not in seen_replacements:
            seen_replacements.add(decoded_token)
            result = text.replace(tokenizer.mask_token, decoded_token)
            results.append(result)

    return results


def generate_predictions(queries, product_titles, k, batch_size, tokenizer, device, model):
    """
    Generates masked language model predictions for product search.

    Args:
        queries (list of str): List of search queries.
        product_titles (list of str): List of product titles.
        k (int): Number of top predictions to consider.
        batch_size (int): Batch size for processing.
        tokenizer (transformers.PreTrainedTokenizer): Tokenizer to process input.
        device (str): Device to run inference ('cpu' or 'cuda').
        model (transformers.PreTrainedModel): The masked language model.

    Returns:
        list: List of dictionaries containing query results with predicted words.
    """
    all_results = []

    for query in queries:
        query_results = []
        seen_titles = set()

        for i in range(0, len(product_titles), batch_size):
            batch_titles = product_titles[i:i + batch_size]
            input_texts = [f"{query} <mask> {title}" for title in batch_titles]
            inputs = tokenizer(input_texts, padding=True, truncation=True, return_tensors='pt')
            inputs = {key: val.to(device) for key, val in inputs.items()}

            model.eval()

            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits

            for j in range(len(batch_titles)):
                mask_index = (inputs['input_ids'][j] == tokenizer.mask_token_id).nonzero(as_tuple=True)[0]

                if mask_index.numel() == 0:
                    print(f"No mask token found for input: {input_texts[j]}")
                    continue

                mask_logits = logits[j, mask_index.item()]
                top_k_indices = torch.topk(mask_logits, k).indices
                predicted_tokens = tokenizer.convert_ids_to_tokens(top_k_indices)

                product_title = batch_titles[j]
                if product_title not in seen_titles:
                    seen_titles.add(product_title)
                    query_results.append({
                        'query': query,
                        'product_title': product_title,
                        'predicted_tokens': predicted_tokens,
                        'logits': mask_logits
                    })

        query_results.sort(key=lambda x: x['logits'].max().item(), reverse=True)
        top_k_results = []

        for result in query_results:
            if len(top_k_results) < k:
                if result['product_title'] not in {r['product_title'] for r in top_k_results}:
                    top_k_results.append(result)

        all_results.extend(top_k_results[:k])

    return all_results


def process_text(batch, puncts):
    """
    Removes punctuation from a batch of text.

    Args:
        batch (dict): Dictionary containing a 'text' key with a list of strings.
        puncts (str): String containing punctuation characters to remove.

    Returns:
        dict: Dictionary with processed text.
    """
    processed_texts = [''.join(ch for ch in str(text) if ch not in puncts) for text in batch['text']]
    return {'processed_text': processed_texts}


def tokenize_function(examples, tokenizer):
    """
    Tokenizes text using the provided tokenizer.

    Args:
        examples (dict): Dictionary with key "processed_text".
        tokenizer (transformers.PreTrainedTokenizer): Tokenizer object.

    Returns:
        dict: Tokenized representation of input text.
    """
    result = tokenizer(examples["processed_text"])
    if tokenizer.is_fast:
        result["word_ids"] = [result.word_ids(i) for i in range(len(result["input_ids"]))]
    return result


def whole_word_masking_data_collator(features):
    """
    Performs whole-word masking for masked language modeling.

    Args:
        features (list of dict): List of feature dictionaries containing word IDs.

    Returns:
        dict: Dictionary containing modified input features with masked words.
    """
    for feature in features:
        word_ids = feature.pop("word_ids")
        mapping = collections.defaultdict(list)
        current_word_index = -1
        current_word = None

        for idx, word_id in enumerate(word_ids):
            if word_id is not None:
                if word_id != current_word:
                    current_word = word_id
                    current_word_index += 1
                mapping[current_word_index].append(idx)

        mask = np.random.binomial(1, (len(mapping),))
        input_ids = feature["input_ids"]
        labels = feature["labels"]
        new_labels = [-100] * len(labels)

        for word_id in np.where(mask)[0]:
            word_id = word_id.item()
            for idx in mapping[word_id]:
                new_labels[idx] = labels[idx]
                input_ids[idx] = tokenizer.mask_token_id

        feature["labels"] = new_labels

    return default_data_collator(features)


def generate_embeddings_finetuned(texts, device, tokenizer_ft, model_ft):
    """
    Generates embeddings using a fine-tuned model.

    Args:
        texts (list of str): List of input texts.
        device (str): Device to run inference ('cpu' or 'cuda').
        tokenizer_ft (transformers.PreTrainedTokenizer): Tokenizer for fine-tuned model.
        model_ft (transformers.PreTrainedModel): Fine-tuned transformer model.

    Returns:
        np.ndarray: Array of text embeddings.
    """
    batch_size = 64
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        inputs = tokenizer_ft(batch.tolist(), return_tensors='pt', padding=True, truncation=True, max_length=512)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = model_ft(**inputs, output_hidden_states=True)
            last_hidden_state = outputs.hidden_states[-1]

        batch_embeddings = last_hidden_state[:, 0, :].cpu().numpy()
        embeddings.append(batch_embeddings)
        torch.cuda.empty_cache()

    return np.vstack(embeddings)
   
