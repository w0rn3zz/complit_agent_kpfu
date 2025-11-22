# train_simple.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import torch
from transformers import AutoTokenizer, AutoModel
from collections import Counter

# ---------- 1. Загрузка данных ----------
df = pd.read_csv('new_output_dataset.csv')
df = df.dropna(subset=['Текст заявки', 'Класс'])
texts = df['Текст заявки'].astype(str).tolist()
labels = df['Класс'].tolist()

# Подсчитываем частоты
label_counts = Counter(labels)
print("Классы с 1 примером:", [k for k, v in label_counts.items() if v == 1])

# Оставляем только классы с ≥2 примерами
valid_labels = {k for k, v in label_counts.items() if v >= 2}
mask = [label in valid_labels for label in labels]
texts = [t for t, m in zip(texts, mask) if m]
labels = [l for l, m in zip(labels, mask) if m]

print(f"Оставлено {len(labels)} примеров после фильтрации редких классов.")

# ---------- 2. Эмбеддинги через rubert-tiny2 ----------
print("Загружаем rubert-tiny2...")
tokenizer = AutoTokenizer.from_pretrained("./rubert-tiny2-local")
model = AutoModel.from_pretrained("./rubert-tiny2-local")

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        outputs = model(**inputs)
    # Берём [CLS] токен и нормализуем
    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()
    return cls_embedding[0]

print("Генерируем эмбеддинги...")
embeddings = np.array([get_embedding(text) for text in texts])

# ---------- 3. Обучение классификатора ----------
X_train, X_test, y_train, y_test = train_test_split(
    embeddings, labels, test_size=0.2, random_state=42, stratify=labels
)

print("Обучаем логистическую регрессию...")
clf = LogisticRegression(
    max_iter=1000,
    random_state=42,
    class_weight='balanced',
    C=10.0  # регуляризация
)
clf.fit(X_train, y_train)

# ---------- 4. Оценка ----------
y_pred = clf.predict(X_test)
print("\n📊 Точность:")
print(classification_report(y_test, y_pred, zero_division=0))

# ---------- 5. Сохранение ----------
joblib.dump(clf, 'logistic_classifier_new_dataset.pkl')
joblib.dump(tokenizer, 'tokenizer_new_dataset.pkl')
# Модель BERT уже локально — не нужно сохранять заново

print("\n✅ Модель сохранена: logistic_classifier_new_dataset.pkl")