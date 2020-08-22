import requests
import os
import time
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def get_last_page_number(id):
    response = requests.get(f'http://tululu.org/l{id}/', allow_redirects=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        last_page_number = soup.select('a.npage')[-1].text
        return int(last_page_number)


def get_genres_collection_soup(id, page):
    response = requests.get(
        f'http://tululu.org/l{id}/{page}', allow_redirects=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        return soup


def get_books_url(soup):
    base = 'http://tululu.org'
    books_url = [
        urljoin(base, url['href']) for url in soup.select('table.d_book a[href^="/b"]')
    ]
    books_url = list(set(books_url))
    return books_url


def collect_book_urls(start_page, end_page, genre_id):
    url_collection = []
    for page_list in range(start_page, end_page):
        soup = get_genres_collection_soup(genre_id, page_list)
        list_of_books = get_books_url(soup)
        url_collection.extend(list_of_books)
    return url_collection


if __name__ == "__main__":
    pass
