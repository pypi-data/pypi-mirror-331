def dfs_search(book_list, title):
    """Recursive DFS search for a book in a list of dictionaries."""
    for book in book_list:
        if book["title"] == title:
            return book
    return None

def dfs_search_library(library, title):
    """Recursive DFS search through the entire library."""
    for group in library["groups"]:
        result = dfs_search(library["groups"][group]["books"], title)
        if result:
            return result
    return None
