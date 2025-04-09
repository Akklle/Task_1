import os
import re
import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

# Подготовка
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('russian'))
MORPH = pymorphy2.MorphAnalyzer()

# Очистка и токенизация
def extract_tokens_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

    text = soup.get_text(separator=' ')
    text = re.sub(r'[^а-яА-ЯёЁ\s]', '', text)
    tokens = text.lower().split()
    tokens = [w for w in tokens if w not in STOPWORDS and len(w) > 2 and not re.search(r'\d', w)]
    return tokens

# Лемматизация
def lemmatize_tokens(tokens):
    return [MORPH.parse(t)[0].normal_form for t in tokens]

inverted_index = {}

for filename in os.listdir('pages'):
    if filename.endswith('.html'):
        filepath = os.path.join('pages', filename)
        tokens = extract_tokens_from_html(filepath)
        lemmas = lemmatize_tokens(tokens)
        unique_lemmas = set(lemmas)
        for lemma in unique_lemmas:
            if lemma not in inverted_index:
                inverted_index[lemma] = set()
            inverted_index[lemma].add(filename)

# Сохранение индекса
with open('inverted_index.txt', 'w', encoding='utf-8') as f:
    for lemma in sorted(inverted_index):
        files = ' '.join(sorted(inverted_index[lemma]))
        f.write(f"{lemma} {files}\n")

print("Инвертированный индекс сохранён в inverted_index.txt")
