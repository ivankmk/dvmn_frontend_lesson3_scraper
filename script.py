import requests
import os
import time
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

def get_book_soup(id):
    response = requests.get(f'http://tululu.org/b{id}/', allow_redirects=False)
    if response.status_code == 200:
        soup =  BeautifulSoup(response.text, 'lxml')
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
    if 'nopic.gif' not in img_name:
        return urljoin(base, img_name)



def download_txt(id, filename, folder=None):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    filename_cleaned = clean_filename(id, filename)
    folder_to_save = folder or 'books'
    file_url = f'http://tululu.org/txt.php?id={id}'
    
    os.makedirs(folder_to_save, exist_ok=True)

    response = requests.get(file_url, allow_redirects=False)

    full_path = os.path.join(folder_to_save, filename_cleaned)
    if response.status_code == 200:
        data = response.text
        with open(f'{full_path}.txt', 'w') as f:
            f.write(data)
        return full_path

if __name__ == "__main__":
    for book_id in range(1, 11):
        time.sleep(3)
        book_soup = get_book_soup(book_id)
        if book_soup:
            title_and_author = get_title_and_author(book_soup)
            if download_txt(book_id, title_and_author['title'], folder=None):
                print(get_cover_fullpath(book_soup) or f'{book_id} does not have cover')