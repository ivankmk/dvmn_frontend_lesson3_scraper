import requests
import os
import time


def save_books(limit):
    url_template = 'http://tululu.org/txt.php?id='
    os.makedirs('books', exist_ok=True)

    for id in range(1, limit):
        time.sleep(3)
        response = requests.get(f'{url_template}{id}', allow_redirects=False)
        if response.status_code == 200:
            data = response.text

            with open(f'books/book_id_{id}.txt', 'w') as f:
                f.write(data)


if __name__ == "__main__":
    save_books(11)
