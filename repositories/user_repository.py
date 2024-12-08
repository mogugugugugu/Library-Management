
import json
from datetime import datetime

from entities.user import User


class UserRepository:
    def __init__(self, file_path="data/user.json"):
        self.file_path = file_path

    def _read_users(self):
        with open(self.file_path, "r") as file:
            return json.load(file)

    def _write_users(self, users):
        with open(self.file_path, "w") as file:
            json.dump(users, file, indent=4)

    def get_all_users(self):
        return [User(**user) for user in self._read_users()]

    def get_user_by_username_password(self, username, password):
        try:
            users = self._read_users()
            for user in users:
                if all(k in user for k in ["username", "password", "inventory", "role"]):
                    if user["username"] == username and user["password"] == password:
                        print(f"DEBUG: Found user '{username}' with role '{user['role']}'")
                        return User(username=user["username"], password=user["password"], inventory=user["inventory"], role=user["role"])
            print(f"DEBUG: User '{username}' not found or password mismatch.")
        except Exception as e:
            print(f"Error retrieving user: {e}")
        return None

    def add_user(self, user):
        try:
            users = self._read_users()
            if any(u["username"] == user.username for u in users):
                raise ValueError(f"Username '{user.username}' already exists.")
            users.append(user.__dict__)
            self._write_users(users)
            print(f"User {user.username} added successfully.")
        except ValueError as ve:
            print(ve)
            raise
        except Exception as e:
            print(f"Error adding user: {e}")
            raise

    def get_regular_users(self):
        return [User(**user) for user in self._read_users() if user["role"] == "regular"]

    def add_book_to_inventory(self, username, book_id):
        users = self._read_users()
        for user in users:
            if user["username"] == username:
                if book_id not in user["inventory"]:
                    user["inventory"].append(book_id)
                break
        self._write_users(users)

    def remove_book_from_inventory(self, username, book_id):
        users = self._read_users()
        for user in users:
            if user["username"] == username:
                user["inventory"] = [b_id for b_id in user["inventory"] if b_id != book_id]
                break
        self._write_users(users)

    def remove_book_from_all_inventories(self, book_id):
        users = self._read_users()
        for user in users:
            user["inventory"] = [b_id for b_id in user["inventory"] if b_id != book_id]
        self._write_users(users)


