import requests
import os
import time
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import logging


def get_last_page_number(id):
    try:
        response = requests.get(f'https://tululu.org/l{id}/',
            allow_redirects=False, verify=False)
        soup = BeautifulSoup(response.text, 'lxml')
        last_page_number = soup.select('a.npage')[-1].text

        return int(last_page_number)
    except requests.exceptions.HTTPError:
        logging.warning(f'Page https://tululu.org/l{id}/ could not be opened.')


def get_genres_collection_soup(id, page):
    try:
        response = requests.get(f'https://tululu.org/l{id}/{page}',
            allow_redirects=False, verify=False)
        soup = BeautifulSoup(response.text, 'lxml')
        return soup
    except requests.exceptions.HTTPError:
        logging.warning(f'Page https://tululu.org/l{id}/{page} could not be opened.')


def get_books_urls(soup):
    base = 'https://tululu.org/'
    books_url = {
        urljoin(base, url['href']) for url in soup.select('table.d_book a[href^="/b"]')
    } 
    return books_url


def collect_book_urls(start_page, end_page, genre_id):
    url_collection = []
    for page_list in range(start_page, end_page):
        soup = get_genres_collection_soup(genre_id, page_list)
        books = get_books_urls(soup)
        url_collection.extend(books)
    return url_collection


if __name__ == "__main__":
    pass
