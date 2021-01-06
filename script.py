import requests
import os
import time
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from parse_tululu_category import collect_book_urls, get_last_page_number
import json
import argparse
import logging
import sys
import urllib3


def check_response(response):
    response.raise_for_status()
    if response.history:
        raise requests.HTTPError('Redirect')
    return response

def get_book_soup(book_url):
    response = check_response(requests.get(book_url, allow_redirects=False, verify=False))
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def get_title_and_author(soup):
    title, author = soup.select_one('h1').text.split('::')

    return {
        'title': title.strip(),
        'author': author.strip()
    }


def get_cover_fullpath(soup):
    base = 'https://tululu.org/shots'
    img_name = soup.select_one('div.bookimage img')['src']

    return urljoin(base, img_name)


def get_comments(soup):
    comments = [
        comment.text for comment in soup.select('div.texts span.black')
    ]
    return None if not comments else comments


def get_genres(soup):
    genres = [genre.text for genre in soup.select('span.d_book a')]
    return None if not genres else genres


def download_txt(book_id, filename, folder=None):
    filename_cleaned = f'{book_id}-{sanitize_filename(filename)}'
    folder_to_save = folder or 'books'
    file_url = f'https://tululu.org/txt.php?id={book_id}'

    os.makedirs(folder_to_save, exist_ok=True)
    response = check_response(requests.get(file_url, allow_redirects=False, verify=False))
    full_path = os.path.join(folder_to_save, filename_cleaned)

    if not response.status_code == 200:
        return
    data = response.text
    full_path_with_ext = f'{full_path}.txt'
    with open(full_path_with_ext, 'w') as f:
        f.write(data)
    return full_path_with_ext


def download_image(image_url, folder=None):
    folder_to_save = folder or 'images'
    os.makedirs(folder_to_save, exist_ok=True)
    response = check_response(requests.get(image_url, allow_redirects=False, verify=False))
    full_path = os.path.join(folder_to_save, str(image_url.split('/')[-1]))

    if not response.status_code == 200:
        return
    data = response.content
    with open(full_path, 'wb') as f:
        f.write(data)
    return full_path

def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    book_category = 55
    last_page_number = get_last_page_number(book_category)

    parser = argparse.ArgumentParser(
        description='The parser of tululu.org library')
    parser.add_argument('--start_page', default=1,
                        help='Download starts with this page', type=int)
    parser.add_argument('--end_page',
                        help='Download ends with this page', type=int)
    parser.add_argument('--filename', default='books_db.json',
                        help='Name of json-db file')
    parser.add_argument('--skip_txt', action='store_true',
                        help='Skip saving the files', required=False)
    parser.add_argument('--skip_images', action='store_true',
                        help='Skip saving the images',
                        required=False)
    parser.add_argument('--dest_folder', default='',
                        help='Folder for book saving',
                        type=str, required=False)

    args = parser.parse_args()

    parse_up_to = args.end_page or args.start_page+1 or last_page_number 

    print('Actions summary:')
    print('-'*50)
    print(f'Pages to load from {args.start_page} to {parse_up_to}')
    print(f'Filename of the DB is {args.filename}')
    print(f'Is filesaving will be skipped? {args.skip_txt}')
    print(f'Is cover inages will be skipped? {args.skip_images}')

    json_db_file_path = os.path.join(args.dest_folder, args.filename)
    

    books_collection = []

    try:
        book_urls = collect_book_urls(
            args.start_page, 
            parse_up_to, 
            book_category)

    except (requests.HTTPError, requests.ConnectionError):
        logging.critical(f'HTTPError or ConnectionError')
        sys.exit()

    for book_url in book_urls:
        time.sleep(3)
        try:
            book_soup = get_book_soup(book_url)
        except requests.exceptions.HTTPError:
            logging.warning(f'Page {book_url} could not be opened.')
            continue
        if book_soup:
            try:
                comments = get_comments(book_soup)
                genres = get_genres(book_soup)
                title_and_author = get_title_and_author(book_soup)
                book_id = book_url.split('/')[-2].replace('b', '')
                book_path = None if args.skip_txt else download_txt(book_id, title_and_author['title'])

                img_src = get_cover_fullpath(book_soup)
                cover_link = None if args.skip_images else download_image(img_src)
                logging.info('This book was saved: ', title_and_author['title'])
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
            except (requests.HTTPError, requests.ConnectionError):
                logging.critical(f'HTTPError or ConnectionError')
                sys.exit()

    with open(json_db_file_path, 'w', encoding='utf8') as books_json_db:
        json.dump(books_collection, books_json_db, ensure_ascii=False)

if __name__ == "__main__":
    main()

