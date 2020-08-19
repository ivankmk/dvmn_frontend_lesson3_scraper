import requests
import os
import time
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

def get_genres_collection_soup(id, page):
    response = requests.get(f'http://tululu.org/l{id}/{page}', allow_redirects=False)
    if response.status_code == 200:
        soup =  BeautifulSoup(response.text, 'lxml')
        return soup


def get_books_url(soup):
    base = 'http://tululu.org'
    all_books_with_one_genre = soup.findAll('table', {'class': 'd_book'})
    books_url = [
        urljoin(base, book.find('a')['href']) for book in all_books_with_one_genre
        ]
    return books_url

def collect_book_urls(pages_to_search, genre_id):
    url_collection = []
    for page_list in range(1, pages_to_search+1):
        soup = get_genres_collection_soup(genre_id, page_list)
        list_of_books = get_books_url(soup)
        url_collection = url_collection.extend(list_of_books)
    return url_collection



if __name__ == "__main__":

    print(collect_book_urls(3, 55))
