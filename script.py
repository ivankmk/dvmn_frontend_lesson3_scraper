import requests
import os
import time
from bs4 import BeautifulSoup


def get_book_name(id):
    response = requests.get(f'http://tululu.org/b{id}/', allow_redirects=False)
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('h1').text.split('::')[0].strip()
    author = soup.find('h1').text.split('::')[1].strip()
    print('Заголовок: ', title)
    print('Автор: ', author)


if __name__ == "__main__":
    get_book_name(1)