import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import requests

class CoffeeAI:
    def __init__(self, model=None, api_key=None):
        self.api_key = api_key
        self.model = model or self.create_model()

        if api_key and not self.validate_key(api_key):
            raise ValueError("Invalid API Key")

    def create_model(self):
        """Создание модели с использованием PyTorch"""
        class SimpleNN(nn.Module):
            def __init__(self):
                super(SimpleNN, self).__init__()
                self.fc1 = nn.Linear(4, 128)  # 4 input features
                self.fc2 = nn.Linear(128, 64)
                self.fc3 = nn.Linear(64, 1)
                self.relu = nn.ReLU()
                self.sigmoid = nn.Sigmoid()

            def forward(self, x):
                x = self.relu(self.fc1(x))
                x = self.relu(self.fc2(x))
                x = self.sigmoid(self.fc3(x))
                return x
        
        return SimpleNN()

    def validate_key(self, api_key):
        """Проверка ключа через сервер."""
        response = requests.post('http://long-time.ru:5007/validate_key', json={'key': api_key})
        return response.status_code == 200

    def train(self, X_train, y_train, epochs=10, batch_size=32):
        """Обучение модели"""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(device)

        # Преобразование входных данных в тензоры PyTorch
        X_train_tensor = torch.tensor(X_train, dtype=torch.float32).to(device)
        y_train_tensor = torch.tensor(y_train, dtype=torch.float32).to(device)

        criterion = nn.BCELoss()  # Для бинарной классификации
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        for epoch in range(epochs):
            self.model.train()
            optimizer.zero_grad()
            
            # Прямой проход (forward pass)
            outputs = self.model(X_train_tensor)
            loss = criterion(outputs.squeeze(), y_train_tensor)
            
            # Обратный проход (backward pass) и оптимизация
            loss.backward()
            optimizer.step()

            if epoch % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

    def predict(self, data):
        """Предсказание с использованием обученной модели"""
        self.model.eval()  # Переводим модель в режим оценки
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        data_tensor = torch.tensor(data, dtype=torch.float32).to(device)
        
        with torch.no_grad():
            output = self.model(data_tensor)
        
        return output.cpu().numpy()

    def save_model(self, filepath):
        """Сохранение модели"""
        torch.save(self.model.state_dict(), filepath)

    def load_model(self, filepath):
        """Загрузка модели"""
        self.model.load_state_dict(torch.load(filepath))
        self.model.eval()  # Переводим модель в режим оценки
