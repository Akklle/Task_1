import os
import re
import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

# Загрузка необходимых ресурсов
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('russian'))
MORPH = pymorphy2.MorphAnalyzer()

TOKENS_DIR = "tokens"
LEMMAS_DIR = "lemmas"
PAGES_DIR = "pages"

os.makedirs(TOKENS_DIR, exist_ok=True)
os.makedirs(LEMMAS_DIR, exist_ok=True)

# Функция для извлечения и очистки текста
def extract_tokens_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

    text = soup.get_text(separator=' ')

    text = re.sub(r'[^а-яА-ЯёЁ\s]', ' ', text)

    tokens = text.lower().split()

    # Фильтрация токенов
    tokens = [word for word in tokens if word not in STOPWORDS and len(word) > 2]

    return set(tokens)


# Функция для лемматизации токенов
def lemmatize_tokens(tokens):
    lemmas = {}
    for token in tokens:
        lemma = MORPH.parse(token)[0].normal_form
        if lemma not in lemmas:
            lemmas[lemma] = []
        lemmas[lemma].append(token)
    return lemmas


# Обработка всех страниц
for filename in os.listdir(PAGES_DIR):
    if not filename.endswith('.html'):
        continue

    file_path = os.path.join(PAGES_DIR, filename)

    # Токенизация
    tokens = extract_tokens_from_html(file_path)

    # Лемматизация
    lemmas = lemmatize_tokens(tokens)

    base_name = filename.replace('.html', '')
    tokens_file = os.path.join(TOKENS_DIR, f"{base_name}_tokens.txt")
    lemmas_file = os.path.join(LEMMAS_DIR, f"{base_name}_lemmas.txt")

    with open(tokens_file, "w", encoding="utf-8") as f:
        for token in sorted(tokens):
            f.write(token + '\n')

    with open(lemmas_file, "w", encoding="utf-8") as f:
        for lemma, words in sorted(lemmas.items()):
            f.write(lemma + ' ' + ' '.join(sorted(set(words))) + '\n')

    print(f"Обработан файл: {filename}")

print("Всё.")
