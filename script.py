import requests
import os
import time
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from parse_tululu_category import collect_book_urls
import json


def get_book_soup(book_url):
    response = requests.get(book_url, allow_redirects=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        return soup


def clean_filename(id, filename):
    return f'{id}-{sanitize_filename(filename)}'


def get_title_and_author(soup):
    title, author = soup.find('h1').text.split('::')

    return {
        'title': title.strip(),
        'author': author.strip()
    }


def get_cover_fullpath(soup):
    base = 'http://tululu.org'
    img_name = soup.find('div', {'class': 'bookimage'}).find('img')['src']

    return urljoin(base, img_name)


def get_comments(soup):
    all_comments = soup.findAll('div', {'class': 'texts'})
    comments = [
        comment.find('span', {'class': 'black'}).text for comment in all_comments
    ]

    return None if len(comments) == 0 else comments


def get_genres(soup):
    genres_html = soup.find('span', {'class': 'd_book'})
    genres = [genre.text for genre in genres_html.findAll('a')]
    return None if len(genres) == 0 else genres


def download_txt(book_id, filename, folder=None):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    filename_cleaned = clean_filename(book_id, filename)
    folder_to_save = folder or 'books'
    file_url = f'http://tululu.org/txt.php?id={book_id}'

    os.makedirs(folder_to_save, exist_ok=True)
    response = requests.get(file_url, allow_redirects=False)
    full_path = os.path.join(folder_to_save, filename_cleaned)

    if response.status_code == 200:
        data = response.text
        full_path_with_ext = f'{full_path}.txt'
        with open(full_path_with_ext, 'w') as f:
            f.write(data)
        return full_path_with_ext


def download_image(image_url, folder=None):
    folder_to_save = folder or 'images'
    os.makedirs(folder_to_save, exist_ok=True)
    response = requests.get(image_url, allow_redirects=False)
    full_path = os.path.join(folder_to_save, str(image_url.split('/')[-1]))

    if response.status_code == 200:
        data = response.content
        with open(full_path, 'wb') as f:
            f.write(data)
        return full_path


if __name__ == "__main__":
    books_collection = []
    book_urls = collect_book_urls(4, 55)
    for book_url in book_urls:
        time.sleep(3)
        book_soup = get_book_soup(book_url)
        if book_soup:
            comments = get_comments(book_soup)
            genres = get_genres(book_soup)
            title_and_author = get_title_and_author(book_soup)
            book_id = book_url.split('/')[-2].replace('b', '')
            book_path = download_txt(
                book_id, title_and_author['title'], folder=None)
            if book_path:
                img_src = get_cover_fullpath(book_soup)
                if img_src:
                    cover_link = download_image(img_src, folder=None)
                    print('This book was saved: ', title_and_author['title'])
                    books_collection.append(
                        {
                            'title': title_and_author['title'],
                            'author': title_and_author['author'],
                            'img_src': cover_link,
                            'book_path': book_path,
                            'comments': comments,
                            'genres': genres
                        }
                    )
    with open('books_db.json', 'w', encoding='utf8') as books_json_db:
        json.dump(books_collection, books_json_db, ensure_ascii=False)
