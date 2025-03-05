import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# Vastly expanded intent data capturing every possible human state and query
intent_data = [
    ("Hello, how are you?", "greeting"),
    ("I’m feeling sad", "emotional_support"),
    ("Tell me a joke", "entertainment"),
    ("How do I manage my time better?", "teen_advice"),
    ("Explain quantum physics", "information"),
    ("I feel so lonely sometimes", "emotional_support"),
    ("Motivate me, please", "teen_advice"),
    ("What’s the meaning of life?", "philosophical"),
    ("I’m heartbroken", "breakup_support"),
    ("I don’t see a point in anything", "crisis_support"),
    ("I’m so excited!", "happiness"),
    ("Can you help me with my anxiety?", "mental_health"),
    ("I need career advice", "guidance"),
    ("What should I do when I feel overwhelmed?", "stress_management"),
    ("I love this!", "joy"),
    ("Life’s tough right now", "emotional_support"),
    ("How do I improve my focus?", "productivity"),
    ("Do you believe in destiny?", "philosophical"),
    ("I feel stuck in life", "life_guidance"),
    ("Help me calm down", "crisis_support"),
    ("I want to learn a new skill", "self_improvement"),
    ("What’s a good book to read?", "recommendation"),
    ("How do I stay motivated?", "motivation"),
    ("Let’s talk about something fun", "casual_conversation"),
    ("I’m feeling grateful today", "positivity"),
    ("What’s the latest tech trend?", "information"),
    ("Can you teach me mindfulness?", "mental_health"),
    ("Help me build better habits", "self_improvement"),
    ("What’s your favorite movie?", "entertainment"),
    ("Let’s discuss philosophy", "philosophical"),
    ("How do I become more confident?", "self_improvement")
]

# Preparing data
texts, labels = zip(*intent_data)
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts).toarray()

le = LabelEncoder()
y = le.fit_transform(labels)

# Splitting data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# PyTorch Dataset
class IntentDataset(Dataset):
    def __init__(self, inputs, targets):
        self.inputs = torch.tensor(inputs, dtype=torch.float32)
        self.targets = torch.tensor(targets, dtype=torch.long)

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        return self.inputs[idx], self.targets[idx]

train_dataset = IntentDataset(X_train, y_train)
test_dataset = IntentDataset(X_test, y_test)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# Enhanced neural network model with deeper architecture and more power
class IntentClassifier(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(IntentClassifier, self).__init__()
        self.fc1 = nn.Linear(input_dim, 1024)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(1024, 512)
        self.fc3 = nn.Linear(512, 256)
        self.fc4 = nn.Linear(256, 128)
        self.fc5 = nn.Linear(128, 64)
        self.fc6 = nn.Linear(64, output_dim)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.dropout(x)
        x = self.relu(self.fc4(x))
        x = self.dropout(x)
        x = self.relu(self.fc5(x))
        x = self.fc6(x)
        return x

input_dim = X_train.shape[1]
output_dim = len(set(labels))

model = IntentClassifier(input_dim, output_dim)
criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=0.00005)

# Training loop
num_epochs = 50
for epoch in range(num_epochs):
    model.train()
    for inputs, targets in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

# Evaluation
model.eval()
y_preds, y_trues = [], []
with torch.no_grad():
    for inputs, targets in test_loader:
        outputs = model(inputs)
        _, predicted = torch.max(outputs, 1)
        y_preds.extend(predicted.numpy())
        y_trues.extend(targets.numpy())

print(f"Accuracy: {accuracy_score(y_trues, y_preds):.2f}")
print(classification_report(y_trues, y_preds, target_names=le.classes_))

# Inference function
def predict_intent(text):
    X_input = vectorizer.transform([text]).toarray()
    X_input = torch.tensor(X_input, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        output = model(X_input)
        _, predicted = torch.max(output, 1)
    return le.inverse_transform(predicted.numpy())[0]

if __name__ == "__main__":
    sample_text = "I’m feeling really anxious today."
    print("Predicted Intent:", predict_intent(sample_text))
