# Web scraper of the tululu.org

The script will scrape all books from the "Fantasy" section.

### How to install

Python >= 3.6. <br>
Install dependencies:
```
pip install -r requirements.txt
```

### How to use
```
python tululu.py --start_page xxx --end_page yyy
```
If argument `end_page` will be skipped, scraper will check the latest page of the book category and will scrape untill then<br>
<br>

Example of the json-db:
```json
[
  {
      "title": "Book name",
      "author": "Book author",
      "img_src": "images/image_id.jpg",
      "book_path": "books/book_name.txt",
      "comments": ["comment_1", "comment_2"],
      "genres": ["genre_1", "genre_2"]
  }, 

]
```

### Goal of the project

Project created as a part of the Python course [dvmn.org](https://dvmn.org/).