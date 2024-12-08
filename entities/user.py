
class User:
    def __init__(self, username, password, inventory=None, role="regular"):
        self.username = username
        self.password = password
        self.inventory = inventory if inventory else []
        self.role = role
