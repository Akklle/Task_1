import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os

# Функция для загрузки страницы по URL
def download_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Проверка успешного ответа
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None


def should_ignore_url(url, start_domain):
    parsed_url = urlparse(url)

    if parsed_url.fragment:  # Игнорируем ссылки с якорем (#)
        return True

    if parsed_url.netloc != start_domain:  # Игнорируем ссылки с другого домена
        return True

    if ('/category/' in parsed_url.path or '.png' in parsed_url.path or
            '.php' in parsed_url.path or '.jpg' in parsed_url.path or '.css' in parsed_url.path
            or '.js' in parsed_url.path or 'feed' in parsed_url.path):
        return True

    return False


def save_page_to_file(page_number, url, content):
    if not os.path.exists('pages'):
        os.makedirs('pages')

    with open(f'pages/page_{page_number}.html', 'w', encoding='utf-8') as file:
        file.write(content)

    with open('index.txt', 'a', encoding='utf-8') as index_file:
        index_file.write(f"{page_number} {url}\n")


# Основная функция краулера
def crawl(start_url, max_pages=150):
    crawled_pages = 0
    visited_urls = set()
    current_url = start_url
    start_domain = urlparse(start_url).netloc

    if os.path.exists('index.txt'):
        os.remove('index.txt')

    page_number = 1  # Начальный номер страницы

    while crawled_pages < max_pages:
        if current_url not in visited_urls: # Если URL еще не посещен
            visited_urls.add(current_url)

            content = download_page(current_url)
            if content:
                crawled_pages += 1
                print(f"{crawled_pages} {current_url}")
                save_page_to_file(crawled_pages, current_url, content)

                soup = BeautifulSoup(content, 'html.parser')
                links = soup.find_all('a', href=True) # Ищем все ссылки на странице

                next_url = None
                for link in links:
                    full_url = urljoin(current_url, link['href'])
                    if not should_ignore_url(full_url, start_domain) and full_url not in visited_urls:
                        next_url = full_url
                        break

                if next_url: # Если нашли подходящую ссылку
                    current_url = next_url
                else:
                    # Если не нашли следующую ссылку, переходим на следующую страницу с помощью URL
                    page_number += 1
                    next_page_url = f"https://{start_domain}/page/{page_number}/"
                    current_url = next_page_url




# Стартовый URL для краулера
start_url = 'https://kartinysistoriey.ru/devyatyj-val-otchayannaya-borba-so-stihiej-glazami-hudozhnika/'
crawl(start_url, max_pages=150)
