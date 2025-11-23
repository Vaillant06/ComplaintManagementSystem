from flask_login import UserMixin
class UserWrapper(UserMixin):
    def __init__(self, user_id, name, email, is_admin):
        self.id = user_id
        self.name = name
        self.email = email
        self.is_admin = is_admin
