import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import numpy as np
from sklearn.metrics import accuracy_score


# Define FullyConnected class
class FullyConnected(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(FullyConnected, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(p=0.1)
        self.maxpool = nn.MaxPool1d(kernel_size=2, stride=2)
        pooled_output_size = hidden_size // 2
        self.fc2 = nn.Linear(pooled_output_size, num_layers)

    def forward(self, x):
        x = torch.flatten(x, 1).float()
        x = F.relu(self.fc1(x))
        x = x.unsqueeze(1)
        x = self.maxpool(x)
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


# Define MLPsoftmax class
class MLPsoftmax(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(MLPsoftmax, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(p=0.1)
        self.maxpool = nn.MaxPool1d(kernel_size=2, stride=2)
        pooled_output_size = hidden_size // 2
        self.fc2 = nn.Linear(pooled_output_size, num_layers)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = torch.flatten(x, 1).float()
        x = F.relu(self.fc1(x))
        x = x.unsqueeze(1)
        x = self.maxpool(x)
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.softmax(x)
        return x


# Define ESCIDataset class
class ESCIDataset(Dataset):
    def __init__(self, embeddings, labels):
        self.embeddings = embeddings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.embeddings[idx], self.labels[idx]


# Define test functions
def test_fully_connected():
    print("Testing FullyConnected...")
    model = FullyConnected(input_size=100, hidden_size=50, num_layers=10)
    dummy_input = torch.rand(5, 100)  # Batch size 5, input_size 100
    output = model(dummy_input)
    assert output.shape == (5, 10), f"Expected output shape (5, 10), got {output.shape}"
    print("FullyConnected passed.")


def test_mlp_softmax():
    print("Testing MLPsoftmax...")
    model = MLPsoftmax(input_size=100, hidden_size=50, num_layers=10)
    dummy_input = torch.rand(5, 100)
    output = model(dummy_input)
    assert output.shape == (5, 10), f"Expected output shape (5, 10), got {output.shape}"
    assert torch.allclose(output.sum(dim=1), torch.tensor([1.0] * 5), atol=1e-6), "Softmax outputs do not sum to 1."
    print("MLPsoftmax passed.")


def test_escidataset():
    print("Testing ESCIDataset...")
    embeddings = torch.rand(10, 100)
    labels = torch.randint(0, 2, (10,))
    dataset = ESCIDataset(embeddings, labels)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=False)
    batch = next(iter(dataloader))
    assert batch[0].shape == (2, 100), "Unexpected shape for embeddings"
    assert batch[1].shape == (2,), "Unexpected shape for labels"
    print("ESCIDataset passed.")


def test_training_loop():
    print("Testing training loop...")
    embeddings = torch.rand(10, 100)
    labels = torch.randint(0, 2, (10,))
    dataset = ESCIDataset(embeddings, labels)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

    model = FullyConnected(input_size=100, hidden_size=50, num_layers=2)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    for epoch in range(1):  # One epoch for testing
        model.train()
        for batch in dataloader:
            optimizer.zero_grad()
            outputs = model(batch[0].float())
            loss = criterion(outputs, batch[1])
            loss.backward()
            optimizer.step()

    print("Training loop passed.")


def test_evaluation_loop():
    print("Testing evaluation loop...")
    embeddings = torch.rand(10, 100)
    labels = torch.randint(0, 2, (10,))
    dataset = ESCIDataset(embeddings, labels)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=False)

    model = MLPsoftmax(input_size=100, hidden_size=50, num_layers=2)
    predictions, true_labels = [], []

    model.eval()
    with torch.no_grad():
        for batch in dataloader:
            outputs = model(batch[0].float())
            preds = torch.argmax(outputs, dim=1).numpy()
            predictions.extend(preds)
            true_labels.extend(batch[1].numpy())

    acc = accuracy_score(true_labels, predictions)
    print(f"Accuracy: {acc}")
    assert 0 <= acc <= 1, "Accuracy out of bounds"
    print("Evaluation loop passed.")


if __name__ == "__main__":
    test_fully_connected()
    test_mlp_softmax()
    test_escidataset()
    test_training_loop()
    test_evaluation_loop()
