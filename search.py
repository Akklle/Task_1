import re

# Загрузка инвертированного индекса
def load_index(filename='inverted_index.txt'):
    index = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            lemma = parts[0]
            documents = set(parts[1:])
            index[lemma] = documents
    return index

# Токенизация
def tokenize_query(query):
    tokens = re.findall(r'\w+|AND|OR|NOT|\(|\)', query)
    return [t.upper() if t.upper() in {"AND", "OR", "NOT"} else t.lower() for t in tokens]

# Оценка булевого выражения
def evaluate(tokens, index, all_docs):
    def get_set(term):
        return index.get(term, set())

    def parse(tokens):
        stack = []
        ops = []
        precedence = {'OR': 1, 'AND': 2, 'NOT': 3}

        def apply_op():
            op = ops.pop()
            if op == 'NOT':
                a = stack.pop()
                stack.append(all_docs - a)
            else:
                b = stack.pop()
                a = stack.pop()
                result = a & b if op == 'AND' else a | b
                stack.append(result)

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '(':
                ops.append(token)
            elif token == ')':
                while ops and ops[-1] != '(':
                    apply_op()
                ops.pop()
            elif token in precedence:
                while ops and ops[-1] in precedence and precedence[ops[-1]] >= precedence[token]:
                    apply_op()
                ops.append(token)
            else:
                stack.append(get_set(token))
            i += 1

        while ops:
            apply_op()

        return stack[0] if stack else set()

    return parse(tokens)

# Логика поиска
def main():
    index = load_index()
    all_docs = set()
    for docs in index.values():
        all_docs.update(docs)

    print("Введите булев запрос (например: (брайтер AND брат) OR (айвазовский AND август) OR быть):")
    query = input("> ")
    tokens = tokenize_query(query)

    try:
        result = evaluate(tokens, index, all_docs)
        if result:
            print("\nНайдено в следующих документах:")
            for doc in sorted(result):
                print(doc)
        else:
            print("\nПо вашему запросу ничего не найдено.")
    except Exception as e:
        print(f"\nОшибка обработки запроса: {e}")

if __name__ == '__main__':
    main()
