from flask_login import UserMixin

class UserWrapper(UserMixin):
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email 
        self.role = role