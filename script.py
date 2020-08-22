import requests
import os
import time
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from parse_tululu_category import collect_book_urls, get_last_page_number
import json
import argparse


def get_book_soup(book_url):
    response = requests.get(book_url, allow_redirects=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        return soup


def clean_filename(id, filename):
    return f'{id}-{sanitize_filename(filename)}'


def get_title_and_author(soup):
    title, author = soup.select_one('h1').text.split('::')

    return {
        'title': title.strip(),
        'author': author.strip()
    }


def get_cover_fullpath(soup):
    base = 'http://tululu.org'
    img_name = soup.select_one('div.bookimage img')['src']
    return urljoin(base, img_name)


def get_comments(soup):
    comments = [
        comment.text for comment in soup.select('div.texts span.black')
    ]
    return None if len(comments) == 0 else comments


def get_genres(soup):
    genres = [genre.text for genre in soup.select('span.d_book a')]
    return None if len(genres) == 0 else genres


def download_txt(book_id, filename, skip_txt, folder=None):
    if not skip_txt:
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


def download_image(image_url, skip_images, folder=None):
    if not skip_images:
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
    book_category = 55

    parser = argparse.ArgumentParser(
        description='The parser of tululu.org library')
    parser.add_argument('--start_page', default=1,
                        help='Download starts with this page', type=int)
    parser.add_argument('--end_page',
                        help='Download ends with this page', type=int)
    parser.add_argument('--filename', default='books_db.json',
                        help='Name of json-db file')
    parser.add_argument('--skip_txt', default=False,
                        help='Skip saving the files', type=bool, required=False)
    parser.add_argument('--skip_images', default=False,
                        help='Skip saving the images', type=bool,
                        required=False)
    parser.add_argument('--dest_folder', default='',
                        help='Директория для хранения файлов',
                        type=str, required=False)

    args = parser.parse_args()

    print('Actions summary:')
    print('-'*50)
    print(f'Pages to load from {args.start_page} to {args.end_page}')
    print(f'Filename of the DB is {args.filename}')
    print(f'Is filesaving will be skipped? {args.skip_txt}')
    print(f'Is cover inages will be skipped? {args.skip_images}')

    json_db_file_path = os.path.join(args.dest_folder, args.filename)

    books_collection = []
    book_urls = collect_book_urls(
        args.start_page, args.end_page or get_last_page_number(book_category), book_category)

    for book_url in book_urls:
        time.sleep(3)
        book_soup = get_book_soup(book_url)
        if book_soup:
            comments = get_comments(book_soup)
            genres = get_genres(book_soup)
            title_and_author = get_title_and_author(book_soup)
            book_id = book_url.split('/')[-2].replace('b', '')
            book_path = download_txt(
                book_id, title_and_author['title'], args.skip_txt)

            img_src = get_cover_fullpath(book_soup)
            cover_link = download_image(img_src, args.skip_images)
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
    with open(json_db_file_path, 'w', encoding='utf8') as books_json_db:
        json.dump(books_collection, books_json_db, ensure_ascii=False)
