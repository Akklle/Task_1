import os
import math
from collections import Counter, defaultdict

NUM_DOCS = 150

TOKENS_DIR = "tokens"
LEMMAS_DIR = "lemmas"
TFIDF_TOKENS_DIR = "tfidf_tokens"
TFIDF_LEMMAS_DIR = "tfidf_lemmas"

os.makedirs(TFIDF_TOKENS_DIR, exist_ok=True)
os.makedirs(TFIDF_LEMMAS_DIR, exist_ok=True)

all_tokens = []
all_lemmas = []

# Чтение
for i in range(1, NUM_DOCS + 1):
    with open(f"{TOKENS_DIR}/page_{i}_tokens.txt", encoding="utf-8") as f:
        tokens = f.read().split()
        all_tokens.append(tokens)

    with open(f"{LEMMAS_DIR}/page_{i}_lemmas.txt", encoding="utf-8") as f:
        lemmas = f.read().split()
        all_lemmas.append(lemmas)

# Подсчёт DF
def compute_df(documents):
    df = defaultdict(int)
    for doc in documents:
        unique_terms = set(doc)
        for term in unique_terms:
            df[term] += 1
    return df

token_df = compute_df(all_tokens)
lemma_df = compute_df(all_lemmas)

# Подсчёт IDF
def compute_idf(df_dict):
    return {term: math.log(NUM_DOCS / df) for term, df in df_dict.items()}

token_idf = compute_idf(token_df)
lemma_idf = compute_idf(lemma_df)

# Подсчёт TF-IDF и сохранение
def save_tfidf(documents, idf_dict, out_folder):
    for idx, doc in enumerate(documents, 1):
        tfidf_lines = []
        count = Counter(doc)
        total_terms = len(doc)
        for term, freq in count.items():
            tf = freq / total_terms
            idf = idf_dict.get(term, 0)
            tfidf = tf * idf
            tfidf_lines.append(f"{term} {idf:.6f} {tfidf:.6f}")

        output_path = f"{out_folder}/page_{idx}.txt"
        with open(output_path, "w", encoding="utf-8") as out_file:
            out_file.write("\n".join(tfidf_lines))

# Сохранение токенов и лемм
save_tfidf(all_tokens, token_idf, TFIDF_TOKENS_DIR)
save_tfidf(all_lemmas, lemma_idf, TFIDF_LEMMAS_DIR)
