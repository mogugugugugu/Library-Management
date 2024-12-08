
import json
from datetime import datetime

from entities.book import Book
from repositories.user_repository import UserRepository

class LibraryRepository:
    def __init__(self, file_path="data/books.json"):
        self.file_path = file_path
        self.user_repo = UserRepository()

    def _read_books(self):
        with open(self.file_path, "r") as file:
            return json.load(file)

    def _write_books(self, books):
        with open(self.file_path, "w") as file:
            json.dump(books, file, indent=4)

    def get_all_books(self):
        return [Book(**book) for book in self._read_books()]

    def get_all_books_sorted(self):
        books = self._read_books()
        return sorted(books, key=lambda x: x["title"])

    def get_available_books(self):
        return [Book(**book) for book in self._read_books() if book["available"]]

    def get_book_by_id(self, book_id):
        books = self._read_books()
        for book in books:
            if book["id"] == book_id:
                return Book(**book)
        return None

    def add_book(self, book):
        books = self._read_books()
        books.append(book.__dict__)
        self._write_books(books)

    def update_book(self, book_id, updated_data):
        books = self._read_books()
        for book in books:
            if book["id"] == book_id:
                book.update(updated_data)
                break
        self._write_books(books)

    def delete_book(self, book_id):
        books = self._read_books()
        books = [book for book in books if book["id"] != book_id]
        self._write_books(books)
        # Remove book from all user inventories
        self.user_repo.remove_book_from_all_inventories(book_id)

    def get_user_inventory_overdue_status(self, inventory):
        overdue_books = []
        not_overdue_books = []

        for book_id in inventory:
            book = self.get_book_by_id(book_id)  # Directly fetch the book by ID
            if book:
                if book.return_date:
                    return_date = datetime.strptime(book.return_date, "%Y-%m-%d")
                    if return_date < datetime.now():
                        overdue_books.append(book)
                    else:
                        not_overdue_books.append(book)
                else:
                    not_overdue_books.append(book)  # If no return date, consider it not overdue

        return overdue_books, not_overdue_books

