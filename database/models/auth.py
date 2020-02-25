from werkzeug.security import generate_password_hash, check_password_hash
from database.models.tables import UserTable

users = UserTable()

class UserAuth()
    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password, email):
        return check_password_has(user.get_pw_hash_by_email(email), password)

