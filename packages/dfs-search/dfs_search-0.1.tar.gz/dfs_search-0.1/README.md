# dfs_search

A simple DFS-based search library for locating books in a structured library format.

## Installation

To install the `dfs_search` library, you can use pip:

```bash
pip install dfs_search
```

## Usage

### Searching for a Book

You can use the `dfs_search` function to search for a book in a list of dictionaries:

```python
from dfs_search import dfs_search

book_list = [
    {"title": "Book A", "author": "Author A"},
    {"title": "Book B", "author": "Author B"},
]

result = dfs_search(book_list, "Book A")
print(result)  # Output: {'title': 'Book A', 'author': 'Author A'}
```

### Searching Through a Library

To search through an entire library structure, use the `dfs_search_library` function:

```python
from dfs_search import dfs_search_library

library = {
    "groups": {
        "group1": {
            "books": [
                {"title": "Book A", "author": "Author A"},
                {"title": "Book B", "author": "Author B"},
            ]
        }
    }
}

result = dfs_search_library(library, "Book B")
print(result)  # Output: {'title': 'Book B', 'author': 'Author B'}
```

## Author

Your Name  
your_email@example.com

## License

This project is licensed under the MIT License.
