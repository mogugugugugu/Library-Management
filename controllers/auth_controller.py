
from flask import Blueprint, render_template, redirect, request, session, flash
from repositories.user_repository import UserRepository
from entities.user import User

auth_blueprint = Blueprint("auth", __name__)
user_repo = UserRepository()

@auth_blueprint.route("/")
def login_page():
    # Redirect logged-in users based on their role
    if "username" in session:
        return redirect("/inventory" if session.get("role") == "regular" else "/library_database")
    return render_template("login.html")

@auth_blueprint.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = user_repo.get_user_by_username_password(username, password)
    if user:
        # Only set the session once user validation is successful
        session["username"] = user.username
        session["role"] = user.role
        print(f"DEBUG: Login successful for user '{user.username}' with role '{user.role}'")
        return redirect("/inventory" if user.role == "regular" else "/library_database")
    flash("Invalid username or password. Please try again.")
    print(f"DEBUG: Login failed for username '{username}'")
    return redirect("/")

@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            # Validate and add new user
            user = User(username, password)
            user_repo.add_user(user)
            user = user_repo.get_user_by_username_password(username, password)
            if user:
                # Only set the session once user validation is successful
                session["username"] = user.username
                session["role"] = user.role
                print(f"DEBUG: Login successful for user '{user.username}' with role '{user.role}'")
                return redirect("/inventory" if user.role == "regular" else "/library_database")
            flash("Invalid username or password. Please try again.")
            print(f"DEBUG: Login failed for username '{username}'")
            return redirect("/register")
        except ValueError as ve:
            flash(str(ve))
        except Exception as e:
            flash("An error occurred during registration. Please try again.")
        return redirect("/register")
    return render_template("register.html")


@auth_blueprint.route("/logout")
def logout():
    session.clear()
    print("DEBUG: User logged out successfully.")
    return redirect("/")
