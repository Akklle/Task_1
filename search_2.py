import os
import math
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pymorphy2

NUM_DOCS = 150
TFIDF_LEMMAS_DIR = "tfidf_lemmas"
INDEX_FILE = "index.txt"

# Инициализация лемматизатора
morph = pymorphy2.MorphAnalyzer()

# Загрузка TF-IDF векторов документов
doc_vectors = []
vocab = set()
doc_terms = []

for i in range(1, NUM_DOCS + 1):
    path = f"{TFIDF_LEMMAS_DIR}/page_{i}.txt"
    vector = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            lemma, idf, tfidf = line.strip().split()
            tfidf = float(tfidf)
            vector[lemma] = tfidf
            vocab.add(lemma)
    doc_vectors.append(vector)
    doc_terms.append(set(vector.keys()))

# Создание словаря индексов для лемм
vocab = sorted(vocab)
vocab_index = {term: i for i, term in enumerate(vocab)}

# Преобразование документов
def vectorize(doc_dict):
    vec = np.zeros(len(vocab))
    for term, val in doc_dict.items():
        idx = vocab_index.get(term)
        if idx is not None:
            vec[idx] = val
    return vec

doc_matrix = np.array([vectorize(doc) for doc in doc_vectors])

# Лемматизация запроса
def lemmatize(text):
    return [morph.parse(word)[0].normal_form for word in text.lower().split() if word.isalpha()]

# Поиск
def search(query, top_n=10):
    lemmas = lemmatize(query)
    count = Counter(lemmas)
    total_terms = sum(count.values())

    # Расчёт TF
    tf = {term: count[term] / total_terms for term in count}

    # Расчёт IDF
    tfidf = {
        term: tf[term] * math.log(NUM_DOCS / sum(1 for d in doc_terms if term in d))
        for term in tf
    }

    query_vec = vectorize(tfidf).reshape(1, -1)
    sims = cosine_similarity(query_vec, doc_matrix)[0]
    top_indices = sims.argsort()[::-1][:top_n]

    # Загрузка ссылок
    with open(INDEX_FILE, encoding="utf-8") as f:
        links = [line.strip().split(" ", 1)[1] for line in f.readlines()]

    print("\nРезультаты поиска:")
    for rank, idx in enumerate(top_indices, 1):
        print(f"{rank}. Документ {idx+1} — {links[idx]} (сходство: {sims[idx]:.4f})")

# Запуск
if __name__ == "__main__":
    query = input("Введите поисковый запрос: ")
    search(query)
