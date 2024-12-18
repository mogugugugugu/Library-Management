
from flask import Blueprint, render_template, request, redirect, session, flash

import app
from repositories.library_repository import LibraryRepository
from repositories.user_repository import UserRepository
from entities.book import Book
from datetime import datetime, timedelta  # Ensure datetime is imported
import logging

# Configure logger for this module
logging.basicConfig(
    level=logging.INFO,  # Set logging level
    format="%(asctime)s [%(levelname)s] %(message)s"  # Set log message format
)
logger = logging.getLogger(__name__)

library_blueprint = Blueprint("library", __name__)
library_repo = LibraryRepository()
user_repo = UserRepository()

@library_blueprint.route("/inventory")
def user_inventory():
    if "username" not in session or session.get("role") != "regular":
        flash("You must be logged in to view your inventory.")
        return redirect("/")
    print(f"DEBUG: User '{session['username']}' accessing inventory.")
    # Directly use session data for the user
    username = session["username"]
    user = next((u for u in user_repo.get_all_users() if u.username == username), None)
    if not user:
        flash("Session expired or user data is invalid. Please log in again.")
        session.clear()
        return redirect("/")
    inventory_books = [library_repo.get_book_by_id(book_id) for book_id in user.inventory]
    return render_template("inventory.html", inventory=inventory_books)

@library_blueprint.route("/library")
def library():
    if "username" not in session:
        flash("You must be logged in to access the library.")
        return redirect("/")
    books = library_repo.get_available_books()
    return render_template("library.html", books=books)

@library_blueprint.route("/library_database")
def library_database():
    if session.get("role") != "admin":
        flash("You must be an admin to access this page.")
        return redirect("/")
    books = library_repo.get_all_books_sorted()
    return render_template("library_database.html", books=books)

@library_blueprint.route("/book/<book_id>")
def book_detail(book_id):
    if "username" not in session:
        flash("You must be logged in to view book details.")
        return redirect("/")
    book = library_repo.get_book_by_id(book_id)
    return render_template("book_detail.html", book=book, role=session.get("role"))

@library_blueprint.route("/add_book", methods=["GET", "POST"])
def add_book():
    if session.get("role") != "admin":
        flash("Only admins can add books.")
        return redirect("/")
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        description = request.form["description"]
        photo_url = request.form["photo_url"]
        book = Book(
            id=str(len(library_repo.get_all_books()) + 1),
            title=title,
            author=author,
            description=description,
            available=True,
            return_date=None,
            photo_url=photo_url
        )
        library_repo.add_book(book)
        flash("Book added successfully!")
        return redirect("/library_database")
    return render_template("add_book.html")

@library_blueprint.route("/add_to_inventory/<book_id>", methods=["POST"])
def add_to_inventory(book_id):
    if session.get("role") != "regular":
        flash("Only regular users can add books to inventory.")
        return redirect("/")
    user = next((u for u in user_repo.get_all_users() if u.username == session["username"]), None)
    if not user:
        flash("Session expired or user data is invalid. Please log in again.")
        session.clear()
        return redirect("/")
    book = library_repo.get_book_by_id(book_id)
    if book and book.available:
        return_date = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d")
        user_repo.add_book_to_inventory(user.username, book_id)
        library_repo.update_book(book_id, {"available": False, "return_date": return_date})
        flash(f"Book added to your inventory. Return date: {return_date}")
    else:
        flash("Book is not available.")
    return redirect("/library")

@library_blueprint.route("/remove_from_inventory/<book_id>", methods=["POST"])
def remove_from_inventory(book_id):
    if session.get("role") != "regular":
        flash("Only regular users can remove books from inventory.")
        return redirect("/")
    user = next((u for u in user_repo.get_all_users() if u.username == session["username"]), None)
    if not user:
        flash("Session expired or user data is invalid. Please log in again.")
        session.clear()
        return redirect("/")
    book = library_repo.get_book_by_id(book_id)
    if book and book_id in user.inventory:
        user_repo.remove_book_from_inventory(user.username, book_id)
        library_repo.update_book(book_id, {"available": True, "return_date": None})
        flash("Book removed from your inventory.")
    else:
        flash("Book not found in your inventory.")
    return redirect("/inventory")

@library_blueprint.route("/delete_book/<book_id>", methods=["POST"])
def delete_book(book_id):
    if session.get("role") != "admin":
        flash("Only admins can delete books.")
        return redirect("/")
    library_repo.delete_book(book_id)
    flash("Book deleted successfully!")
    return redirect("/library_database")

@library_blueprint.route("/update_book/<book_id>", methods=["GET", "POST"])
def update_book(book_id):
    if session.get("role") != "admin":
        flash("Only admins can update books.")
        return redirect("/")
    book = library_repo.get_book_by_id(book_id)
    if request.method == "POST":
        updated_data = {
            "title": request.form["title"],
            "author": request.form["author"],
            "description": request.form["description"],
            "photo_url": request.form["photo_url"],
        }
        library_repo.update_book(book_id, updated_data)
        flash("Book updated successfully!")
        return redirect("/library_database")
    return render_template("update_book.html", book=book)


@library_blueprint.route('/admin_dashboard')
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/")  # Redirect non-admin users

    try:
        # Fetch all books
        books = library_repo.get_all_books()

        # Calculate availability
        available = sum(1 for book in books if book.available)
        unavailable = len(books) - available

        # Prepare overdue books by month
        from collections import Counter
        overdue_books_by_month = Counter()

        for book in books:
            if book.return_date:
                return_date = datetime.strptime(book.return_date, "%Y-%m-%d")
                if return_date < datetime.now():
                    month = return_date.strftime("%B %Y")  # Month-Year format
                    overdue_books_by_month[month] += 1

        # Sort data by month
        sorted_months = sorted(overdue_books_by_month.keys(), key=lambda m: datetime.strptime(m, "%B %Y"))
        bar_chart_data = {
            "months": sorted_months,
            "overdue_counts": [overdue_books_by_month[month] for month in sorted_months],
        }

        pie_chart_data = {"available": available, "unavailable": unavailable}

        return render_template(
            "admin_dashboard.html",
            pie_chart_data=pie_chart_data,
            bar_chart_data=bar_chart_data,
        )
    except Exception as e:
        # Log the error
        logger.error(f"Error in admin_dashboard: {e}")
        return render_template(
            "admin_dashboard.html",
            pie_chart_data={"available": 0, "unavailable": 0},
            bar_chart_data={"months": [], "overdue_counts": []},
            error_message="An error occurred while loading the dashboard. Please try again later.",
        )


@library_blueprint.route('/user_dashboard')
def user_dashboard():
    if session.get("role") != "regular":
        return redirect("/")  # Redirect non-regular users

    try:
        username = session["username"]
        user = next((u for u in user_repo.get_all_users() if u.username == username), None)

        if not user:
            raise ValueError("User not found")

        inventory = user.inventory  # List of book IDs in the user's inventory

        # Get overdue and not overdue books
        overdue_books, not_overdue_books = library_repo.get_user_inventory_overdue_status(inventory)

        # Prepare data for the pie chart
        overdue_count = len(overdue_books)
        not_overdue_count = len(not_overdue_books)
        pie_chart_data = {"overdue": overdue_count, "not_overdue": not_overdue_count}

        # Get book recommendation
        recommended_book = library_repo.recommend_book(inventory)

        return render_template(
            "user_dashboard.html",
            pie_chart_data=pie_chart_data,
            recommended_book=recommended_book,
        )
    except Exception as e:
        logging.error(f"Error in user_dashboard: {e}")
        return render_template(
            "user_dashboard.html",
            pie_chart_data={"overdue": 0, "not_overdue": 0},
            recommended_book=None,
            error_message="An error occurred while loading the dashboard. Please try again later.",
        )
