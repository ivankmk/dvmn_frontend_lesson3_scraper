import requests
import os
import time
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def get_book_soup(id):
    response = requests.get(f'http://tululu.org/b{id}/', allow_redirects=False)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'lxml')


def get_name_and_author(soup):
    title, author = soup.find('h1').text.split('::')

    return {
        'title': title.strip(),
        'author': author.strip()
    }


def download_txt(url, filename, folder=None):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    filename_cleaned = sanitize_filename(filename)
    folder_to_save = folder or 'books'
    
    os.makedirs(folder_to_save, exist_ok=True)

    response = requests.get(url, allow_redirects=False)

    full_path = os.path.join(folder_to_save, filename_cleaned)
    if response.status_code == 200:
        data = response.text
        with open(full_path, 'w') as f:
            f.write(data)
        return full_path

if __name__ == "__main__":
    
    url = 'http://tululu.org/txt.php?id=1'

    filepath = download_txt(url, 'Алиби')
    print(filepath)  # Выведется books/Алиби.txt

    filepath = download_txt(url, 'Али/би', folder='books/')
    print(filepath)  # Выведется books/Алиби.txt

    filepath = download_txt(url, 'Али\\би', folder='txt/')
    print(filepath) 

 # Выведется txt/Алиби.txt
    # book_soup = get_book_soup(1)
    # get_name_and_author(book_soup)